#!/bin/bash
cd /home/ireguly/pansim
while kill -0 29706 2>/dev/null; do sleep 30; done
export PANSIM_JOBS=3
PANSIM_BIN=/home/ireguly/pansim/build_r67/panSim python3 superspreader/study/run_round6.py r67 > superspreader/study/results/round6_r67.log 2>&1
