#!/bin/bash
cd /home/ireguly/pansim
export PANSIM_JOBS=3
export PANSIM_BIN=/home/ireguly/pansim/build_r7/panSim
for t in s2 s3 s4 s5 s5_pairs; do
  python3 superspreader/study/run_round7.py $t > superspreader/study/results/round7_$t.log 2>&1
done
