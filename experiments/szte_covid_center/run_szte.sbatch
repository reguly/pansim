#!/bin/bash
#SBATCH --job-name=szte_covid
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=16
#SBATCH --time=12:00:00
#SBATCH --output=szte_covid_%j.log

# SZTE COVID-centre batch (README.md): every scenario in scenarios.yaml, 20 runs x 52 weeks,
# ~1.3 h per scenario. If the job hits the time limit, submit it again: scenarios that already
# have all_runs.tsv are skipped. Submit with: sbatch experiments/szte_covid_center/run_szte.sbatch

module load gpu/cuda/11.4
cd ~/PanSim/pansim
echo "commit $(git rev-parse --short HEAD), $(date -Is)"
RESULTS_ROOT=experiments/szte_covid_center/results SCENARIOS_FILE=experiments/szte_covid_center/scenarios.yaml ./experiments/hcw_interventions/run_scenarios.sh
