#pragma once
#include <iostream>
#include <fstream>
#include <random>
#include <vector>
#include <cmath>
#include <sstream>
#include <algorithm>
#include <unordered_map>
#include "customExceptions.h"
#include "timeHandler.h"
#include "datatypes.h"
#include "cxxopts.hpp"
#include "operators.h"
#include "locationTypesFormat.h"

template<typename SimulationType>
class NoMovement {
public:
    // add program parameters if we need any, this function got called already
    // from Simulation
    static void addProgramParameters(cxxopts::Options& options) {}
    void initializeArgs(const cxxopts::ParseResult& result) {}
    void init(const parser::LocationTypes& data, unsigned cemeteryID) {}

    void planLocations(Timehandler simTime, unsigned timeStep) {}
    void movement(Timehandler simTime, unsigned timeStep) {}
};

template<typename SimulationType>
class DummyMovement {
protected:
    thrust::device_vector<unsigned> stepsUntilMove;

public:
    // add program parameters if we need any, this function got called already
    // from Simulation
    static void addProgramParameters(cxxopts::Options& options) {}
    void initializeArgs(const cxxopts::ParseResult& result) {}
    void init(const parser::LocationTypes& data, unsigned cemeteryID) {}

    void planLocations(Timehandler simTime, unsigned timeStep) {
        auto realThis = static_cast<SimulationType*>(this);
        thrust::device_vector<unsigned>& agentLocations = realThis->agents->location;
        unsigned numberOfAgents = agentLocations.size();

        if (stepsUntilMove.size() == 0) stepsUntilMove.resize(numberOfAgents);
        thrust::fill(stepsUntilMove.begin(), stepsUntilMove.end(), 0u);
    }

    void movement(Timehandler simTime, unsigned timeStep) {
        PROFILE_FUNCTION();
        auto realThis = static_cast<SimulationType*>(this);
        thrust::device_vector<unsigned>& locationAgentList = realThis->locs->locationAgentList;
        thrust::device_vector<unsigned>& locationListOffsets = realThis->locs->locationListOffsets;
        thrust::device_vector<unsigned>& locationIdsOfAgents = realThis->locs->locationIdsOfAgents;
        thrust::device_vector<unsigned>& agentLocations = realThis->agents->location;
        unsigned numberOfAgents = agentLocations.size();
        unsigned numberOfLocations = locationListOffsets.size() - 1;

        thrust::for_each(thrust::make_zip_iterator(thrust::make_tuple(agentLocations.begin(), stepsUntilMove.begin())),
            thrust::make_zip_iterator(thrust::make_tuple(agentLocations.end(), stepsUntilMove.end())),
            [numberOfLocations] HD(thrust::tuple<unsigned&, unsigned&> tuple) {
                auto& location = thrust::get<0>(tuple);
                auto& stepsUntilMove = thrust::get<1>(tuple);
                if (stepsUntilMove == 0) {
                    location = RandomGenerator::randomUnsigned(numberOfLocations);
                    stepsUntilMove = RandomGenerator::randomUnsigned(144 / 4);// Move 4 times per day on average
                }
                stepsUntilMove--;
            });
        Util::updatePerLocationAgentLists(agentLocations, locationIdsOfAgents, locationAgentList, locationListOffsets);
    }
};

namespace RealMovementOps {
    constexpr unsigned noWorkNoRequest = std::numeric_limits<unsigned>::max();
    constexpr unsigned noWorkNeedsSelection = std::numeric_limits<unsigned>::max() - 1;

    [[nodiscard]] inline HD unsigned findActualLocationForType(unsigned agent,
        unsigned locType,
        unsigned long* locationOffsetPtr,
        unsigned* possibleLocationsPtr,
        unsigned* possibleTypesPtr,
        unsigned homeType,
        unsigned schoolType,
        unsigned workType,
        int retry,
        bool* locationStatesPtr) {
        if (locType == homeType || locType == schoolType || locType == workType) {
            for (unsigned i = locationOffsetPtr[agent]; i < locationOffsetPtr[agent + 1]; i++) {
                if (locType == possibleTypesPtr[i]) return possibleLocationsPtr[i];
            }
            return std::numeric_limits<unsigned>::max();
        }
        // count number of possible locations
        unsigned counter = 0;
        unsigned pos = 0;
        for (unsigned i = locationOffsetPtr[agent]; i < locationOffsetPtr[agent + 1]; i++) {
            if (locType == possibleTypesPtr[i]) {
                if (counter == 0) pos = i;
                counter++;
            }
        }
        if (counter == 1)
            return possibleLocationsPtr[pos];
        else if (counter > 1) {
            // Pick one at random
            unsigned counter2 = counter;
            unsigned randIdx = counter2;
            while (true) {
                while (randIdx == counter2) randIdx = RandomGenerator::randomUnsigned(counter);
                counter2 = 0;
                for (unsigned i = pos; i < locationOffsetPtr[agent + 1]; i++) {
                    if (locType == possibleTypesPtr[i]) {
                        if (counter2 == randIdx) {
                            if (retry && locationStatesPtr[possibleLocationsPtr[i]] == false) {
                                retry = 0;
                                break;
                            } else
                                return possibleLocationsPtr[i];
                        }
                        counter2++;
                    }
                }
            }
        }
        return std::numeric_limits<unsigned>::max();

        // printf("locType %d not found for agent %d - locationOffsets:
        // %d-%d\n", locType, agent, locationOffsetPtr[agent],
        // locationOffsetPtr[agent+1]);
    }

    template<typename PPState, typename AgentMeta, typename LocationType>
    struct MovementArguments {
        MovementArguments() : simTime(0u) {}
        unsigned* stepsUntilMovePtr;
        PPState* agentStatesPtr;
        AgentMeta* agentMetaDataPtr;
        unsigned* agentTypesPtr;
        bool* diagnosedPtr;
        bool* quarantinedPtr;
        AgentStats* agentStatsPtr;
        unsigned* eventOffsetPtr;
        AgentTypeList::Event* eventsPtr;
        unsigned* agentLocationsPtr;
        unsigned long* locationOffsetPtr;
        unsigned* possibleLocationsPtr;
        unsigned* possibleTypesPtr;
        bool* locationStatesPtr;
        bool* stayedHomePtr;
        unsigned* closedUntilPtr;
        unsigned* locationCapacitiesPtr;
        unsigned* locationQuarantineUntilPtr;
        unsigned quarantinePolicy;
        unsigned quarantineLength;
        Days day;
        unsigned hospitalType;
        unsigned homeType;
        unsigned publicPlaceType;
        unsigned doctorType;
        TimeDay simTime;
        unsigned timeStep;
        unsigned timestamp;
        unsigned tracked;
        unsigned cemeteryLoc;
        unsigned schoolType;
        unsigned classroomType;
        unsigned workType;
        LocationType* locationTypePtr;
        uint8_t* noWorkAgentPtr;
        uint8_t* essentialLocPtr;
        unsigned curfewBegin;
        unsigned curfewEnd;
        bool enableCurfew;
        unsigned schoolAgeRestriction;
        bool quarantineImmuneActive;
        bool lockdownNonvaccActive;
        // High-velocity individuals (HVI): persistent per-agent activity multiplier on discretionary visits
        const float* hviMultPtr = nullptr;
        const uint8_t* hviClassPtr = nullptr;
        const uint8_t* hviRotatePtr = nullptr;
        uint8_t* repeatLeftPtr = nullptr;
        uint8_t* repeatTypePtr = nullptr;
        unsigned* repeatStepsPtr = nullptr;
        unsigned hviStatesMask = 3u;
        bool hviInfectiousOnly = false;
        unsigned hviVisitsFactor = 1;
        uint8_t* rolePtr = nullptr;  // activity role (event type) of the current stay, for the mobility log
        bool hviLeverDuration = false;  // false: the multiplier changes discretionary chances against home; true: it scales durations
        // Round 8: venue-type tilt of the class, minority-dominated scene, isolation breaking
        float hviTilt = 0.0f;               // share of the class's low-L discretionary visits moved to the high-L types at the same duration
        unsigned hviHighMask = 0u;          // bit t set: location type t is a high-L type
        float hviOthersHighScale = 1.0f;    // chances of the high-L types of agents outside the class are multiplied by this, the difference goes to home
        bool hviIsolationBreak = false;     // class members keep their W schedule in the well-being states N and M
    };

    template<typename PPState, typename AgentMeta, typename LocationType>
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        void
        quarantineAgent(unsigned i, MovementArguments<PPState, AgentMeta, LocationType>& a, unsigned until, bool quarantineImmuneActive) {
        //No quarantining
        if (a.quarantinePolicy == 0) return;
        //No quarantine: If "immune" due to previous diagnosis, and we are not quarantining immune
        if (a.agentStatsPtr[i].diagnosedTimestamp > 0 && a.agentStatesPtr[i].isInfected() == false && quarantineImmuneActive == false) return;
        //No quarantine: If "immune" due to vaccination, not currently diagnosed, and we are not quarantining immune
        if (!a.diagnosedPtr[i] && a.agentStatsPtr[i].immunizationTimestamp > 0 && quarantineImmuneActive == false) return;
        a.quarantinedPtr[i] = true;
        a.agentStatsPtr[i].quarantinedTimestamp = a.timestamp;
        unsigned previousQuarantineUntil = a.agentStatsPtr[i].quarantinedUntilTimestamp;
        a.agentStatsPtr[i].quarantinedUntilTimestamp = until;
        a.agentStatsPtr[i].daysInQuarantine += (until - a.timestamp) / (24 * 60 / a.timeStep);

        // If agent was also diagnosed (is sick with COVID)
        if (a.diagnosedPtr[i]) {
            // Place home under quarantine
            unsigned myHome = RealMovementOps::findActualLocationForType(i,
                a.homeType,
                a.locationOffsetPtr,
                a.possibleLocationsPtr,
                a.possibleTypesPtr,
                a.homeType,
                a.schoolType,
                a.workType,
                0,
                nullptr);
            if (a.quarantinePolicy > 1) {// Home under quarantine for 2 weeks from now
                a.locationQuarantineUntilPtr[myHome] = until;// TODO: quarantine period
                if (i == a.tracked) printf("\tFlagging home as quarantined: %d\n", myHome);
                // if (myHome==2149) printf("LOCATION 2149 quarantined until %d
                // because agent %d got
                // hospitalized\n",a.locationQuarantineUntilPtr[myHome],i);
            }// Place work/classroom under quarantine
            if (a.quarantinePolicy > 2 && previousQuarantineUntil < a.timestamp) {
                unsigned classroom = RealMovementOps::findActualLocationForType(i,
                    a.classroomType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);
                unsigned work = RealMovementOps::findActualLocationForType(i,
                    a.workType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);
                unsigned toClose[2] = { classroom, work };
                for (unsigned loc : toClose) {
                    if (loc != std::numeric_limits<unsigned>::max()
                        && (a.locationTypePtr[loc] == a.workType || a.locationTypePtr[loc] == a.classroomType)
                        // only quarantining work & classrooms
                        //&& a.locationTypePtr[loc] != a.doctorType
                        //&& a.locationTypePtr[loc] != a.hospitalType
                        && a.locationQuarantineUntilPtr[loc] < a.timestamp && a.locationStatesPtr[loc] == true
                        && a.closedUntilPtr[loc] < a.timestamp) {
                        if (i == a.tracked) printf("\tFlagging work/classroom as quarantined: %d\n", loc);
                        a.locationQuarantineUntilPtr[loc] = until;// TODO: quarantine period
                    }
                }
            }
        }
    }

    constexpr unsigned hviRotatingCode = 255u;

    [[nodiscard]] inline HD bool isDiscretionaryType(unsigned t) {
        // public space 1, restaurants 5, large venues 6, short-visit shops 7, long-visit shops 8, church 9, recreation 10
        return t < 32u && ((0x7E2u >> t) & 1u);
    }

    // Uniform pick over the agent's own venues of types 5, 7 and 8 (the rotating set of an occupationally mobile worker)
    [[nodiscard]] inline HD unsigned findRotatingLocation(unsigned agent,
        unsigned long* locationOffsetPtr,
        unsigned* possibleLocationsPtr,
        unsigned* possibleTypesPtr) {
        unsigned counter = 0;
        for (unsigned i = locationOffsetPtr[agent]; i < locationOffsetPtr[agent + 1]; i++) {
            unsigned t = possibleTypesPtr[i];
            if (t == 5u || t == 7u || t == 8u) counter++;
        }
        if (counter == 0) return std::numeric_limits<unsigned>::max();
        unsigned pick = RandomGenerator::randomUnsigned(counter);
        unsigned c = 0;
        for (unsigned i = locationOffsetPtr[agent]; i < locationOffsetPtr[agent + 1]; i++) {
            unsigned t = possibleTypesPtr[i];
            if (t == 5u || t == 7u || t == 8u) {
                if (c == pick) return possibleLocationsPtr[i];
                c++;
            }
        }
        return std::numeric_limits<unsigned>::max();
    }

    // Chance of event j of a window for an agent whose discretionary activity multiplier is u. Discretionary chances are
    // scaled by g and the home event takes up the difference, so that the window still sums as before. A window without a
    // home event, or without a discretionary event, is unchanged. For u > 1 the factor g stops where the home chance reaches 0.
    [[nodiscard]] inline HD float hviEffectiveChance(const AgentTypeList::Event* ev, unsigned begin, unsigned num, unsigned j, float u, unsigned homeType) {
        const float c = ev[begin + j].chance;
        if (u == 1.0f) return c;
        float sumDisc = 0.0f;
        float homeChance = 0.0f;
        int homeIdx = -1;
        for (unsigned k = 0; k < num; ++k) {
            const unsigned t = ev[begin + k].locationType;
            if (isDiscretionaryType(t)) sumDisc += ev[begin + k].chance;
            else if (t == homeType && homeIdx < 0) {
                homeIdx = static_cast<int>(k);
                homeChance = ev[begin + k].chance;
            }
        }
        if (homeIdx < 0 || !(sumDisc > 0.0f)) return c;
        float g = u;
        if (g > 1.0f) g = fminf(g, 1.0f + homeChance / sumDisc);
        if (static_cast<int>(j) == homeIdx) return fmaxf(homeChance - (g - 1.0f) * sumDisc, 0.0f);
        if (isDiscretionaryType(ev[begin + j].locationType)) return c * g;
        return c;
    }

    [[nodiscard]] inline HD bool isHighType(unsigned t, unsigned mask) { return t < 32u && ((mask >> t) & 1u); }

    // Chance of event j of a window for an agent outside the class when the scene is minority-dominated: the chances of the
    // high-L types are multiplied by s (on top of the agent's hviEffectiveChance scaling by u) and the home event takes up
    // the difference. A window without a home event is unchanged.
    [[nodiscard]] inline HD float hviOthersChance(const AgentTypeList::Event* ev, unsigned begin, unsigned num, unsigned j, float u, float s, unsigned homeType, unsigned mask) {
        const float c = hviEffectiveChance(ev, begin, num, j, u, homeType);
        float sumHigh = 0.0f;
        int homeIdx = -1;
        for (unsigned k = 0; k < num; ++k) {
            const unsigned t = ev[begin + k].locationType;
            if (isHighType(t, mask)) sumHigh += hviEffectiveChance(ev, begin, num, k, u, homeType);
            else if (t == homeType && homeIdx < 0) homeIdx = static_cast<int>(k);
        }
        if (homeIdx < 0 || !(sumHigh > 0.0f)) return c;
        if (static_cast<int>(j) == homeIdx) return c + (1.0f - s) * sumHigh;
        if (isHighType(ev[begin + j].locationType, mask)) return c * s;
        return c;
    }

