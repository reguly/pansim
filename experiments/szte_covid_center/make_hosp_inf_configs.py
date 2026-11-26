"""Progression configs with a higher infectiousness for hospitalised COVID patients (hospInf test, README.md).

The validated runs use inputConfigFiles/progressions_Jun17_tune/transition_config.json, where the hospitalised
states I5_h and I6_h have infectious = 0.1 (a tenth of a symptomatic case at home). This writes copies with
0.3, 0.5, 0.7 and 1.0 next to it, so the transition matrices they name resolve to the same files (panSim reads them
relative to the config's directory). Nothing else changes; R_h stays at 0.

Run from anywhere:  python make_hosp_inf_configs.py
Use in a scenario:  --progression inputConfigFiles/progressions_Jun17_tune/transition_config_hospInf05.json
"""
import json
from pathlib import Path

DIR = Path(__file__).resolve().parents[2] / "inputConfigFiles/progressions_Jun17_tune"
SRC = DIR / "transition_config.json"
LEVELS = {"03": 0.3, "05": 0.5, "07": 0.7, "10": 1.0}
STATES = ("I5_h", "I6_h")


def main():
    base = json.loads(SRC.read_text())
    for tag, value in LEVELS.items():
        cfg = json.loads(json.dumps(base))
        hit = [s for s in cfg["states"] if s["stateName"] in STATES]
        assert len(hit) == len(STATES), f"{STATES} not all found in {SRC}"
        for s in hit:
            s["infectious"] = value
        out = DIR / f"transition_config_hospInf{tag}.json"
        out.write_text(json.dumps(cfg, indent=2) + "\n")
        print(f"{out.relative_to(DIR.parents[1])}: {', '.join(STATES)} infectious = {value}")


if __name__ == "__main__":
    main()
