#!/bin/bash
# Runs the remaining round-6 tasks one after another once the R6-1 job has finished.
cd /home/ireguly/pansim
while pgrep -f "run_round6.py r61" > /dev/null; do sleep 30; done
export PANSIM_JOBS=3
python3 superspreader/study/run_round6.py r64 > superspreader/study/results/round6_r64.log 2>&1
python3 superspreader/study/run_round6.py r65 > superspreader/study/results/round6_r65.log 2>&1
PANSIM_BIN=/home/ireguly/pansim/build_r62/panSim python3 superspreader/study/run_round6.py r62 > superspreader/study/results/round6_r62.log 2>&1
python3 superspreader/study/run_round6.py r66 > superspreader/study/results/round6_r66.log 2>&1