    template<typename PPState, typename AgentMeta, typename LocationType>
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        void
        checkLarger(unsigned i, MovementArguments<PPState, AgentMeta, LocationType>& a) {
        /*      if (a.stepsUntilMovePtr[i] >  a.simTime.getStepsUntilMidnight(a.timeStep)) {
            printf("WARN LARGER %d > %d\n", a.stepsUntilMovePtr[i],  a.simTime.getStepsUntilMidnight(a.timeStep));
        }*/
    }

    template<typename PPState, typename AgentMeta, typename LocationType>
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        void
        doMovement(unsigned i, MovementArguments<PPState, AgentMeta, LocationType>& a) {
        unsigned& agentType = a.agentTypesPtr[i];

        // if not dead or not in hospital (covid or non-covid) go home at curfew
        if (a.enableCurfew && a.curfewBegin == a.simTime.getMinutes() / a.timeStep) {
            states::WBStates wBState = a.agentStatesPtr[i].getWBState();
            bool deadOrHospitalized = (wBState == states::WBStates::D || wBState == states::WBStates::S);
            bool hospitalizedWithNonCOVID = (a.agentStatsPtr[i].hospitalizedTimestamp <= a.timestamp
                                             && a.agentStatsPtr[i].hospitalizedUntilTimestamp > a.timestamp);
            if (!deadOrHospitalized && !hospitalizedWithNonCOVID) {
                if (agentType + 1 == 7) {// afternoon shift worker
                    // if currently at work, do nothing
                    unsigned workplace = RealMovementOps::findActualLocationForType(i,
                        a.workType,
                        a.locationOffsetPtr,
                        a.possibleLocationsPtr,
                        a.possibleTypesPtr,
                        a.homeType,
                        a.schoolType,
                        a.workType,
                        0,
                        nullptr);
                    // if not at workplace, or workplace is closed, move home, but allow movement later if not closed
                    if (a.agentLocationsPtr[i] != workplace || a.locationStatesPtr[workplace] == false) {
                        a.agentLocationsPtr[i] = RealMovementOps::findActualLocationForType(i,
                            a.homeType,
                            a.locationOffsetPtr,
                            a.possibleLocationsPtr,
                            a.possibleTypesPtr,
                            a.homeType,
                            a.schoolType,
                            a.workType,
                            0,
                            nullptr);
                        if (a.locationStatesPtr[workplace] == false) {
                            a.stepsUntilMovePtr[i] = a.simTime.getStepsUntilMidnight(a.timeStep);
                            return;        
                        } 
                    }

                } else {
                    a.stepsUntilMovePtr[i] = a.simTime.getStepsUntilMidnight(a.timeStep);
                    a.agentLocationsPtr[i] = RealMovementOps::findActualLocationForType(i,
                        a.homeType,
                        a.locationOffsetPtr,
                        a.possibleLocationsPtr,
                        a.possibleTypesPtr,
                        a.homeType,
                        a.schoolType,
                        a.workType,
                        0,
                        nullptr);
                    if (a.tracked == i)
                        printf("Agent %d day %d at %d:%d WBState %d moved to home %d due to curfew\n",
                            i,
                            (int)a.day,
                            a.simTime.getMinutes() / 60,
                            a.simTime.getMinutes() % 60,
                            (int)wBState,
                            a.agentLocationsPtr[i]);
                    return;
                }
            }
        }

        if (a.stepsUntilMovePtr[i] > 0) {
            a.stepsUntilMovePtr[i]--;
            return;
        }

        //Check if quarantine is over
        if (a.agentStatsPtr[i].quarantinedUntilTimestamp <= a.timestamp) { a.quarantinedPtr[i] = false; }

        states::WBStates wBState = a.agentStatesPtr[i].getWBState();
        if (wBState == states::WBStates::D) {// If dead, do not go anywhere
            a.stepsUntilMovePtr[i] = std::numeric_limits<unsigned>::max();
            a.agentLocationsPtr[i] = a.cemeteryLoc;
            return;
        }

        unsigned agentHome = RealMovementOps::findActualLocationForType(i,
            a.homeType,
            a.locationOffsetPtr,
            a.possibleLocationsPtr,
            a.possibleTypesPtr,
            a.homeType,
            a.schoolType,
            a.workType,
            0,
            nullptr);

        // if non-COVID hospitalization, go to hospital
        if (a.agentStatsPtr[i].hospitalizedTimestamp <= a.timestamp
            && a.agentStatsPtr[i].hospitalizedUntilTimestamp > a.timestamp && wBState != states::WBStates::S
            && wBState != states::WBStates::D) {

            a.stepsUntilMovePtr[i] = MIN(
                a.agentStatsPtr[i].hospitalizedUntilTimestamp - a.timestamp - 1, a.simTime.getStepsUntilMidnight(a.timeStep));
            a.agentLocationsPtr[i] = RealMovementOps::findActualLocationForType(i,
                a.hospitalType,
                a.locationOffsetPtr,
                a.possibleLocationsPtr,
                a.possibleTypesPtr,
                a.homeType,
                a.schoolType,
                a.workType,
                0,
                nullptr);
            //Diagnose with COVID if infected
            if (!a.diagnosedPtr[i] && a.agentStatesPtr[i].isInfectious()) {
                a.diagnosedPtr[i] = true;
                a.agentStatsPtr[i].diagnosedTimestamp = a.timestamp;
                if (a.simTime.getStepsUntilMidnight(a.timeStep) == 24 * 60 / a.timeStep)// is it midnight
                    a.agentStatsPtr[i].diagnosedTimestamp++;// shift timestamp by 1 to avoid
                                                            // being counted as random test in
                                                            // TestingPolicy

                if (i == a.tracked) printf("\tDiagnosed at location %d\n", a.agentLocationsPtr[i]);

                RealMovementOps::quarantineAgent(i,
                    a,
                    a.timestamp + a.quarantineLength * 24 * 60 / a.timeStep, a.quarantineImmuneActive);
            }

            if (i == a.tracked) {
                printf(
                    "Agent %d of type %d day %d at %d:%d WBState %d in hospital %d due to non-COVID hospitalization between "
                    "%d-%d\n",
                    i,
                    agentType + 1,
                    (int)a.day,
                    a.simTime.getMinutes() / 60,
                    a.simTime.getMinutes() % 60,
                    (int)wBState,
                    a.agentLocationsPtr[i],
                    a.agentStatsPtr[i].hospitalizedTimestamp,
                    a.agentStatsPtr[i].hospitalizedUntilTimestamp);
            }
            checkLarger(i, a);
            return;
        }

        if (wBState == states::WBStates::S) {// go to hospital if in serious condition
            a.stepsUntilMovePtr[i] = a.simTime.getStepsUntilMidnight(a.timeStep);
            a.agentLocationsPtr[i] = RealMovementOps::findActualLocationForType(i,
                a.hospitalType,
                a.locationOffsetPtr,
                a.possibleLocationsPtr,
                a.possibleTypesPtr,
                a.homeType,
                a.schoolType,
                a.workType,
                0,
                nullptr);
            if (i == a.tracked) {
                printf(
                    "Agent %d of type %d day %d at %d:%d WBState %d in "
                    "hospital %d\n",
                    i,
                    agentType + 1,
                    (int)a.day,
                    a.simTime.getMinutes() / 60,
                    a.simTime.getMinutes() % 60,
                    (int)wBState,
                    a.agentLocationsPtr[i]);
            }
            // If not diagnosed before, diagnose & quarantine
            if (!a.diagnosedPtr[i] && a.agentStatesPtr[i].isInfectious()) {
                a.diagnosedPtr[i] = true;
                a.agentStatsPtr[i].diagnosedTimestamp = a.timestamp;
                if (a.simTime.getStepsUntilMidnight(a.timeStep) == 24 * 60 / a.timeStep)// is it midnight, and agent got S
                                                                                        // due to disease progression?
                    a.agentStatsPtr[i].diagnosedTimestamp++;// shift timestamp by 1 to avoid
                                                            // being counted as random test in
                                                            // TestingPolicy

                RealMovementOps::quarantineAgent(i, a, a.timestamp + a.quarantineLength * 24 * 60 / a.timeStep, a.quarantineImmuneActive);
            }
            checkLarger(i, a);
            return;
        }

        // Is agent currently in a place under quarantine
        if (a.quarantinePolicy > 1 && a.timestamp < a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]]
            && (a.locationTypePtr[a.agentLocationsPtr[i]] == a.homeType
                || a.locationTypePtr[a.agentLocationsPtr[i]] == a.schoolType// Only send agent to quarantine if this
                                                                            // is home, work or school
                || a.locationTypePtr[a.agentLocationsPtr[i]] == a.classroomType
                || a.locationTypePtr[a.agentLocationsPtr[i]] == a.workType)) {
            if (a.quarantinedPtr[i] == false) {
                if (i == a.tracked)
                    printf(
                        "Agent %d of type %d day %d at %d:%d location %d is "
                        "quarantined, staying at home until %d\n",
                        i,
                        agentType + 1,
                        (int)a.day,
                        a.simTime.getMinutes() / 60,
                        a.simTime.getMinutes() % 60,
                        a.agentLocationsPtr[i],
                        a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]]);
                RealMovementOps::quarantineAgent(i, a, a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]], a.quarantineImmuneActive);
            }
            // if now quarantined
            if (a.quarantinedPtr[i] == true) {
                a.stepsUntilMovePtr[i] = MIN(a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]] - a.timestamp - 1,
                    a.simTime.getStepsUntilMidnight(a.timeStep));

                if (i == a.tracked) {
                    printf(
                        "Agent %d of type %d day %d at %d:%d WBState %d at "
                        "location %d under quarantine (1), quarantined %d-%d "
                        "locationQuarantineUntil %d timestamp %d\n",
                        i,
                        agentType + 1,
                        (int)a.day,
                        a.simTime.getMinutes() / 60,
                        a.simTime.getMinutes() % 60,
                        (int)wBState,
                        a.agentLocationsPtr[i],
                        a.agentStatsPtr[i].quarantinedTimestamp,
                        a.agentStatsPtr[i].quarantinedUntilTimestamp,
                        a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]],
                        a.timestamp);
                }

                // If not home, send home
                unsigned homeLocation = RealMovementOps::findActualLocationForType(i,
                    a.homeType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);
                if (homeLocation != a.agentLocationsPtr[i]) {
                    a.agentLocationsPtr[i] = homeLocation;
                    // TODO: quarantine whole home??
                    // unsigned until =
                    // a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]];
                    // a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]] = until;
                }
                checkLarger(i, a);
                if (agentHome != std::numeric_limits<unsigned>::max() && a.agentLocationsPtr[i] != agentHome
                    && a.stepsUntilMovePtr[i] > 60 / a.timeStep)
                    a.stayedHomePtr[i] = false;
                return;
            }
        }

        // Should agent still be quarantined due to recent diagnosis
        if ((a.quarantinePolicy > 0
                && (a.diagnosedPtr[i]
                    || (a.agentStatsPtr[i].diagnosedTimestamp > 0
                        && (a.timestamp - a.agentStatsPtr[i].diagnosedTimestamp)
                               < a.quarantineLength * 24 * 60 / a.timeStep)))// stay home if diagnosed or
                                                                             // quarantine has not
                                                                             // expired
            || (a.quarantinePolicy > 0 && a.quarantinedPtr[i])) {

            // Diagnosed, but not yet quarantined
            if (a.quarantinePolicy > 0 && !a.quarantinedPtr[i]) {
                RealMovementOps::quarantineAgent(i, a, a.timestamp + a.quarantineLength * 24 * 60 / a.timeStep, a.quarantineImmuneActive);
                if (i == a.tracked && a.quarantinedPtr[i]) {
                    printf(
                        "Agent %d of type %d day %d at %d:%d WBState %d was "
                        "recently diagnosed, enforcing quarantine: diagnosed "
                        "%d diagnosedTimestamp %d, current timestamp %d\n",
                        i,
                        agentType + 1,
                        (int)a.day,
                        a.simTime.getMinutes() / 60,
                        a.simTime.getMinutes() % 60,
                        (int)wBState,
                        a.diagnosedPtr[i],
                        a.agentStatsPtr[i].diagnosedTimestamp,
                        a.timestamp);
                }
            }

            if (a.quarantinedPtr[i]) {
                // Stay in quarantine at home
                a.agentLocationsPtr[i] = RealMovementOps::findActualLocationForType(i,
                    a.homeType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);

                // if less than 2 weeks since diagnosis/quarantine, stay where agent
                // already is
                a.stepsUntilMovePtr[i] = a.simTime.getStepsUntilMidnight(a.timeStep);
                if (i == a.tracked) {
                    printf(
                        "Agent %d of type %d day %d at %d:%d WBState %d still "
                        "quarantined (2): diagnosed %d diagnosedTimestamp %d, "
                        "personal quarantine until %d, current timestamp %d\n",
                        i,
                        agentType + 1,
                        (int)a.day,
                        a.simTime.getMinutes() / 60,
                        a.simTime.getMinutes() % 60,
                        (int)wBState,
                        a.diagnosedPtr[i],
                        a.agentStatsPtr[i].diagnosedTimestamp,
                        a.agentStatsPtr[i].quarantinedUntilTimestamp,
                        a.timestamp);
                }
                checkLarger(i, a);
                if (agentHome != std::numeric_limits<unsigned>::max() && a.agentLocationsPtr[i] != agentHome
                    && a.stepsUntilMovePtr[i] > 60 / a.timeStep)
                    a.stayedHomePtr[i] = false;
                return;
            }
        }

        // HVI: remaining parts of a split discretionary stay (visits lever) or of a rotating workday
        if (a.repeatLeftPtr != nullptr && a.repeatLeftPtr[i] > 0 && wBState != states::WBStates::S) {
            unsigned rtype = a.repeatTypePtr[i];
            unsigned rloc = (rtype == RealMovementOps::hviRotatingCode)
                                ? RealMovementOps::findRotatingLocation(i, a.locationOffsetPtr, a.possibleLocationsPtr, a.possibleTypesPtr)
                                : RealMovementOps::findActualLocationForType(i,
                                      rtype,
                                      a.locationOffsetPtr,
                                      a.possibleLocationsPtr,
                                      a.possibleTypesPtr,
                                      a.homeType,
                                      a.schoolType,
                                      a.workType,
                                      1,
                                      a.locationStatesPtr);
            // a repeat is a visit to a different venue when the agent has one
            for (int attempt = 0; attempt < 8 && rloc == a.agentLocationsPtr[i]; ++attempt) {
                rloc = (rtype == RealMovementOps::hviRotatingCode)
                           ? RealMovementOps::findRotatingLocation(i, a.locationOffsetPtr, a.possibleLocationsPtr, a.possibleTypesPtr)
                           : RealMovementOps::findActualLocationForType(i,
                                 rtype,
                                 a.locationOffsetPtr,
                                 a.possibleLocationsPtr,
                                 a.possibleTypesPtr,
                                 a.homeType,
                                 a.schoolType,
                                 a.workType,
                                 1,
                                 a.locationStatesPtr);
            }
            a.repeatLeftPtr[i]--;
            if (rloc != std::numeric_limits<unsigned>::max() && a.locationStatesPtr[rloc] != false
                && a.closedUntilPtr[rloc] <= a.timestamp) {
                a.agentLocationsPtr[i] = rloc;
                if (a.rolePtr != nullptr) a.rolePtr[i] = static_cast<uint8_t>(rtype == RealMovementOps::hviRotatingCode ? a.workType : rtype);
                a.stepsUntilMovePtr[i] = a.repeatStepsPtr[i];
                if (agentHome != std::numeric_limits<unsigned>::max() && a.agentLocationsPtr[i] != agentHome
                    && a.stepsUntilMovePtr[i] > 60 / a.timeStep)
                    a.stayedHomePtr[i] = false;
                a.stepsUntilMovePtr[i]--;
                return;
            }
            a.repeatLeftPtr[i] = 0;
        }

        states::WBStates scheduleState = wBState;
        if (a.hviIsolationBreak && a.hviClassPtr != nullptr && a.hviClassPtr[i] != 0
            && (wBState == states::WBStates::N || wBState == states::WBStates::M))
            scheduleState = states::WBStates::W;
        unsigned agentTypeOffset = AgentTypeList::getOffsetIndex(agentType, scheduleState, a.day);
        unsigned eventsBegin = a.eventOffsetPtr[agentTypeOffset];
        unsigned eventsEnd = a.eventOffsetPtr[agentTypeOffset + 1];

        int activeEventsBegin = -1;
        int activeEventsEnd = -1;

        // Here we assume if multiple events are given for the same timeslot,
        // they all start & end at the same time
        for (unsigned j = eventsBegin; j < eventsEnd; j++) {
            if (a.simTime >= a.eventsPtr[j].start && a.simTime < a.eventsPtr[j].end && activeEventsBegin == -1)
                activeEventsBegin = j;
            if (a.simTime < a.eventsPtr[j].start) {
                activeEventsEnd = j;
                break;
            }
            if (j == eventsEnd - 1) {
                if (a.simTime >= a.eventsPtr[j].start && a.simTime < a.eventsPtr[j].end) activeEventsEnd = eventsEnd;
            }
        }
        if (i == a.tracked)
            printf(
                "Agent %d of type %d day %d at %d:%d WBState %d activeEvents: "
                "%d-%d\n",
                i,
                agentType + 1,
                (int)a.day,
                a.simTime.getMinutes() / 60,
                a.simTime.getMinutes() % 60,
                (int)wBState,
                activeEventsBegin,
                activeEventsEnd);

        // Possibilities:
        // 1 both are -1 -> no more events for that day. Should be home if
        // wBState != S, or at hospital if S
        // 2 Begin != -1, End == -1 -> last event for the day. Move there (if needed pick randomly)
        // 3 Begin == -1, End != -1 -> no events right now, but there will be some later
        //      3a if less than 30 mins until next possible event, then stay
        //      here 3b if 30-60 to next possible event, should go to public
        //      place (type 0) 3c more than 60 mins, then go home
        // 4 neither -1, then pick randomly between one of the events

        // ISSUES:
        // do we forcibly finish at midnight?? What if the duration goes beyond
        // that?
        unsigned newLocationType = std::numeric_limits<unsigned>::max();

        // Case 1
        if (activeEventsBegin == -1 && activeEventsEnd == -1) {
            newLocationType = wBState == states::WBStates::S ? a.hospitalType : a.homeType;// Hostpital if sick, home otherwise
            unsigned myHome = RealMovementOps::findActualLocationForType(i,
                newLocationType,
                a.locationOffsetPtr,
                a.possibleLocationsPtr,
                a.possibleTypesPtr,
                a.homeType,
                a.schoolType,
                a.workType,
                0,
                nullptr);
            a.agentLocationsPtr[i] = myHome;
            if (a.rolePtr != nullptr) a.rolePtr[i] = static_cast<uint8_t>(newLocationType);
            a.stepsUntilMovePtr[i] = a.simTime.getStepsUntilMidnight(a.timeStep);
            checkLarger(i, a);
            if (i == a.tracked)
                printf(
                    "\tCase 1- moving to locType %d location %d until midnight "
                    "(for %d steps)\n",
                    newLocationType,
                    myHome,
                    a.stepsUntilMovePtr[i] - 1);
        }
        // Case 2 and 4
        if (activeEventsBegin != -1) {
            unsigned numPotentialEvents = (activeEventsEnd == -1 ? activeEventsBegin + 1 : activeEventsEnd) - activeEventsBegin;
            unsigned pickedEventIdx = 0;
            TimeDayDuration basicDuration(0.0);
            if (numPotentialEvents == 1) {
                newLocationType = a.eventsPtr[activeEventsBegin].locationType;
                basicDuration = a.eventsPtr[activeEventsBegin].duration;
            } else {
                double rand = RandomGenerator::randomReal(1.0);
                float hviU = 1.0f;
                if (a.hviMultPtr != nullptr && !a.hviLeverDuration && ((a.hviStatesMask >> static_cast<unsigned>(wBState)) & 1u)
                    && (!a.hviInfectiousOnly || a.agentStatesPtr[i].isInfectious()))
                    hviU = a.hviMultPtr[i];
                const bool othersScene = a.hviOthersHighScale != 1.0f && a.hviClassPtr != nullptr && a.hviClassPtr[i] == 0
                                         && ((a.hviStatesMask >> static_cast<unsigned>(wBState)) & 1u);
                double threshhold = othersScene ? RealMovementOps::hviOthersChance(a.eventsPtr, activeEventsBegin, numPotentialEvents, 0, hviU, a.hviOthersHighScale, a.homeType, a.hviHighMask)
                                    : hviU == 1.0f ? a.eventsPtr[activeEventsBegin].chance
                                                   : RealMovementOps::hviEffectiveChance(a.eventsPtr, activeEventsBegin, numPotentialEvents, 0, hviU, a.homeType);
                unsigned idx = 0;
                while (rand > threshhold && idx < numPotentialEvents) {
                    idx++;
                    if (othersScene) {
                        if (idx < numPotentialEvents)
                            threshhold += RealMovementOps::hviOthersChance(a.eventsPtr, activeEventsBegin, numPotentialEvents, idx, hviU, a.hviOthersHighScale, a.homeType, a.hviHighMask);
                    } else if (hviU == 1.0f) threshhold += a.eventsPtr[activeEventsBegin + idx].chance;
                    else if (idx < numPotentialEvents)
                        threshhold += RealMovementOps::hviEffectiveChance(a.eventsPtr, activeEventsBegin, numPotentialEvents, idx, hviU, a.homeType);
                }
                if (idx == numPotentialEvents) {
                    /*printf("Error, overrun1: %g, agentType %d WB %d, day %d, time %d:%d\n",rand, agentType + 1, wBState,
                (int)a.day,
                a.simTime.getMinutes() / 60,
                a.simTime.getMinutes() % 60);*/
                    idx--;
                }
                pickedEventIdx = idx;
                newLocationType = a.eventsPtr[activeEventsBegin + idx].locationType;
                basicDuration = a.eventsPtr[activeEventsBegin + idx].duration;
            }

            // if agent has to stay home with children, then check to see if is work, and set it to home
            if (a.noWorkAgentPtr[i] != 0 && newLocationType == a.workType) {
                newLocationType = a.homeType;
                numPotentialEvents = 1;
                if (a.quarantinedPtr[i] == false) a.agentStatsPtr[i].daysInQuarantine++;
                if (i == a.tracked) printf("Agent %d not going to work because child at home\n", i);
            }

            // Round 8 tilt: a class member's low-L discretionary visit is moved, at the same duration, to a high-L type the agent has
            if (a.hviTilt > 0.0f && a.hviClassPtr != nullptr && a.hviClassPtr[i] != 0
                && ((a.hviStatesMask >> static_cast<unsigned>(wBState)) & 1u)
                && RealMovementOps::isDiscretionaryType(newLocationType) && !RealMovementOps::isHighType(newLocationType, a.hviHighMask)
                && RandomGenerator::randomReal(1.0) < a.hviTilt) {
                unsigned have = 0u;
                for (unsigned q = a.locationOffsetPtr[i]; q < a.locationOffsetPtr[i + 1]; q++) {
                    const unsigned t = a.possibleTypesPtr[q];
                    if (RealMovementOps::isHighType(t, a.hviHighMask)) have |= (1u << t);
                }
                unsigned cnt = 0u;
                for (unsigned t = 0; t < 32u; ++t) cnt += (have >> t) & 1u;
                if (cnt > 0u) {
                    unsigned pickT = RandomGenerator::randomUnsigned(cnt);
                    for (unsigned t = 0; t < 32u; ++t) {
                        if ((have >> t) & 1u) {
                            if (pickT == 0u) {
                                newLocationType = t;
                                break;
                            }
                            pickT--;
                        }
                    }
                }
            }

            // HVI occupational mobility: the working day is spent visiting a rotating set of shops and restaurants
            bool rotatingPick = false;
            unsigned rotatingLoc = std::numeric_limits<unsigned>::max();
            if (a.hviRotatePtr != nullptr && a.hviRotatePtr[i] != 0 && newLocationType == a.workType
                && ((a.hviStatesMask >> static_cast<unsigned>(wBState)) & 1u)) {
                rotatingLoc = RealMovementOps::findRotatingLocation(i, a.locationOffsetPtr, a.possibleLocationsPtr, a.possibleTypesPtr);
                if (rotatingLoc != std::numeric_limits<unsigned>::max()) {
                    rotatingPick = true;
                    newLocationType = a.locationTypePtr[rotatingLoc];
                }
            }
            unsigned newLocation = rotatingPick ? rotatingLoc
                                                : RealMovementOps::findActualLocationForType(i,
                                                      newLocationType,
                                                      a.locationOffsetPtr,
                                                      a.possibleLocationsPtr,
                                                      a.possibleTypesPtr,
                                                      a.homeType,
                                                      a.schoolType,
                                                      a.workType,
                                                      numPotentialEvents == 1,
                                                      a.locationStatesPtr);
            // Check if location is open/closed. If closed, go home instead
            unsigned wasClosed = std::numeric_limits<unsigned>::max();
            bool schoolAndTooOld = (newLocationType == a.schoolType || newLocationType == a.classroomType)
                                   && a.agentMetaDataPtr[i].getAge() >= a.schoolAgeRestriction;
            if (schoolAndTooOld //school is closed for student
                || ((a.locationStatesPtr[newLocation] == false || a.closedUntilPtr[newLocation] > a.timestamp)
                    && newLocationType != a.workType) //or destination is closed and it's not agent's workplace
                || (a.lockdownNonvaccActive && a.agentStatsPtr[i].immunizationTimestamp==0)) //or non-immune should be locked down, and this is nonessential
                {
                // If closed, but there is another option to go to different type location, try that
                if (numPotentialEvents > 1) {
                    double rand = RandomGenerator::randomReal(1.0);
                    double threshhold = (pickedEventIdx == 0)
                                            ? 0.0
                                            : a.eventsPtr[activeEventsBegin].chance
                                                  / (1.0 - a.eventsPtr[activeEventsBegin + pickedEventIdx].chance);
                    unsigned idx = 0;
                    while (rand > threshhold && idx < numPotentialEvents) {
                        idx++;
                        threshhold += (pickedEventIdx == idx)
                                          ? 0.0
                                          : a.eventsPtr[activeEventsBegin + idx].chance
                                                / (1.0 - a.eventsPtr[activeEventsBegin + pickedEventIdx].chance);
                    }
                    if (idx == numPotentialEvents) { idx--; }
                    newLocationType = a.eventsPtr[activeEventsBegin + idx].locationType;
                    basicDuration = a.eventsPtr[activeEventsBegin + idx].duration;
                    newLocation = RealMovementOps::findActualLocationForType(i,
                        newLocationType,
                        a.locationOffsetPtr,
                        a.possibleLocationsPtr,
                        a.possibleTypesPtr,
                        a.homeType,
                        a.schoolType,
                        a.workType,
                        0,
                        nullptr);
                    wasClosed = std::numeric_limits<unsigned>::max();
                    bool schoolAndTooOld2 = (newLocationType == a.schoolType || newLocationType == a.classroomType)
                                            && a.agentMetaDataPtr[i].getAge() >= a.schoolAgeRestriction;
                    // is that closed too?
                    if (schoolAndTooOld
                        || ((a.locationStatesPtr[newLocation] == false || a.closedUntilPtr[newLocation] > a.timestamp)
                               && newLocationType != a.workType)
                        || (a.lockdownNonvaccActive && a.agentStatsPtr[i].immunizationTimestamp==0)) {
                        wasClosed = newLocation;
                        newLocation = RealMovementOps::findActualLocationForType(i,
                            a.homeType,
                            a.locationOffsetPtr,
                            a.possibleLocationsPtr,
                            a.possibleTypesPtr,
                            a.homeType,
                            a.schoolType,
                            a.workType,
                            0,
                            nullptr);
                    }
                } else {
                    wasClosed = newLocation;
                    newLocation = RealMovementOps::findActualLocationForType(i,
                        a.homeType,
                        a.locationOffsetPtr,
                        a.possibleLocationsPtr,
                        a.possibleTypesPtr,
                        a.homeType,
                        a.schoolType,
                        a.workType,
                        0,
                        nullptr);
                }
            } else if (newLocationType == a.schoolType) {
                // if classroom closed, don't go to school either
                unsigned myClassroom = RealMovementOps::findActualLocationForType(i,
                    a.classroomType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);
                if (myClassroom != std::numeric_limits<unsigned>::max() && a.closedUntilPtr[myClassroom] > a.timestamp) {
                    wasClosed = newLocation;
                    newLocation = RealMovementOps::findActualLocationForType(i,
                        a.homeType,
                        a.locationOffsetPtr,
                        a.possibleLocationsPtr,
                        a.possibleTypesPtr,
                        a.homeType,
                        a.schoolType,
                        a.workType,
                        0,
                        nullptr);
                }
            }

            a.agentLocationsPtr[i] = newLocation;
            if (a.rolePtr != nullptr)
                a.rolePtr[i] = static_cast<uint8_t>(wasClosed != std::numeric_limits<unsigned>::max() ? a.homeType
                                                    : (rotatingPick ? a.workType : newLocationType));
            if (a.hviMultPtr != nullptr) {
                // role-based: the event type is what is scaled; the physical venue may be of any type
                const unsigned finalType = wasClosed == std::numeric_limits<unsigned>::max() ? newLocationType : 0xffffu;
                const bool stateOk = ((a.hviStatesMask >> static_cast<unsigned>(wBState)) & 1u) != 0u;
                const bool whenOk = !a.hviInfectiousOnly || a.agentStatesPtr[i].isInfectious();
                if (rotatingPick && wasClosed == std::numeric_limits<unsigned>::max() && stateOk) {
                    // 8 working hours become 1-hour visits to the rotating set
                    unsigned total = basicDuration.getMinutes();
                    unsigned visit = 60u;
                    if (total > visit) {
                        a.repeatLeftPtr[i] = static_cast<uint8_t>(MIN(total / visit - 1u, 254u));
                        a.repeatTypePtr[i] = static_cast<uint8_t>(RealMovementOps::hviRotatingCode);
                        a.repeatStepsPtr[i] = TimeDayDuration(visit).steps(a.timeStep);
                        basicDuration = TimeDayDuration(visit);
                    }
                } else if (!rotatingPick && stateOk && whenOk && RealMovementOps::isDiscretionaryType(finalType)) {
                    float u = a.hviLeverDuration ? a.hviMultPtr[i] : 1.0f;
                    unsigned mins = basicDuration.getMinutes();
                    if (u != 1.0f && mins > 0u) {
                        unsigned nm = static_cast<unsigned>(lroundf(static_cast<float>(mins) * u));
                        if (nm < a.timeStep) nm = a.timeStep;
                        basicDuration = TimeDayDuration(nm);
                        mins = nm;
                    }
                    if (a.hviVisitsFactor > 1u && a.hviClassPtr[i] != 0 && mins > 0u) {
                        unsigned pv = mins / a.hviVisitsFactor;
                        if (pv < a.timeStep) pv = a.timeStep;
                        a.repeatLeftPtr[i] = static_cast<uint8_t>(a.hviVisitsFactor - 1u);
                        a.repeatTypePtr[i] = static_cast<uint8_t>(finalType);
                        a.repeatStepsPtr[i] = TimeDayDuration(pv).steps(a.timeStep);
                        basicDuration = TimeDayDuration(pv);
                    }
                }
            }
            if (basicDuration.getHours() > 24) {
                a.stepsUntilMovePtr[i] = a.simTime.getStepsUntilMidnight(a.timeStep);
            } else if (activeEventsEnd == -1) {
                if ((a.simTime + basicDuration).isOverMidnight()) {
                    a.stepsUntilMovePtr[i] = a.simTime.getStepsUntilMidnight(a.timeStep);
                } else {
                    // does not last till midnight, but no events afterwards -
                    // spend full duration there
                    a.stepsUntilMovePtr[i] = basicDuration.steps(a.timeStep);
                }
            } else {
                // If duration is less then the beginning of the next move
                // window, then spend full duration here
                if (a.simTime + basicDuration < a.eventsPtr[activeEventsEnd].start) {
                    a.stepsUntilMovePtr[i] = basicDuration.steps(a.timeStep);
                    checkLarger(i, a);
                } else if (a.simTime + basicDuration > a.eventsPtr[activeEventsEnd].end) {
                    a.stepsUntilMovePtr[i] = (a.eventsPtr[activeEventsEnd].end - a.simTime).steps(a.timeStep) - 1;
                    checkLarger(i, a);
                } else {
                    // Otherwise I need to move again randomly between the end
                    // of this duration and the end of next movement window
                    TimeDayDuration window = a.eventsPtr[activeEventsEnd].end - (a.simTime + basicDuration);
                    unsigned st = window.steps(a.timeStep);
                    unsigned randExtra = RandomGenerator::randomUnsigned(st);
                    a.stepsUntilMovePtr[i] = basicDuration.steps(a.timeStep) + randExtra;
                    checkLarger(i, a);
                }
            }
            if (agentType + 1 == 7 && a.enableCurfew
                && (a.curfewBegin <= a.simTime.getMinutes() / a.timeStep
                    || a.curfewEnd > a.simTime.getMinutes() / a.timeStep)) {
                bool workButClosed =
                    (newLocationType == a.workType
                        && (a.locationStatesPtr[newLocation] == false || a.closedUntilPtr[newLocation] > a.timestamp));
                if (workButClosed || (newLocationType != a.workType && newLocationType != a.homeType)) {
                    a.agentLocationsPtr[i] = agentHome;
                    if (i == a.tracked) {
                        printf(
                            "\tCase 2&4- Night shift worker tried moving to locType %d location %d, "
                            "but it's curfew, moving home to %d for %d steps\n",
                            newLocationType,
                            newLocation,
                            agentHome,
                            a.stepsUntilMovePtr[i] - 1);
                    }
                }
            }

            if (i == a.tracked) {
                if (wasClosed == std::numeric_limits<unsigned>::max())
                    printf(
                        "\tCase 2&4- moving to locType %d location %d for %d "
                        "steps\n",
                        newLocationType,
                        newLocation,
                        a.stepsUntilMovePtr[i] - 1);
                else
                    printf(
                        "\tCase 2&4- tried moving to locType %d location %d, "
                        "but was closed, moving home to %d for %d steps\n",
                        newLocationType,
                        wasClosed,
                        newLocation,
                        a.stepsUntilMovePtr[i] - 1);
            }
        }

        // Case 3
        if (activeEventsBegin == -1 && activeEventsEnd != -1) {
            // Randomly decide when the move will occur in the next window:
            TimeDayDuration length = a.eventsPtr[activeEventsEnd].end - a.eventsPtr[activeEventsEnd].start;
            unsigned length_steps = length.steps(a.timeStep);
            unsigned randDelay = RandomGenerator::randomUnsigned(length_steps);
            a.stepsUntilMovePtr[i] = (a.eventsPtr[activeEventsEnd].start - a.simTime).steps(a.timeStep) + randDelay;
            unsigned timeLeft = a.stepsUntilMovePtr[i];
            // Case 3.a -- less than 30 mins -> stay here
            if (timeLeft < TimeDayDuration(0.3).steps(a.timeStep)) {
                if (i == a.tracked) printf("\tCase 3a- staying in place for %d steps\n", a.stepsUntilMovePtr[i] - 1);
                // Do nothing - location stays the same
            } else if (timeLeft < TimeDayDuration(1.0).steps(a.timeStep)) {
                newLocationType = a.publicPlaceType;
                unsigned myPublicPlace = RealMovementOps::findActualLocationForType(i,
                    a.publicPlaceType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);
                a.agentLocationsPtr[i] = myPublicPlace;
                if (a.rolePtr != nullptr) a.rolePtr[i] = static_cast<uint8_t>(a.publicPlaceType);
                if (i == a.tracked)
                    printf(
                        "\tCase 3b- moving to public Place type 1 location %d "
                        "for %d steps\n",
                        myPublicPlace,
                        a.stepsUntilMovePtr[i] - 1);
            } else {
                newLocationType = a.homeType;
                unsigned myHome = RealMovementOps::findActualLocationForType(i,
                    a.homeType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);
                a.agentLocationsPtr[i] = myHome;
                if (a.rolePtr != nullptr) a.rolePtr[i] = static_cast<uint8_t>(a.homeType);
                if (i == a.tracked)
                    printf(
                        "\tCase 3c- moving to home type 2 location %d for %d "
                        "steps\n",
                        myHome,
                        a.stepsUntilMovePtr[i] - 1);
            }
        }

        // Has agent just gone someplace currently under quarantine
        if (a.quarantinePolicy > 1 && a.timestamp < a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]]
            && (a.locationTypePtr[a.agentLocationsPtr[i]] == a.homeType
                || a.locationTypePtr[a.agentLocationsPtr[i]] == a.schoolType// Only send agent to quarantine if this
                                                                            // is home, work or school
                || a.locationTypePtr[a.agentLocationsPtr[i]] == a.classroomType
                || a.locationTypePtr[a.agentLocationsPtr[i]] == a.workType)) {
            // if not currently under quarantine
            if (!a.quarantinedPtr[i]) {
                RealMovementOps::quarantineAgent(i, a, a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]], a.quarantineImmuneActive);

                if (i == a.tracked && a.quarantinedPtr[i])
                    printf(
                        "Agent %d of type %d day %d at %d:%d location %d is "
                        "quarantined, staying at home until %d\n",
                        i,
                        agentType + 1,
                        (int)a.day,
                        a.simTime.getMinutes() / 60,
                        a.simTime.getMinutes() % 60,
                        a.agentLocationsPtr[i],
                        a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]]);
            }
            if (a.quarantinedPtr[i]) {
                a.stepsUntilMovePtr[i] = MIN(a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]] - a.timestamp - 1,
                    a.simTime.getStepsUntilMidnight(a.timeStep));
                checkLarger(i, a);

                if (i == a.tracked) {
                    printf(
                        "Agent %d of type %d day %d at %d:%d WBState %d at "
                        "location %d under quarantine (1), quarantined %d-%d "
                        "locationQuarantineUntil %d timestamp %d\n",
                        i,
                        agentType + 1,
                        (int)a.day,
                        a.simTime.getMinutes() / 60,
                        a.simTime.getMinutes() % 60,
                        (int)wBState,
                        a.agentLocationsPtr[i],
                        a.agentStatsPtr[i].quarantinedTimestamp,
                        a.agentStatsPtr[i].quarantinedUntilTimestamp,
                        a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]],
                        a.timestamp);
                }

                // If not home, send home
                unsigned homeLocation = RealMovementOps::findActualLocationForType(i,
                    a.homeType,
                    a.locationOffsetPtr,
                    a.possibleLocationsPtr,
                    a.possibleTypesPtr,
                    a.homeType,
                    a.schoolType,
                    a.workType,
                    0,
                    nullptr);
                if (homeLocation != a.agentLocationsPtr[i]) {
                    // unsigned until =
                    // a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]];
                    a.agentLocationsPtr[i] = homeLocation;
                    // TODO: quarantine whole home??
                    // a.locationQuarantineUntilPtr[a.agentLocationsPtr[i]] = until;
                }
                checkLarger(i, a);
                if (agentHome != std::numeric_limits<unsigned>::max() && a.agentLocationsPtr[i] != agentHome
                    && a.stepsUntilMovePtr[i] > 60 / a.timeStep)
                    a.stayedHomePtr[i] = false;
                return;
            }
        }

        // if (a.locationTypePtr[a.agentLocationsPtr[i]] == a.workType) {
        //     printf("Agent %d  of type %d moved to work type location %d at day %d %d:%d\n",
        //             i, agentType+1, a.agentLocationsPtr[i],
        //             (int)a.day,
        //             a.simTime.getMinutes() / 60,
        //             a.simTime.getMinutes() % 60);
        // }76030
        // if (a.agentLocationsPtr[i] == 76030) {
        //      printf("Agent %d  of type %d moved to location %d type %d at day %d %d:%d\n",
        //             i, agentType+1, a.agentLocationsPtr[i],
        //             a.locationTypePtr[a.agentLocationsPtr[i]],
        //             (int)a.day,
        //             a.simTime.getMinutes() / 60,
        //             a.simTime.getMinutes() % 60);
        // }


        // Diagnosis-related operations
        if (newLocationType == a.hospitalType || (newLocationType == a.doctorType && RandomGenerator::randomReal(1.0)<0.7)) {
            // If previously undiagnosed and
            if (!a.diagnosedPtr[i] && a.agentStatesPtr[i].isInfectious()) {
                a.diagnosedPtr[i] = true;
                a.agentStatsPtr[i].diagnosedTimestamp = a.timestamp;
                if (a.simTime.getStepsUntilMidnight(a.timeStep) == 24 * 60 / a.timeStep)// is it midnight, and agent got S
                                                                                        // due to disease progression?
                    a.agentStatsPtr[i].diagnosedTimestamp++;// shift timestamp by 1 to avoid
                                                            // being counted as random test in
                                                            // TestingPolicy

                if (i == a.tracked) printf("\tDiagnosed at location %d\n", a.agentLocationsPtr[i]);

                RealMovementOps::quarantineAgent(i,
                    a,
                    a.timestamp + a.quarantineLength * 24 * 60 / a.timeStep, a.quarantineImmuneActive);// TODO: quarantine period

                // We are not moving the agent - stay here for full duration,
                // potentially infect others when moving next, he will go into
                // quarantine anyway (if enabled)
            }
        }
        checkLarger(i, a);
        if (agentHome != std::numeric_limits<unsigned>::max() && a.agentLocationsPtr[i] != agentHome
            && a.stepsUntilMovePtr[i] > 60 / a.timeStep) {
            a.stayedHomePtr[i] = false;
            if (i == a.tracked) printf("\tdid not stay home %d %d\n", a.agentLocationsPtr[i], agentHome);
        }
        a.stepsUntilMovePtr[i]--;
    }

