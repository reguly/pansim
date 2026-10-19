# 59a: review of note 58 and what round 11 will do

19 October 2026. Written before the round-11 arms were run, so that the choices below are on record ahead of the results. Results go to `59_round11_results.md`.

## What note 58 asks for

Redo the round-10 world comparison with the worlds matched on the **likelihood** k (about 0.35) instead of the moment k, report the observed zero and 80% shares rather than negative-binomial projections to mean 1.4, and score six registered predictions (a) to (f). Then R11-2 (class membership redrawn per infection) and R11-3 (cluster composition from existing traces).

I accept the change of primary estimator. It is the right one: the moment estimator is dominated by the largest observation, so two distributions with the same moment k can have visibly different bodies, which is what round 10 ran into.

## Decisions taken before the runs

**1. World 2a starting shape: 0.70, not the 0.73 in the note.**

Note 58 describes 0.73 as a log interpolation between (shape 1, likelihood k 0.435) and (shape 0.5, likelihood k 0.284). Interpolating on the log of both quantities gives

- ln 0.435 = -0.832, ln 0.284 = -1.260, ln 0.35 = -1.050
- fraction of the interval = (-1.050 + 0.832) / (-1.260 + 0.832) = 0.509
- ln shape = 0.509 x ln 0.5 = -0.353, shape = **0.703**

0.73 is what you get interpolating linearly in k rather than in log k. The difference is small (predicted likelihood k 0.358 at shape 0.73 against 0.350 at 0.703, both inside the 10% window the note allows), so this is not a correction of substance, only of arithmetic. I use 0.70.

**2. World 2b starting shape: 0.58, not the 0.46 in the note.**

The note extrapolates from shapes 3, 2, 1 at lambda 10 (likelihood k 0.812, 0.702, 0.510), which gives a local log-log slope of 0.463 between shapes 1 and 2 and so shape 0.44 to 0.46 for k = 0.35. But the slope is not constant: at lambda 30 the slope between shapes 1 and 2 is 0.416 and between shapes 1 and 0.5 it is 0.618, that is 1.49 times steeper below shape 1. Applying the same factor to lambda 10 gives a slope of about 0.69 below shape 1, hence

- ln shape = (ln 0.35 - ln 0.510) / 0.69 = -0.546, shape = **0.58**

If the note's 0.46 were used and the curvature is as at lambda 30, the arm would land near k = 0.30, outside the 10% window, and cost an extra tuning round. I use 0.58 and will report what it actually gives. This is the kind of deviation the note's "expect more tuning rounds" anticipates; I am spending the knowledge of lambda 30's curvature instead of a run.

**3. World 1 is reused unchanged**, as the note instructs: the round-10 arm `w1_sh0.32`, likelihood k 0.357, already inside the window. No new run; its statistics are recomputed from the existing traces with the two additions the note asks for (number of infectors in the top 1%, and the negative binomial evaluated at the likelihood k and the arm's own mean).

**4. World 3 is not tuned.** The lowest likelihood k the closed-group events have reached in any arm run so far is 1.199 (round 10, rate 0.034, group size 30, factor 3000); round 6 reached 1.8. Both are a factor of three above the target. I will report this and say the world cannot be matched, as instructed, and will not spend a run on it.

**5. R11-2 is dropped as specified, and replaced by a free test of the same hypothesis.**

The note says to drop it "if that needs more than a flag". It does. Class membership is drawn once per agent in `initHvi()` on the host, from a generator keyed by the agent index, and it is then fixed for the whole run: it sets the agent's mobility multiplier (`hviMult`), the weekend multiplier, and the venue tilt. Redrawing it at each infection means writing into the movement policy's device arrays from the infection kernel, that is a cross-policy device-side change plus a rebuild and a fresh byte-identity check. That is not a flag.

Instead I will test the same hypothesis from data that costs nothing extra: **decompose the repeat-infection correlation by class membership.** The repeat-infection arm dumps each agent's class flag, so the correlation between an agent's first and second offspring count can be computed separately within class members and within non-members, as well as over all pairs. If the correlation is carried by the persistent class, the overall correlation will be positive while both within-group correlations are near zero. If it survives inside the groups, something else is persistent (household, home location, age), which is exactly the alternative note 58 raises. This answers the question note 58 asks; it does not reproduce the counterfactual run, and I will not claim that it does.

**6. Order and budget.** World 2a tuning, then world 1 and world 2b, then R11-3 (no new runs), then the repeat-infection arm for world 2a and its class decomposition. The world-1 repeat-infection arm from round 10 is at the same shape (0.32) and is reused, so only world 2a needs a new one.

## Points checked in note 58

- Prediction (f) says the pupil share in the top 1% of world 2a stays at 0% "by construction". That is right, and the construction is worth stating precisely: the high-volume class is restricted to agent types 4 to 8 and to ages 15 and over (`--hviTypes 4,5,6,7,8`, `--hviMinAge 15` by default), so school-age agents can never be class members, and at lambda 30 the top 1% is essentially all class members. The prediction therefore tests nothing about the model; it is a label for a structural feature. I will score it as the note asks and say so.
- Prediction (b) quotes "8.8 and 15.5%" for round 10. Those are world 2's values (the round-9 gate cell at shape 1). The closest round-10 arm to world 2a, R10-4 (lambda 30, shape 0.5), gave 9.72 distinct venues and 14.1%. Either way the thresholds of 7 and 25% are the test.
- The note's statement that the R10-4 cell reached the real pattern (likelihood k 0.284, zero 56.9%, 80% share 17.9%) matches `56_r102_r104_summary.csv`.

## Standing constraints

No edits to `locations1.json`, `agents2.json`, `locations3.json` or `agents4.json`; the lambda 30 and lambda 10 venue files are separate copies built by `build_r8_inputs.py`. 12 replicates on seeds 77001 to 77012, day 28 within 3% of 6,211.25, binary `build_r10/panSim` (no code change this round, so no new byte-identity check is needed; the binary is the one whose T1 check passed in round 10).

Still outstanding from earlier rounds: `47_s1_summary_BAD_upload_ignore.csv` and `50_r80_hours_by_type_BAD_upload_ignore.csv` are superseded duplicates I cannot delete; please trash them.
