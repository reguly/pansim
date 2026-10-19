#!/bin/bash
# Order after R6-5 has finished its four arms: refine R6-5, then R6-2, R6-6, R6-7.
cd /home/ireguly/pansim
while kill -0 42920 2>/dev/null; do sleep 20; done
export PANSIM_JOBS=3
python3 superspreader/study/run_round6.py r65_refine > superspreader/study/results/round6_r65_refine.log 2>&1
PANSIM_BIN=/home/ireguly/pansim/build_r62/panSim python3 superspreader/study/run_round6.py r62 > superspreader/study/results/round6_r62.log 2>&1
python3 superspreader/study/run_round6.py r66 > superspreader/study/results/round6_r66.log 2>&1
PANSIM_BIN=/home/ireguly/pansim/build_r67/panSim python3 superspreader/study/run_round6.py r67 > superspreader/study/results/round6_r67.log 2>&1