#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    template<typename PPState, typename AgentMeta, typename LocationType>
    __global__ void doMovementDriver(unsigned numberOfAgents, MovementArguments<PPState, AgentMeta, LocationType> a) {
        unsigned i = threadIdx.x + blockIdx.x * blockDim.x;
        if (i < numberOfAgents) { RealMovementOps::doMovement(i, a); }
    }
#endif

    template<typename AgentMeta>
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        void
        checkUnderageAtHome(unsigned i,
            unsigned* noWorkPtr,
            AgentMeta* agentMetaDataPtr,
            bool* quarantinedPtr,
            bool* locationStatesPtr,
            unsigned* closedUntilPtr,
            unsigned long* locationOffsetPtr,
            unsigned* possibleLocationsPtr,
            unsigned* possibleTypesPtr,
            unsigned home,
            unsigned school,
            unsigned classroom,
            unsigned timestamp,
            unsigned schoolAgeRestriction) {
        if (agentMetaDataPtr[i].getAge() > 14) return;// Only underage
        if (quarantinedPtr[i]) {
            // If quarantined
            unsigned homeLocation = RealMovementOps::findActualLocationForType(
                i, home, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, school, classroom, 0, nullptr);
            if (homeLocation != std::numeric_limits<unsigned>::max()) noWorkPtr[homeLocation] = noWorkNeedsSelection;
        } else {
            // Check if school open/closed
            unsigned schoolLocation = RealMovementOps::findActualLocationForType(
                i, school, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, school, classroom, 0, nullptr);
            unsigned classroomLocation = RealMovementOps::findActualLocationForType(
                i, classroom, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, school, classroom, 0, nullptr);
            bool schoolAndTooOld = agentMetaDataPtr[i].getAge() >= schoolAgeRestriction;
            if (schoolAndTooOld
                || (schoolLocation != std::numeric_limits<unsigned>::max()
                    && (locationStatesPtr[schoolLocation] == false || closedUntilPtr[schoolLocation] > timestamp))
                || (classroomLocation != std::numeric_limits<unsigned>::max()
                    && (locationStatesPtr[classroomLocation] == false
                        || closedUntilPtr[classroomLocation] > timestamp))) {// School closed
                unsigned homeLocation = RealMovementOps::findActualLocationForType(
                    i, home, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, school, classroom, 0, nullptr);
                if (homeLocation != std::numeric_limits<unsigned>::max()) noWorkPtr[homeLocation] = noWorkNeedsSelection;
            }
        }
    }

