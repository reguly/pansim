# 59 upload index (round 11)

19 October 2026. Every file is in `superspreader/` with Unix newlines (`\n`) and under 1 MB.

| File | Bytes (local) | Content |
|---|---|---|
| 59_round11_results.md | 28353 | main note: headline, deviations, R11-1 worlds matched on likelihood k, R11-2 within-class repeat-infection decomposition, R11-3 cluster composition, predictions scored |
| 59a_review_of_note58.md | 6577 | pre-run review of note 58 and starting-shape derivations, written before the round-11 arms were run |
| 59_r111_worlds.csv | 8173 | the round-11 worlds (worlds 1, 2a, 2b, 3 plus the round-10 gate comparator): likelihood and moment k with 90% intervals, observed and NB zero/80% shares at own mean and mean 1.4, venue shares, cluster and top-1% statistics |
| 59_r111_worlds_offspring.csv | 5817 | pooled offspring histograms of the worlds in 59_r111_worlds.csv |
| 59_r111_clusters.csv | 22271 | the ten largest clusters of each replicate in each world: offspring, distinct venues, share in one venue-day (600 rows) |
| 59_r112_repeat_infections.csv | 990 | repeat-infection correlations (16 weeks, 8 replicates) for world 1, world 2a and the round-10 gate cell, decomposed into all pairs, within-class pairs and within-others pairs |
| 59_r113_cluster_composition.csv | 49729 | R11-3 contact-tracing composition of the ten largest clusters per replicate across all five arms: same-household share, modal venue type and share, distinct venue types, infectee age min/max/mean/range (600 rows) |

Notes:

1. Not uploaded to root: run directories, traces, episode logs and HVI dumps (stored in `superspreader/study/results/round11/`), and the study scripts (`superspreader/study/run_round11.py`, `analyze_round11.py`, `report_round11.py`).
2. Still outstanding from earlier rounds on Drive: `47_s1_summary_BAD_upload_ignore.csv` and `50_r80_hours_by_type_BAD_upload_ignore.csv` are superseded duplicates.