#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    template<typename AgentMeta>
    __global__ void checkUnderageAtHomeDriver(unsigned numberOfAgents,
        unsigned* noWorkPtr,
        AgentMeta* agentMetaDataPtr,
        bool* quarantinedPtr,
        bool* locationStatesPtr,
        unsigned* closedUntilPtr,
        unsigned long* locationOffsetPtr,
        unsigned* possibleLocationsPtr,
        unsigned* possibleTypesPtr,
        unsigned home,
        unsigned school,
        unsigned classroom,
        unsigned timestamp,
        unsigned schoolAgeRestriction) {
        unsigned i = threadIdx.x + blockIdx.x * blockDim.x;
        if (i < numberOfAgents) {
            RealMovementOps::checkUnderageAtHome(i,
                noWorkPtr,
                agentMetaDataPtr,
                quarantinedPtr,
                locationStatesPtr,
                closedUntilPtr,
                locationOffsetPtr,
                possibleLocationsPtr,
                possibleTypesPtr,
                home,
                school,
                classroom,
                timestamp,
                schoolAgeRestriction);
        }
    }
#endif

    template<typename AgentMeta>
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        void
        setNoWorkToday(unsigned i,
            unsigned* noWorkLocPtr,
            AgentMeta* agentMetaDataPtr,
            unsigned long* locationOffsetPtr,
            unsigned* possibleLocationsPtr,
            unsigned* possibleTypesPtr,
            unsigned home) {
        if (agentMetaDataPtr[i].getAge() > 26 && agentMetaDataPtr[i].getAge() < 65) {
            unsigned homeLocation = RealMovementOps::findActualLocationForType(
                i, home, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, home, home, 0, nullptr);
            if (homeLocation != std::numeric_limits<unsigned>::max()) {
                const unsigned currentSelection = noWorkLocPtr[homeLocation];
                if (currentSelection != noWorkNoRequest) {
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
                    atomicMin(&noWorkLocPtr[homeLocation], i);
#else
                    if (currentSelection == noWorkNeedsSelection || i < currentSelection) noWorkLocPtr[homeLocation] = i;
#endif
                }
            }
        }
    }

    __host__
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
    inline bool isSelectedNoWorkAgent(unsigned selectedAgent, unsigned numberOfAgents) {
        return selectedAgent != noWorkNoRequest && selectedAgent != noWorkNeedsSelection && selectedAgent < numberOfAgents;
    }

    __host__
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        inline void
        finalizeNoWorkToday(unsigned locationIdx, unsigned numberOfAgents, const unsigned* noWorkLocPtr, uint8_t* noWorkAgentPtr) {
        const unsigned selectedAgent = noWorkLocPtr[locationIdx];
        if (isSelectedNoWorkAgent(selectedAgent, numberOfAgents)) noWorkAgentPtr[selectedAgent] = 1;
    }

#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    template<typename AgentMeta>
    __global__ void setNoWorkTodayDriver(unsigned numberOfAgents,
        unsigned* noWorkLocPtr,
        AgentMeta* agentMetaDataPtr,
        unsigned long* locationOffsetPtr,
        unsigned* possibleLocationsPtr,
        unsigned* possibleTypesPtr,
        unsigned home) {
        unsigned i = threadIdx.x + blockIdx.x * blockDim.x;
        if (i < numberOfAgents) {
            RealMovementOps::setNoWorkToday(i,
                noWorkLocPtr,
                agentMetaDataPtr,
                locationOffsetPtr,
                possibleLocationsPtr,
                possibleTypesPtr,
                home);
        }
    }

    static __global__ void finalizeNoWorkTodayDriver(
        unsigned numberOfLocations, unsigned numberOfAgents, const unsigned* noWorkLocPtr, uint8_t* noWorkAgentPtr) {
        unsigned i = threadIdx.x + blockIdx.x * blockDim.x;
        if (i < numberOfLocations) { RealMovementOps::finalizeNoWorkToday(i, numberOfAgents, noWorkLocPtr, noWorkAgentPtr); }
    }
#endif
    template<typename PPValues>
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        void
        checkSchoolWorkQuarantine(unsigned i,
            AgentStats* agentStatsPtr,
            PPValues* agentStatesPtr,
            bool* quarantinedPtr,
            unsigned* locationQuarantineUntilPtr,
            unsigned long* locationOffsetPtr,
            unsigned* possibleLocationsPtr,
            unsigned* possibleTypesPtr,
            unsigned home,
            unsigned work,
            unsigned school,
            unsigned classroom,
            unsigned timestamp,
            unsigned timeStep,
            unsigned tracked) {
        // If already quarantined, do nothing
        if (quarantinedPtr[i]) return;
        // If immune, do nothing
        if (agentStatsPtr[i].diagnosedTimestamp > 0 && agentStatesPtr[i].isInfected() == false) return;
        // Get work/school/classroom ID
        unsigned workLocation = RealMovementOps::findActualLocationForType(
            i, work, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, school, classroom, 0, nullptr);
        unsigned schoolLocation = RealMovementOps::findActualLocationForType(
            i, school, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, school, classroom, 0, nullptr);
        unsigned classroomLocation = RealMovementOps::findActualLocationForType(
            i, classroom, locationOffsetPtr, possibleLocationsPtr, possibleTypesPtr, home, school, classroom, 0, nullptr);

        // Check if school/classroom/work quarantined
        unsigned until = 0;
        if (schoolLocation != std::numeric_limits<unsigned>::max() && locationQuarantineUntilPtr[schoolLocation] > timestamp)
            until = locationQuarantineUntilPtr[schoolLocation];
        else if (classroomLocation != std::numeric_limits<unsigned>::max()
                 && locationQuarantineUntilPtr[classroomLocation] > timestamp)
            until = locationQuarantineUntilPtr[classroomLocation];
        else if (workLocation != std::numeric_limits<unsigned>::max() && locationQuarantineUntilPtr[workLocation] > timestamp)
            until = locationQuarantineUntilPtr[workLocation];

        // If so, quarantine agent
        if (until > 0) {
            quarantinedPtr[i] = true;
            agentStatsPtr[i].quarantinedTimestamp = timestamp;
            agentStatsPtr[i].quarantinedUntilTimestamp = until;
            agentStatsPtr[i].daysInQuarantine += (until - timestamp) / (24 * 60 / timeStep);
            if (i == tracked) {
                printf(
                    "Agent %d at %d: "
                    "school/class/work under quarantine, going to quarantine until %d ",
                    i,
                    timestamp,
                    agentStatsPtr[i].quarantinedUntilTimestamp);
            }
        }
    }

#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    template<typename PPValues>
    __global__ void checkSchoolWorkQuarantineDriver(unsigned numberOfAgents,
        AgentStats* agentStatsPtr,
        PPValues* agentStatesPtr,
        bool* quarantinedPtr,
        unsigned* locationQuarantineUntilPtr,
        unsigned long* locationOffsetPtr,
        unsigned* possibleLocationsPtr,
        unsigned* possibleTypesPtr,
        unsigned home,
        unsigned work,
        unsigned school,
        unsigned classroom,
        unsigned timestamp,
        unsigned timeStep,
        unsigned tracked) {
        unsigned i = threadIdx.x + blockIdx.x * blockDim.x;
        if (i < numberOfAgents) {
            RealMovementOps::checkSchoolWorkQuarantine(i,
                agentStatsPtr,
                agentStatesPtr,
                quarantinedPtr,
                locationQuarantineUntilPtr,
                locationOffsetPtr,
                possibleLocationsPtr,
                possibleTypesPtr,
                home,
                work,
                school,
                classroom,
                timestamp,
                timeStep,
                tracked);
        }
    }
#endif


#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    __device__
#endif
        inline void
        checkSchoolQuarantine(unsigned i,
            unsigned* schoolsPtr,
            unsigned* classroomsPtr,
            unsigned* classroomOffsetsPtr,
            unsigned* locationQuarantineUntilPtr,
            unsigned timestamp) {
        unsigned schoolIdx = schoolsPtr[i];
        if (locationQuarantineUntilPtr[schoolIdx] > timestamp) return;
        unsigned counter = 0;
        unsigned max = 0;
        for (unsigned classOffset = classroomOffsetsPtr[i]; classOffset < classroomOffsetsPtr[i + 1]; classOffset++) {
            unsigned classIdx = classroomsPtr[classOffset];
            if (locationQuarantineUntilPtr[classIdx] > timestamp) {
                counter++;
                max = max > locationQuarantineUntilPtr[classIdx] ? max : locationQuarantineUntilPtr[classIdx];
            }
        }
        if (counter > 1) {
            // printf("School %d has %d quarantined classes, quarantining entire school until %d\n", schoolIdx, counter, max);
            locationQuarantineUntilPtr[schoolIdx] = max;
            for (unsigned classOffset = classroomOffsetsPtr[i]; classOffset < classroomOffsetsPtr[i + 1]; classOffset++) {
                unsigned classIdx = classroomsPtr[classOffset];
                locationQuarantineUntilPtr[classIdx] = max;
            }
        }
    }

#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    static __global__ void checkSchoolQuarantineDriver(unsigned numSchools,
        unsigned* schoolsPtr,
        unsigned* classroomsPtr,
        unsigned* classroomOffsetsPtr,
        unsigned* locationQuarantineUntilPtr,
        unsigned timestamp) {
        unsigned i = threadIdx.x + blockIdx.x * blockDim.x;
        if (i < numSchools) {
            RealMovementOps::checkSchoolQuarantine(
                i, schoolsPtr, classroomsPtr, classroomOffsetsPtr, locationQuarantineUntilPtr, timestamp);
        }
    }
#endif
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
    template<typename T>
    __global__ void countByType(unsigned total, unsigned typeCount, T* types, unsigned *offsets, unsigned *counter) {
            unsigned position = threadIdx.x + blockIdx.x * blockDim.x;
            if (position < total) {
                unsigned count = offsets[position+1]-offsets[position];
                if (types[position] == 17) printf("in cemetery %d\n", count);
                if (count) atomicAdd(&counter[types[position]], count); 
            }
        }
#endif
}// namespace RealMovementOps

template<typename SimulationType>
class RealMovement {
    thrust::device_vector<unsigned> stepsUntilMove;
    thrust::device_vector<unsigned> noWorkLoc;// indicating children at home
    thrust::device_vector<uint8_t> noWorkAgent;// indicating agent staying home because children at home
    thrust::device_vector<unsigned> locationTypeCounter;
    unsigned publicSpace;
    unsigned home;
    unsigned hospital;
    unsigned cemeteryLoc;
    unsigned doctor;
    unsigned tracked;
    unsigned quarantineLength;
    unsigned school;
    unsigned classroom;
    unsigned work;
    std::string dumpLocationAgentList;
    std::string dumpLoctypeStat;
    // High-velocity individuals
    std::string hviMode = "off";
    double hviShape = 0.0;
    double hviClassFraction = 0.0;
    double hviClassFactor = 1.0;
    unsigned hviMinAge = 15;
    std::string hviTypes = "4,5,6,7,8";
    std::string hviStates = "WN";
    std::string hviWhen = "always";
    std::string hviLever = "chance";
    std::string hviScaleByType = "";
    std::string hviScaleByTypeWeekend = "";
    unsigned hviVisitsFactor = 1;
    double hviRotateFraction = 0.0;
    unsigned long long hviSeed = 0;
    unsigned hviControlDay = 0;
    std::string hviControlMode = "none";
    double hviControlParam = 1.0;
    std::string hviDump = "";
    std::string mobilityLog = "";
    double hviTilt = 0.0;
    std::string hviHighTypes = "5,6,9,10";
    double hviOthersHighScale = 1.0;
    unsigned hviIsolationBreak = 0;
    bool hviInitialised = false;
    bool hviControlApplied = false;
    thrust::device_vector<float> hviMult;
    thrust::device_vector<float> hviMultWeekend;
    thrust::device_vector<uint8_t> hviClass;
    thrust::device_vector<uint8_t> hviRotate;
    thrust::device_vector<uint8_t> repeatLeft;
    thrust::device_vector<uint8_t> repeatType;
    thrust::device_vector<unsigned> repeatSteps;
    // mobility log accumulators (host)
    bool mobInitialised = false;
    std::vector<unsigned> mobPrevLoc;
    std::vector<unsigned> mobSteps;       // [agent][daytype 2][kind 2: role, physical][group 6]
    std::vector<unsigned> mobMoves;       // [agent][daytype]
    std::vector<unsigned> mobVisits;      // [agent][daytype] discretionary-role stays
    std::vector<unsigned> mobTypeSteps;   // [agent][7] discretionary-role steps by physical location type 1,5,6,7,8,9,10
    std::vector<unsigned> mobAllTypeSteps;// [agent][17] steps at venues of each physical type, whatever the role (types in hptTypes)
    std::vector<uint8_t> mobPrevGroup;
    std::vector<uint8_t> mobLocType;
    std::vector<unsigned> mobStateDisc;   // [agent][wb 4] discretionary steps
    std::vector<unsigned> mobStateInf;    // [agent][wb 4] infectious steps
    std::vector<double> mobLsteps;        // discretionary steps weighted by location infectiousness
    std::vector<unsigned> mobDistinctDay; // [agent][daytype] sum over days of distinct discretionary venues
    std::vector<unsigned> mobDistinctWeek;// [agent] sum over weeks
    std::vector<unsigned> mobWeeks;
    std::vector<std::vector<unsigned>> mobVisitedDay, mobVisitedWeek;
    std::vector<unsigned> mobDays;        // [daytype]
    thrust::device_vector<uint8_t> agentRole;
    std::vector<uint8_t> mobLocGroup;     // per location (physical type group)
    std::vector<float> mobLocL;
    unsigned mobLastDay = 0xffffffffu;

    static int hptSlot(unsigned t) {
        switch (t) {
            case 1: return 0; case 2: return 1; case 3: return 2; case 4: return 3; case 5: return 4; case 6: return 5; case 7: return 6;
            case 8: return 7; case 9: return 8; case 10: return 9; case 11: return 10; case 12: return 11; case 13: return 12;
            case 14: return 13; case 22: return 14; case 33: return 15; case 44: return 16; default: return -1;
        }
    }

    static std::uint64_t hviMix(std::uint64_t x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }

public:
    bool enableCurfew = false;
    unsigned curfewBegin = 0;
    unsigned curfewEnd = 0;
    bool curfewTimeConverted = false;
    unsigned schoolAgeRestriction = 99;
    bool holidayModeActive = false;
    bool quarantineImmuneActive = false;
    bool lockdownNonvaccActive = false;
    unsigned quarantinePolicy;
    // add program parameters if we need any, this function got called already
    // from Simulation
    static void addProgramParameters(cxxopts::Options& options) {
        options.add_options()("trace",
            "Trace movements of agent",
            cxxopts::value<unsigned>()->default_value(std::to_string(std::numeric_limits<unsigned>::max())))("quarantinePolicy",
            "Quarantine policy: 0 - None, 1 - Agent only, 2 - Agent and "
            "household, 3 - + classroom/work, 4 - + school",
            cxxopts::value<unsigned>()->default_value(std::to_string(unsigned(3))))("quarantineLength",
            "Length of quarantine in days",
            cxxopts::value<unsigned>()->default_value(std::to_string(unsigned(10))))
            ("dumpLocationAgentList",
            "Dump per-location list of agents at each iteration (directory)",
            cxxopts::value<std::string>()->default_value(""))
            ("dumpLoctypeStat",
            "Dump per-location type daily occupancy stats (filename)",
            cxxopts::value<std::string>()->default_value(""))
            ("hviMode",
            "High-velocity individuals: off, gamma, lognormal or class. A persistent per-agent multiplier (mean 1 over eligible agents) on the duration of discretionary visits (location types 1,5,6,7,8,9,10)",
            cxxopts::value<std::string>()->default_value("off"))
            ("hviShape",
            "Shape a of the gamma or lognormal multiplier (squared coefficient of variation 1/a)",
            cxxopts::value<double>()->default_value("0"))
            ("hviClassFraction",
            "class mode: fraction f of eligible agents in the high-velocity class",
            cxxopts::value<double>()->default_value("0"))
            ("hviClassFactor",
            "class mode: multiplier F of the class; the others are scaled so that the mean stays 1",
            cxxopts::value<double>()->default_value("1"))
            ("hviMinAge",
            "Minimum age of eligible agents",
            cxxopts::value<unsigned>()->default_value("15"))
            ("hviTypes",
            "Eligible agent types (1-based ids, comma separated)",
            cxxopts::value<std::string>()->default_value("4,5,6,7,8"))
            ("hviStates",
            "Well-being states in which the multiplier acts, letters from W N M S",
            cxxopts::value<std::string>()->default_value("WN"))
            ("hviWhen",
            "always, or infectious (the multiplier acts only while the agent is infectious)",
            cxxopts::value<std::string>()->default_value("always"))
            ("hviLever",
            "Hours lever: chance (the multiplier scales discretionary chances against the home event within each window, per agent) or duration (it scales the duration of each discretionary stay)",
            cxxopts::value<std::string>()->default_value("chance"))
            ("hviScaleByType",
            "Per agent type scale on the multiplier, id:scale pairs (1-based type ids), used to keep mean discretionary hours at baseline",
            cxxopts::value<std::string>()->default_value(""))
            ("hviScaleByTypeWeekend",
            "As --hviScaleByType, for Saturday and Sunday (empty: the weekday scales)",
            cxxopts::value<std::string>()->default_value(""))
            ("hviVisitsFactor",
            "Visits lever: class members split each discretionary stay into this many shorter visits at different venues of the same type (hours unchanged)",
            cxxopts::value<unsigned>()->default_value("1"))
            ("hviRotateFraction",
            "Occupational mobility: this fraction of full-time workers (type 6) spend their working day in 1-hour visits to a rotating set of their own types 5, 7 and 8 venues",
            cxxopts::value<double>()->default_value("0"))
            ("hviSeed",
            "Seed of the HVI draws (0 = the run seed)",
            cxxopts::value<unsigned long long>()->default_value("0"))
            ("hviTilt",
            "Class members move this share of their low-L discretionary visits (types 1, 7, 8 and other non-high types) to the high-L types at the same duration (0 = off)",
            cxxopts::value<double>()->default_value("0"))
            ("hviHighTypes",
            "Location types counted as high-L by --hviTilt and --hviOthersHighScale",
            cxxopts::value<std::string>()->default_value("5,6,9,10"))
            ("hviOthersHighScale",
            "Agents outside the class multiply the chances of the high-L types by this factor; the difference goes to the home event (1 = off)",
            cxxopts::value<double>()->default_value("1"))
            ("hviIsolationBreak",
            "1: class members keep their W schedule in the well-being states N and M (no staying at home when symptomatic)",
            cxxopts::value<unsigned>()->default_value("0"))
            ("hviControlDay",
            "Day from which the control acts (0 = no control)",
            cxxopts::value<unsigned>()->default_value("0"))
            ("hviControlMode",
            "none, capTop (the class or the most active fraction is set to multiplier 1) or scaleAll (all eligible multipliers are scaled)",
            cxxopts::value<std::string>()->default_value("none"))
            ("hviControlParam",
            "capTop: fraction of eligible agents with the largest multiplier; scaleAll: scale factor",
            cxxopts::value<double>()->default_value("1"))
            ("hviDump",
            "Write the multiplier of every agent to this CSV (agent,type,age,m,class,rotate)",
            cxxopts::value<std::string>()->default_value(""))
            ("mobilityLog",
            "Write per-agent mobility summaries (moves, hours by place group, distinct venues) to this CSV, rewritten at the end of each day",
            cxxopts::value<std::string>()->default_value(""));
    }
    void initializeArgs(const cxxopts::ParseResult& result) {
        tracked = result["trace"].as<unsigned>();
        quarantinePolicy = result["quarantinePolicy"].as<unsigned>();
        quarantineLength = result["quarantineLength"].as<unsigned>();
        dumpLocationAgentList = result["dumpLocationAgentList"].as<std::string>();
        dumpLoctypeStat = result["dumpLoctypeStat"].as<std::string>();
        hviMode = result["hviMode"].as<std::string>();
        hviShape = result["hviShape"].as<double>();
        hviClassFraction = result["hviClassFraction"].as<double>();
        hviClassFactor = result["hviClassFactor"].as<double>();
        hviMinAge = result["hviMinAge"].as<unsigned>();
        hviTypes = result["hviTypes"].as<std::string>();
        hviStates = result["hviStates"].as<std::string>();
        hviWhen = result["hviWhen"].as<std::string>();
        hviLever = result["hviLever"].as<std::string>();
        if (hviLever != "chance" && hviLever != "duration") throw CustomErrors("--hviLever must be chance or duration");
        hviScaleByType = result["hviScaleByType"].as<std::string>();
        hviScaleByTypeWeekend = result["hviScaleByTypeWeekend"].as<std::string>();
        hviVisitsFactor = result["hviVisitsFactor"].as<unsigned>();
        hviRotateFraction = result["hviRotateFraction"].as<double>();
        hviSeed = result["hviSeed"].as<unsigned long long>();
        hviControlDay = result["hviControlDay"].as<unsigned>();
        hviControlMode = result["hviControlMode"].as<std::string>();
        hviControlParam = result["hviControlParam"].as<double>();
        hviDump = result["hviDump"].as<std::string>();
        mobilityLog = result["mobilityLog"].as<std::string>();
        hviTilt = result["hviTilt"].as<double>();
        hviHighTypes = result["hviHighTypes"].as<std::string>();
        hviOthersHighScale = result["hviOthersHighScale"].as<double>();
        hviIsolationBreak = result["hviIsolationBreak"].as<unsigned>();
        if (hviTilt < 0.0 || hviTilt > 1.0) throw CustomErrors("--hviTilt must be between 0 and 1");
        if (!(hviOthersHighScale >= 0.0)) throw CustomErrors("--hviOthersHighScale must be at least 0");
        if ((hviTilt > 0.0 || hviOthersHighScale != 1.0 || hviIsolationBreak != 0) && result["hviMode"].as<std::string>() != "class")
            throw CustomErrors("--hviTilt, --hviOthersHighScale and --hviIsolationBreak need --hviMode class");
        if (hviMode != "off" && hviMode != "gamma" && hviMode != "lognormal" && hviMode != "class")
            throw CustomErrors("--hviMode must be off, gamma, lognormal or class");
        if ((hviMode == "gamma" || hviMode == "lognormal") && !(hviShape > 0.0)) throw CustomErrors("--hviMode gamma/lognormal needs --hviShape > 0");
        if (hviMode == "class" && !(hviClassFraction > 0.0 && hviClassFraction < 1.0 && hviClassFraction * hviClassFactor < 1.0))
            throw CustomErrors("--hviMode class needs 0 < --hviClassFraction < 1 and fraction * factor < 1");
        if ((hviMode != "off" || hviRotateFraction > 0.0) && result["traitShape"].as<double>() > 0.0)
            throw CustomErrors("--hviMode cannot be combined with --traitShape (it can be combined with --sheddingShape, round 9)");
        if (result["sheddingClassMean"].as<double>() > 0.0 && hviMode != "class")
            throw CustomErrors("--sheddingClassMean needs --hviMode class");
        if (hviWhen != "always" && hviWhen != "infectious") throw CustomErrors("--hviWhen must be always or infectious");
        if (hviVisitsFactor < 1 || hviVisitsFactor > 16) throw CustomErrors("--hviVisitsFactor must be between 1 and 16");
        if (hviControlMode != "none" && hviControlMode != "capTop" && hviControlMode != "scaleAll")
            throw CustomErrors("--hviControlMode must be none, capTop or scaleAll");
        if (hviMode == "off" && (hviRotateFraction <= 0.0) && (hviVisitsFactor > 1 || hviControlDay > 0))
            throw CustomErrors("the HVI levers and control need --hviMode or --hviRotateFraction");
        if (dumpLocationAgentList.length()>0) Util::needAgentsSortedByLocation = 1;
    }
    void init(const parser::LocationTypes& data, unsigned cemeteryID) {
        publicSpace = data.publicSpace;
        home = data.home;
        hospital = data.hospital;
        cemeteryLoc = cemeteryID;
        doctor = data.doctor;
        school = data.school;
        work = data.work;
        classroom = data.classroom;
    }

    void dumpLoctypeStatNow(unsigned timestamp) {
        auto realThis = static_cast<SimulationType*>(this);
        if (dumpLoctypeStat.length()>0) {
            if (locationTypeCounter.size()==0) {
                locationTypeCounter.resize(realThis->locs->generalLocationTypes.rbegin()->first + 1);
                std::ofstream file;
                file.open(dumpLoctypeStat); //open for write
                thrust::copy(locationTypeCounter.begin(), locationTypeCounter.end(), std::ostream_iterator<unsigned>(file, " "));
                file << "\n";
                file.close();
            }
            if (timestamp>0) {
                std::ofstream file;
                file.open(dumpLoctypeStat, std::ios_base::app); //just append
                thrust::copy(locationTypeCounter.begin(), locationTypeCounter.end(), std::ostream_iterator<unsigned>(file, " "));
                file << "\n";
                file.close();
            }
            thrust::fill(locationTypeCounter.begin(),locationTypeCounter.end(),(unsigned)0);
        }
    }

    [[nodiscard]] bool hviActive() const { return hviMode != "off" || hviRotateFraction > 0.0; }
    // Class flags of every agent (empty when the class mode is off); used by the per-episode multiplier of round 10
    thrust::host_vector<uint8_t> getHviClassFlags() {
        initHvi();
        thrust::host_vector<uint8_t> out;
        if (hviMode == "class" && !hviClass.empty()) out = hviClass;
        return out;
    }

    void initHvi() {
        if (hviInitialised) return;
        hviInitialised = true;
        if (!hviActive() && mobilityLog.empty() && hviDump.empty()) return;
        auto realThis = static_cast<SimulationType*>(this);
        const std::size_t n = realThis->agents->PPValues.size();
        thrust::host_vector<unsigned> types = realThis->agents->types;
        thrust::host_vector<typename SimulationType::AgentMeta_t> meta = realThis->agents->agentMetaData;
        std::vector<bool> eligibleType(64, false);
        {
            std::stringstream stream(hviTypes);
            std::string item;
            while (std::getline(stream, item, ',')) {
                unsigned id = static_cast<unsigned>(std::stoul(item));
                if (id >= 1 && id < 64) eligibleType[id - 1] = true;
            }
        }
        std::vector<double> typeScale(64, 1.0);
        std::vector<double> typeScaleWeekend(64, 1.0);
        auto parseScales = [](const std::string& text, std::vector<double>& target) {
            std::stringstream stream(text);
            std::string item;
            while (std::getline(stream, item, ',')) {
                auto colon = item.find(':');
                if (colon == std::string::npos) continue;
                unsigned id = static_cast<unsigned>(std::stoul(item.substr(0, colon)));
                if (id >= 1 && id < 64) target[id - 1] = std::stod(item.substr(colon + 1));
            }
        };
        parseScales(hviScaleByType, typeScale);
        if (hviScaleByTypeWeekend.empty()) typeScaleWeekend = typeScale;
        else parseScales(hviScaleByTypeWeekend, typeScaleWeekend);
        const std::uint64_t base = hviSeed != 0 ? static_cast<std::uint64_t>(hviSeed) : RandomGenerator::getBaseSeed();
        std::vector<float> mult(n, 1.0f);
        std::vector<float> multWeekend(n, 1.0f);
        std::vector<uint8_t> cls(n, 0), rot(n, 0);
        std::vector<double> raw(n, 1.0);
        std::vector<char> eligible(n, 0);
        double sum = 0.0;
        std::size_t count = 0;
        const double logVar = hviShape > 0.0 ? std::log(1.0 + 1.0 / hviShape) : 0.0;
        for (std::size_t i = 0; i < n; ++i) {
            if (!(types[i] < 64 && eligibleType[types[i]] && static_cast<unsigned>(meta[i].getAge()) >= hviMinAge)) continue;
            eligible[i] = 1;
            std::mt19937_64 generator(hviMix(base ^ 0x687669ULL) + hviMix(static_cast<std::uint64_t>(i) + 1ULL));
            double value = 1.0;
            if (hviMode == "gamma") {
                std::gamma_distribution<double> dist(hviShape, 1.0 / hviShape);
                value = dist(generator);
            } else if (hviMode == "lognormal") {
                std::lognormal_distribution<double> dist(-0.5 * logVar, std::sqrt(logVar));
                value = dist(generator);
            } else if (hviMode == "class") {
                std::uniform_real_distribution<double> unit(0.0, 1.0);
                const bool inClass = unit(generator) < hviClassFraction;
                value = inClass ? hviClassFactor : (1.0 - hviClassFraction * hviClassFactor) / (1.0 - hviClassFraction);
                cls[i] = inClass ? 1 : 0;
            }
            raw[i] = value;
            sum += value;
            ++count;
        }
        const double mean = count > 0 ? sum / static_cast<double>(count) : 1.0;
        for (std::size_t i = 0; i < n; ++i) {
            if (!eligible[i]) continue;
            double m = raw[i] / mean;
            if (hviMode != "class" && m > 1.0) cls[i] = 1;
            mult[i] = static_cast<float>(m * typeScale[types[i]]);
            multWeekend[i] = static_cast<float>(m * typeScaleWeekend[types[i]]);
        }
        if (hviRotateFraction > 0.0) {
            for (std::size_t i = 0; i < n; ++i) {
                if (types[i] != 5) continue;  // type id 6, full-time worker (0-based 5)
                std::mt19937_64 generator(hviMix(base ^ 0x726f74ULL) + hviMix(static_cast<std::uint64_t>(i) + 1ULL));
                std::uniform_real_distribution<double> unit(0.0, 1.0);
                if (unit(generator) < hviRotateFraction) rot[i] = 1;
            }
        }
        hviMult = mult;
        hviMultWeekend = multWeekend;
        hviClass = cls;
        hviRotate = rot;
        repeatLeft.assign(n, 0);
        repeatType.assign(n, 0);
        repeatSteps.assign(n, 0);
        if (!hviDump.empty()) {
            std::ofstream out(hviDump.c_str());
            out << "agent,type,age,m,class,rotate,m_weekend\n";
            out.precision(9);
            for (std::size_t i = 0; i < n; ++i)
                out << i << ',' << (types[i] + 1) << ',' << static_cast<unsigned>(meta[i].getAge()) << ',' << mult[i] << ','
                    << static_cast<unsigned>(cls[i]) << ',' << static_cast<unsigned>(rot[i]) << ',' << multWeekend[i] << '\n';
        }
    }

    void applyHviControl(Timehandler& simTime) {
        if (hviControlDay == 0 || hviControlApplied || hviControlMode == "none" || hviMult.empty()) return;
        const unsigned day = simTime.getTimestamp() / simTime.getStepsPerDay();
        if (day < hviControlDay) return;
        hviControlApplied = true;
        thrust::host_vector<float> mult = hviMult;
        thrust::host_vector<float> multWE = hviMultWeekend;
        thrust::host_vector<uint8_t> cls = hviClass;
        if (hviControlMode == "scaleAll") {
            for (std::size_t i = 0; i < multWE.size(); ++i)
                if (multWE[i] != 1.0f || cls[i]) multWE[i] = static_cast<float>(multWE[i] * hviControlParam);
            for (std::size_t i = 0; i < mult.size(); ++i)
                if (mult[i] != 1.0f || cls[i]) mult[i] = static_cast<float>(mult[i] * hviControlParam);
        } else {
            // capTop: the hviControlParam fraction of eligible agents with the largest multiplier gets multiplier 1
            std::vector<float> values;
            for (std::size_t i = 0; i < mult.size(); ++i)
                if (cls[i] || mult[i] != 1.0f) values.push_back(mult[i]);
            if (!values.empty()) {
                std::sort(values.begin(), values.end());
                const std::size_t cut = static_cast<std::size_t>(std::floor((1.0 - hviControlParam) * values.size()));
                const float threshold = values[std::min(cut, values.size() - 1)];
                for (std::size_t i = 0; i < mult.size(); ++i)
                    if ((cls[i] || mult[i] != 1.0f) && mult[i] >= threshold && mult[i] > 1.0f) {
                        mult[i] = 1.0f;
                        multWE[i] = 1.0f;
                    }
            }
        }
        hviMult = mult;
        hviMultWeekend = multWE;
    }

    // ---- per-agent mobility log -------------------------------------------------------------------------------
    // group: 0 home, 1 school, 2 work, 3 discretionary, 4 hospital and institutions, 5 other
    void mobilityStep(Timehandler& simTime) {
        if (mobilityLog.empty()) return;
        auto realThis = static_cast<SimulationType*>(this);
        const std::size_t n = realThis->agents->PPValues.size();
        if (!mobInitialised) {
            mobInitialised = true;
            thrust::host_vector<typename SimulationType::TypeOfLocation_t> lt = realThis->locs->locType;
            thrust::host_vector<float> li = realThis->locs->infectiousness;
            mobLocGroup.assign(lt.size() + 1, 5);
            mobLocL.assign(lt.size() + 1, 0.0f);
            for (std::size_t j = 0; j < lt.size(); ++j) {
                unsigned t = static_cast<unsigned>(lt[j]);
                uint8_t g = 5;
                if (t == home) g = 0;
                else if (t == school || t == classroom) g = 1;
                else if (t == work || t == 13 || t == 44) g = 2;
                else if (RealMovementOps::isDiscretionaryType(t)) g = 3;
                else if (t == 12 || t == 14 || t == 22) g = 4;
                mobLocGroup[j] = g;
                mobLocL[j] = j < li.size() ? li[j] : 0.0f;
            }
            mobPrevLoc.assign(n, 0xffffffffu);
            mobSteps.assign(n * 24, 0);
            mobMoves.assign(n * 2, 0);
            mobVisits.assign(n * 2, 0);
            mobTypeSteps.assign(n * 7, 0);
            mobAllTypeSteps.assign(n * 17, 0);
            mobLocType.assign(lt.size() + 1, 255);
            for (std::size_t j = 0; j < lt.size(); ++j) mobLocType[j] = static_cast<uint8_t>(std::min<unsigned>(static_cast<unsigned>(lt[j]), 254u));
            mobPrevGroup.assign(n, 255);
            mobStateDisc.assign(n * 4, 0);
            mobStateInf.assign(n * 4, 0);
            mobLsteps.assign(n, 0.0);
            mobDistinctDay.assign(n * 2, 0);
            mobDistinctWeek.assign(n, 0);
            mobWeeks.assign(n, 0);
            mobVisitedDay.assign(n, {});
            mobVisitedWeek.assign(n, {});
            mobDays.assign(2, 0);
        }
        const unsigned stepsPerDay = simTime.getStepsPerDay();
        const unsigned timestamp = simTime.getTimestamp();
        const unsigned day = timestamp / stepsPerDay;
        const bool weekend = (static_cast<unsigned>(simTime.getDay()) >= 5);
        const unsigned dt = weekend ? 1 : 0;
        thrust::host_vector<unsigned> loc = realThis->agents->location;
        thrust::device_vector<uint8_t> codeDev(n);
        thrust::transform(realThis->agents->PPValues.begin(), realThis->agents->PPValues.end(), codeDev.begin(),
            [] HD(const typename SimulationType::PPState_t& p) -> uint8_t {
                return static_cast<uint8_t>(static_cast<unsigned>(p.getWBState()) | (p.isInfectious() ? 8u : 0u));
            });
        thrust::host_vector<uint8_t> code = codeDev;
        thrust::host_vector<uint8_t> roleHost = agentRole;
        for (std::size_t i = 0; i < n; ++i) {
            unsigned c = code[i];
            unsigned wb = c & 7u;
            if (wb >= 4) continue;  // dead
            unsigned l = loc[i];
            if (l >= mobLocGroup.size()) continue;
            unsigned pg = mobLocGroup[l];
            unsigned role = roleHost[i];
            unsigned g = 5;
            if (role == home) g = 0;
            else if (role == school || role == classroom) g = 1;
            else if (role == work || role == 13) g = 2;
            else if (RealMovementOps::isDiscretionaryType(role)) g = 3;
            else if (role == 12 || role == 14 || role == 22) g = 4;
            {
                const int hs = hptSlot(mobLocType[l]);
                if (hs >= 0) mobAllTypeSteps[i * 17 + hs]++;
            }
            mobSteps[i * 24 + dt * 12 + g]++;
            mobSteps[i * 24 + dt * 12 + 6 + pg]++;
            if (g == 3) {
                mobStateDisc[i * 4 + wb]++;
                mobLsteps[i] += mobLocL[l];
                const unsigned pt = mobLocType[l];
                const int slot = pt == 1 ? 0 : pt == 5 ? 1 : pt == 6 ? 2 : pt == 7 ? 3 : pt == 8 ? 4 : pt == 9 ? 5 : pt == 10 ? 6 : -1;
                if (slot >= 0) mobTypeSteps[i * 7 + slot]++;
            }
            if (c & 8u) mobStateInf[i * 4 + wb]++;
            if (g == 3 && (l != mobPrevLoc[i] || mobPrevGroup[i] != 3)) mobVisits[i * 2 + dt]++;
            mobPrevGroup[i] = static_cast<uint8_t>(g);
            if (l != mobPrevLoc[i]) {
                if (mobPrevLoc[i] != 0xffffffffu) mobMoves[i * 2 + dt]++;
                if (g == 3) {
                    auto& vd = mobVisitedDay[i];
                    if (std::find(vd.begin(), vd.end(), l) == vd.end()) vd.push_back(l);
                    auto& vw = mobVisitedWeek[i];
                    if (std::find(vw.begin(), vw.end(), l) == vw.end()) vw.push_back(l);
                }
                mobPrevLoc[i] = l;
            }
        }
        if (simTime.getStepsUntilMidnight() == 1) {
            mobDays[dt]++;
            for (std::size_t i = 0; i < n; ++i) {
                mobDistinctDay[i * 2 + dt] += static_cast<unsigned>(mobVisitedDay[i].size());
                mobVisitedDay[i].clear();
            }
            if (static_cast<unsigned>(simTime.getDay()) == 6) {
                for (std::size_t i = 0; i < n; ++i) {
                    mobDistinctWeek[i] += static_cast<unsigned>(mobVisitedWeek[i].size());
                    mobWeeks[i]++;
                    mobVisitedWeek[i].clear();
                }
            }
            writeMobilityLog(simTime);
        }
        (void)day;
    }

    void writeMobilityLog(Timehandler& simTime) {
        auto realThis = static_cast<SimulationType*>(this);
        const std::size_t n = realThis->agents->PPValues.size();
        thrust::host_vector<unsigned> types = realThis->agents->types;
        thrust::host_vector<typename SimulationType::AgentMeta_t> meta = realThis->agents->agentMetaData;
        thrust::host_vector<float> mult;
        if (!hviMult.empty()) mult = hviMult;
        std::ofstream out(mobilityLog.c_str());
        const double hoursPerStep = static_cast<double>(simTime.getTimeStep()) / 60.0;
        out << "agent,type,age,m,days_weekday,days_weekend,moves_weekday,moves_weekend,visits_wd,visits_we";
        const char* groups[6] = {"home", "school", "work", "disc", "inst", "other"};
        for (int d = 0; d < 2; ++d)
            for (int k = 0; k < 2; ++k)
                for (int g = 0; g < 6; ++g) out << ",h_" << (d == 0 ? "wd_" : "we_") << (k == 0 ? "role_" : "phys_") << groups[g];
        out << ",Lhours_disc,hdisc_W,hdisc_N,hdisc_M,hdisc_S,hinf_W,hinf_N,hinf_M,hinf_S,distinct_day_wd,distinct_day_we,distinct_week,hdt_1,hdt_5,hdt_6,hdt_7,hdt_8,hdt_9,hdt_10,hpt_1,hpt_2,hpt_3,hpt_4,hpt_5,hpt_6,hpt_7,hpt_8,hpt_9,hpt_10,hpt_11,hpt_12,hpt_13,hpt_14,hpt_22,hpt_33,hpt_44\n";
        out.precision(6);
        for (std::size_t i = 0; i < n; ++i) {
            out << i << ',' << (types[i] + 1) << ',' << static_cast<unsigned>(meta[i].getAge()) << ',' << (mult.empty() ? 1.0f : mult[i]) << ','
                << mobDays[0] << ',' << mobDays[1] << ',' << mobMoves[i * 2] << ',' << mobMoves[i * 2 + 1] << ',' << mobVisits[i * 2] << ',' << mobVisits[i * 2 + 1];
            for (int k = 0; k < 24; ++k) out << ',' << mobSteps[i * 24 + k] * hoursPerStep;
            out << ',' << mobLsteps[i] * hoursPerStep;
            for (int w = 0; w < 4; ++w) out << ',' << mobStateDisc[i * 4 + w] * hoursPerStep;
            for (int w = 0; w < 4; ++w) out << ',' << mobStateInf[i * 4 + w] * hoursPerStep;
            out << ',' << (mobDays[0] ? static_cast<double>(mobDistinctDay[i * 2]) / mobDays[0] : 0.0) << ','
                << (mobDays[1] ? static_cast<double>(mobDistinctDay[i * 2 + 1]) / mobDays[1] : 0.0) << ','
                << (mobWeeks[i] ? static_cast<double>(mobDistinctWeek[i]) / mobWeeks[i] : 0.0);
            for (int k = 0; k < 7; ++k) out << ',' << mobTypeSteps[i * 7 + k] * hoursPerStep;
            for (int k = 0; k < 17; ++k) out << ',' << mobAllTypeSteps[i * 17 + k] * hoursPerStep;
            out << '\n';
        }
    }

    void planLocations(Timehandler simTime, unsigned timeStep) {
        PROFILE_FUNCTION();
        auto realThis = static_cast<SimulationType*>(this);
        thrust::device_vector<unsigned>& agentLocations = realThis->agents->location;
        unsigned numberOfAgents = agentLocations.size();
        unsigned numberOfLocations = realThis->locs->locationListOffsets.size() - 1;
        unsigned timestamp = simTime.getTimestamp();
        if (stepsUntilMove.size() == 0) {
            stepsUntilMove.resize(numberOfAgents);
            noWorkLoc.resize(numberOfLocations);
            noWorkAgent.resize(numberOfAgents);
        }
        if (curfewTimeConverted == false) {
            curfewBegin = curfewBegin / timeStep;
            curfewEnd = curfewEnd / timeStep;
            curfewTimeConverted = true;
        }
        // If curfew, noone moves before curfew ends
        thrust::fill(stepsUntilMove.begin(), stepsUntilMove.end(), curfewEnd);
        thrust::fill(realThis->agents->stayedHome.begin(), realThis->agents->stayedHome.end(), true);
        initHvi();
        if (!repeatLeft.empty()) thrust::fill(repeatLeft.begin(), repeatLeft.end(), (uint8_t)0u);

        // For each agent that is under 14 years, check if quarantined or school closed, if so flag home as noWork
        thrust::fill(noWorkLoc.begin(), noWorkLoc.end(), RealMovementOps::noWorkNoRequest);
        thrust::fill(noWorkAgent.begin(), noWorkAgent.end(), (uint8_t)0u);
        unsigned* noWorkLocPtr = thrust::raw_pointer_cast(noWorkLoc.data());
        uint8_t* noWorkAgentPtr = thrust::raw_pointer_cast(noWorkAgent.data());
        thrust::device_vector<typename SimulationType::AgentMeta_t>& agentMetaData = realThis->agents->agentMetaData;
        typename SimulationType::AgentMeta_t* agentMetaDataPtr = thrust::raw_pointer_cast(agentMetaData.data());
        thrust::device_vector<bool>& quarantined = realThis->agents->quarantined;
        bool* quarantinedPtr = thrust::raw_pointer_cast(quarantined.data());
        thrust::device_vector<bool>& locationStates = realThis->locs->states;
        bool* locationStatesPtr = thrust::raw_pointer_cast(locationStates.data());
        thrust::device_vector<unsigned>& closedUntil = realThis->locs->closedUntil;
        unsigned* closedUntilPtr = thrust::raw_pointer_cast(closedUntil.data());
        thrust::device_vector<unsigned long>& locationOffset = realThis->agents->locationOffset;
        unsigned long* locationOffsetPtr = thrust::raw_pointer_cast(locationOffset.data());
        thrust::device_vector<unsigned>& possibleLocations = realThis->agents->possibleLocations;
        unsigned* possibleLocationsPtr = thrust::raw_pointer_cast(possibleLocations.data());
        thrust::device_vector<unsigned>& possibleTypes = realThis->agents->possibleTypes;
        unsigned* possibleTypesPtr = thrust::raw_pointer_cast(possibleTypes.data());
        thrust::device_vector<typename SimulationType::PPState_t>& agentStates = realThis->agents->PPValues;
        typename SimulationType::PPState_t* agentStatesPtr = thrust::raw_pointer_cast(agentStates.data());
        thrust::device_vector<AgentStats>& agentStats = realThis->agents->agentStats;
        AgentStats* agentStatsPtr = thrust::raw_pointer_cast(agentStats.data());
        thrust::device_vector<typename SimulationType::TypeOfLocation_t>& locationTypes = realThis->locs->locType;
        thrust::device_vector<unsigned>& locationQuarantineUntil = realThis->locs->quarantineUntil;
        unsigned* locationQuarantineUntilPtr = thrust::raw_pointer_cast(locationQuarantineUntil.data());

        // if quarantinePolicy >3, check if more than 1 classrrom in a school is quarantined, if so, quarantine the schooland
        // all classrooms
        if (quarantinePolicy > 3) {
            thrust::device_vector<unsigned>& schools = realThis->locs->schools;
            unsigned* schoolsPtr = thrust::raw_pointer_cast(schools.data());
            thrust::device_vector<unsigned>& classrooms = realThis->locs->classrooms;
            unsigned* classroomsPtr = thrust::raw_pointer_cast(classrooms.data());
            thrust::device_vector<unsigned>& classroomOffsets = realThis->locs->classroomOffsets;
            unsigned* classroomOffsetsPtr = thrust::raw_pointer_cast(classroomOffsets.data());
            unsigned numSchools = schools.size();

#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_OMP
#pragma omp parallel for
            for (unsigned i = 0; i < numSchools; i++) {
                RealMovementOps::checkSchoolQuarantine(
                    i, schoolsPtr, classroomsPtr, classroomOffsetsPtr, locationQuarantineUntilPtr, timestamp);
            }
#elif THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
            RealMovementOps::checkSchoolQuarantineDriver<<<(numSchools - 1) / 256 + 1, 256>>>(
                numSchools, schoolsPtr, classroomsPtr, classroomOffsetsPtr, locationQuarantineUntilPtr, timestamp);
            cudaDeviceSynchronize();
#endif
        }

        // put all workers of quarantined workpalces into quarantine, and clear workplace quarantine
        // put all attendees of quarantined classroom into quarantine, clear classroom quarantine, close classroom
        if (quarantinePolicy > 2) {
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_OMP
#pragma omp parallel for
            for (unsigned i = 0; i < numberOfAgents; i++) {
                RealMovementOps::checkSchoolWorkQuarantine(i,
                    agentStatsPtr,
                    agentStatesPtr,
                    quarantinedPtr,
                    locationQuarantineUntilPtr,
                    locationOffsetPtr,
                    possibleLocationsPtr,
                    possibleTypesPtr,
                    home,
                    work,
                    school,
                    classroom,
                    timestamp,
                    timeStep,
                    tracked);
            }
#elif THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
            RealMovementOps::checkSchoolWorkQuarantineDriver<<<(numberOfAgents - 1) / 256 + 1, 256>>>(numberOfAgents,
                agentStatsPtr,
                agentStatesPtr,
                quarantinedPtr,
                locationQuarantineUntilPtr,
                locationOffsetPtr,
                possibleLocationsPtr,
                possibleTypesPtr,
                home,
                work,
                school,
                classroom,
                timestamp,
                timeStep,
                tracked);
            cudaDeviceSynchronize();
#endif
            unsigned schoolType = school;
            unsigned classroomType = classroom;
            unsigned workType = work;
            // Clear quarantine flags, set closedUntil instead for schools/classrooms
            thrust::for_each(thrust::make_zip_iterator(thrust::make_tuple(
                                 closedUntil.begin(), locationQuarantineUntil.begin(), locationTypes.begin())),
                thrust::make_zip_iterator(
                    thrust::make_tuple(closedUntil.end(), locationQuarantineUntil.end(), locationTypes.end())),
                [schoolType, classroomType, workType, timestamp] HD(
                    thrust::tuple<unsigned&, unsigned&, typename SimulationType::TypeOfLocation_t&> tup) {
                    if (thrust::get<1>(tup) > timestamp
                        && (thrust::get<2>(tup) == schoolType || thrust::get<2>(tup) == classroomType)) {
                        thrust::get<0>(tup) = thrust::get<1>(tup);
                        thrust::get<1>(tup) = 0;
                    } else if (thrust::get<1>(tup) > timestamp && thrust::get<2>(tup) == workType) {
                        thrust::get<1>(tup) = 0;
                    }
                });
        }

        // Check if minors are alone at home, flag home
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_OMP
#pragma omp parallel for
        for (unsigned i = 0; i < numberOfAgents; i++) {
            RealMovementOps::checkUnderageAtHome(i,
                noWorkLocPtr,
                agentMetaDataPtr,
                quarantinedPtr,
                locationStatesPtr,
                closedUntilPtr,
                locationOffsetPtr,
                possibleLocationsPtr,
                possibleTypesPtr,
                home,
                school,
                classroom,
                timestamp,
                schoolAgeRestriction);
        }
#elif THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
        RealMovementOps::checkUnderageAtHomeDriver<<<(numberOfAgents - 1) / 256 + 1, 256>>>(numberOfAgents,
            noWorkLocPtr,
            agentMetaDataPtr,
            quarantinedPtr,
            locationStatesPtr,
            closedUntilPtr,
            locationOffsetPtr,
            possibleLocationsPtr,
            possibleTypesPtr,
            home,
            school,
            classroom,
            timestamp,
            schoolAgeRestriction);
        cudaDeviceSynchronize();
#endif

        // For each adult working agent (25-65), if home is flagged, at least one adult is flagged as not working that day
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_OMP
#pragma omp parallel for
        for (unsigned i = 0; i < numberOfAgents; i++) {
            RealMovementOps::setNoWorkToday(i,
                noWorkLocPtr,
                agentMetaDataPtr,
                locationOffsetPtr,
                possibleLocationsPtr,
                possibleTypesPtr,
                home);
        }
#elif THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
        RealMovementOps::setNoWorkTodayDriver<<<(numberOfAgents - 1) / 256 + 1, 256>>>(numberOfAgents,
            noWorkLocPtr,
            agentMetaDataPtr,
            locationOffsetPtr,
            possibleLocationsPtr,
            possibleTypesPtr,
            home);
        cudaDeviceSynchronize();
#endif
        // Commit the deterministic selection for one stay-at-home adult per flagged household.
#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_OMP
#pragma omp parallel for
        for (unsigned i = 0; i < numberOfLocations; i++) {
            RealMovementOps::finalizeNoWorkToday(i, numberOfAgents, noWorkLocPtr, noWorkAgentPtr);
        }
#elif THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
        RealMovementOps::finalizeNoWorkTodayDriver<<<(numberOfLocations - 1) / 256 + 1, 256>>>(
            numberOfLocations, numberOfAgents, noWorkLocPtr, noWorkAgentPtr);
        cudaDeviceSynchronize();
#endif
        //dumpLoctypeStatNow(timestamp);
    }


    void movement(Timehandler simTime, unsigned timeStep) {
        PROFILE_FUNCTION();
        auto realThis = static_cast<SimulationType*>(this);

        RealMovementOps::MovementArguments<typename SimulationType::PPState_t,
            typename SimulationType::AgentMeta_t,
            typename SimulationType::TypeOfLocation_t>
            a;

        a.quarantinePolicy = quarantinePolicy;
        a.quarantineLength = quarantineLength;
        a.tracked = this->tracked;
        a.hospitalType = hospital;
        a.homeType = home;
        a.publicPlaceType = publicSpace;
        a.doctorType = doctor;
        a.timeStep = timeStep;
        a.simTime = TimeDay(simTime);
        a.cemeteryLoc = cemeteryLoc;
        a.schoolType = school;
        a.classroomType = classroom;
        a.workType = work;
        a.enableCurfew = enableCurfew;
        a.curfewBegin = curfewBegin;
        a.curfewEnd = curfewEnd;
        a.schoolAgeRestriction = schoolAgeRestriction;
        a.quarantineImmuneActive = quarantineImmuneActive;
        a.lockdownNonvaccActive = lockdownNonvaccActive;
        initHvi();
        applyHviControl(simTime);
        if (hviActive() && !hviMult.empty()) {
            a.hviMultPtr = (static_cast<unsigned>(simTime.getDay()) >= 5 || holidayModeActive) ? thrust::raw_pointer_cast(hviMultWeekend.data())
                                                                                            : thrust::raw_pointer_cast(hviMult.data());
            a.hviClassPtr = thrust::raw_pointer_cast(hviClass.data());
            a.hviRotatePtr = hviRotateFraction > 0.0 ? thrust::raw_pointer_cast(hviRotate.data()) : nullptr;
            a.repeatLeftPtr = thrust::raw_pointer_cast(repeatLeft.data());
            a.repeatTypePtr = thrust::raw_pointer_cast(repeatType.data());
            a.repeatStepsPtr = thrust::raw_pointer_cast(repeatSteps.data());
            unsigned mask = 0;
            for (char ch : hviStates) {
                if (ch == 'W') mask |= 1u;
                else if (ch == 'N') mask |= 2u;
                else if (ch == 'M') mask |= 4u;
                else if (ch == 'S') mask |= 8u;
            }
            a.hviStatesMask = mask;
            a.hviInfectiousOnly = (hviWhen == "infectious");
            a.hviVisitsFactor = hviVisitsFactor;
            a.hviLeverDuration = (hviLever == "duration");
            a.hviTilt = static_cast<float>(hviTilt);
            unsigned highMask = 0;
            {
                std::stringstream stream(hviHighTypes);
                std::string item;
                while (std::getline(stream, item, ',')) {
                    unsigned id = static_cast<unsigned>(std::stoul(item));
                    if (id < 32) highMask |= (1u << id);
                }
            }
            a.hviHighMask = highMask;
            a.hviOthersHighScale = static_cast<float>(hviOthersHighScale);
            a.hviIsolationBreak = hviIsolationBreak != 0;
        }
        if (!mobilityLog.empty()) {
            if (agentRole.empty()) agentRole.assign(realThis->agents->PPValues.size(), static_cast<uint8_t>(home));
            a.rolePtr = thrust::raw_pointer_cast(agentRole.data());
        }

        // Location-based data
        thrust::device_vector<unsigned>& locationAgentList = realThis->locs->locationAgentList;
        unsigned* locationAgentListPtr = thrust::raw_pointer_cast(locationAgentList.data());
        thrust::device_vector<unsigned>& locationListOffsets = realThis->locs->locationListOffsets;
        unsigned* locationListOffsetsPtr = thrust::raw_pointer_cast(locationListOffsets.data());
        thrust::device_vector<unsigned>& locationIdsOfAgents = realThis->locs->locationIdsOfAgents;
        unsigned* locationIdsOfAgentsPtr = thrust::raw_pointer_cast(locationIdsOfAgents.data());
        thrust::device_vector<bool>& locationStates = realThis->locs->states;
        a.locationStatesPtr = thrust::raw_pointer_cast(locationStates.data());
        thrust::device_vector<unsigned>& closedUntil = realThis->locs->closedUntil;
        a.closedUntilPtr = thrust::raw_pointer_cast(closedUntil.data());
        thrust::device_vector<unsigned>& locationCapacities = realThis->locs->capacity;
        a.locationCapacitiesPtr = thrust::raw_pointer_cast(locationCapacities.data());
        thrust::device_vector<unsigned>& locationQuarantineUntil = realThis->locs->quarantineUntil;
        a.locationQuarantineUntilPtr = thrust::raw_pointer_cast(locationQuarantineUntil.data());
        thrust::device_vector<typename SimulationType::TypeOfLocation_t>& locationTypes = realThis->locs->locType;
        a.locationTypePtr = thrust::raw_pointer_cast(locationTypes.data());
        a.essentialLocPtr = thrust::raw_pointer_cast(realThis->locs->essential.data());

        // Agent-based data
        thrust::device_vector<unsigned>& agentLocations = realThis->agents->location;
        a.agentLocationsPtr = thrust::raw_pointer_cast(agentLocations.data());
        thrust::device_vector<unsigned>& agentTypes = realThis->agents->types;
        a.agentTypesPtr = thrust::raw_pointer_cast(agentTypes.data());
        thrust::device_vector<typename SimulationType::PPState_t>& agentStates = realThis->agents->PPValues;
        a.agentStatesPtr = thrust::raw_pointer_cast(agentStates.data());
        thrust::device_vector<typename SimulationType::AgentMeta_t>& agentMetaData = realThis->agents->agentMetaData;
        a.agentMetaDataPtr = thrust::raw_pointer_cast(agentMetaData.data());
        thrust::device_vector<bool>& diagnosed = realThis->agents->diagnosed;
        a.diagnosedPtr = thrust::raw_pointer_cast(diagnosed.data());
        thrust::device_vector<bool>& stayedHome = realThis->agents->stayedHome;
        a.stayedHomePtr = thrust::raw_pointer_cast(stayedHome.data());
        thrust::device_vector<bool>& quarantined = realThis->agents->quarantined;
        a.quarantinedPtr = thrust::raw_pointer_cast(quarantined.data());
        thrust::device_vector<AgentStats>& agentStats = realThis->agents->agentStats;
        a.agentStatsPtr = thrust::raw_pointer_cast(agentStats.data());
        a.stepsUntilMovePtr = thrust::raw_pointer_cast(this->stepsUntilMove.data());
        a.noWorkAgentPtr = thrust::raw_pointer_cast(noWorkAgent.data());

        // Arrays storing actual location IDs for each agent, for each location
        // type
        thrust::device_vector<unsigned long>& locationOffset = realThis->agents->locationOffset;
        a.locationOffsetPtr = thrust::raw_pointer_cast(locationOffset.data());
        thrust::device_vector<unsigned>& possibleLocations = realThis->agents->possibleLocations;
        a.possibleLocationsPtr = thrust::raw_pointer_cast(possibleLocations.data());
        thrust::device_vector<unsigned>& possibleTypes = realThis->agents->possibleTypes;
        a.possibleTypesPtr = thrust::raw_pointer_cast(possibleTypes.data());

        // Arrays storing movement behaviour with general locationTypes - for
        // each agent type, WB state, and day
        thrust::device_vector<unsigned>& eventOffset = realThis->agents->agentTypes.eventOffset;
        a.eventOffsetPtr = thrust::raw_pointer_cast(eventOffset.data());
        thrust::device_vector<AgentTypeList::Event>& events = realThis->agents->agentTypes.events;
        a.eventsPtr = thrust::raw_pointer_cast(events.data());


        unsigned numberOfAgents = agentLocations.size();
        unsigned numberOfLocations = locationListOffsets.size() - 1;

        a.day = simTime.getDay();
        if (holidayModeActive) { a.day = Days::SUNDAY; }
        a.timestamp = simTime.getTimestamp();

#if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_OMP
#pragma omp parallel for
        for (unsigned i = 0; i < numberOfAgents; i++) { RealMovementOps::doMovement(i, a); }
#elif THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
        RealMovementOps::doMovementDriver<<<(numberOfAgents - 1) / 256 + 1, 256>>>(numberOfAgents, a);
        cudaDeviceSynchronize();
#endif
        Util::updatePerLocationAgentLists(agentLocations, locationIdsOfAgents, locationAgentList, locationListOffsets);
        mobilityStep(simTime);

        if (dumpLocationAgentList.length()>0) {
            std::ofstream file;
            file.open(dumpLocationAgentList + "/locationList"+std::to_string(a.timestamp)+".txt");
            file << locationListOffsets.size()-1 << "\n";
            thrust::copy(locationListOffsets.begin(), locationListOffsets.end(), std::ostream_iterator<unsigned>(file, " "));
            file << "\n";
            thrust::copy(locationAgentList.begin(), locationAgentList.end(), std::ostream_iterator<unsigned>(file, " "));
            file << "\n";
            file.close();
        }

        if (dumpLoctypeStat.length()>0) {
            dumpLoctypeStatNow(simTime.getTimestamp());
            typename SimulationType::TypeOfLocation_t *locationTypePtr = thrust::raw_pointer_cast(locationTypes.data());
            unsigned* locationListOffsetsPtr = thrust::raw_pointer_cast(locationListOffsets.data());
            unsigned numLocTypes = realThis->locs->generalLocationTypes.rbegin()->first + 1;
            unsigned* locationTypeCounterPtr = thrust::raw_pointer_cast(locationTypeCounter.data());
            #if THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_OMP
            std::cout << "Error, dumpLoctypeStat not implemented for CPU\n";
            exit(1);
            #elif THRUST_DEVICE_SYSTEM == THRUST_DEVICE_SYSTEM_CUDA
            RealMovementOps::countByType<<<(numberOfLocations-1)/256+1,256>>>(numberOfLocations, numLocTypes, locationTypePtr, locationListOffsetsPtr, locationTypeCounterPtr);
            cudaDeviceSynchronize();
            #endif
        }
    }
};
