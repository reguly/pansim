# 59 upload index (round 11)

19 October 2026. Every file is in `superspreader/` with Unix newlines (`\n`) and under 1 MB. Each was checked after upload: the byte count Drive reports matches the local file exactly for all eight files.

| File | Bytes (local and on Drive) | Content |
|---|---|---|
| 59_round11_results.md | 36281 | main note: headline, deviations, the correction to note 58 on the closed-group events, R11-1 worlds matched on likelihood k, R11-2 within-class repeat-infection decomposition, R11-3 cluster composition, predictions scored |
| 59a_review_of_note58.md | 6577 | pre-run review of note 58 and the starting-shape derivations, written before the round-11 arms were run |
| 59_r111_worlds.csv | 9213 | the six arms (worlds 1, 2a, 2b, 3b, 3 and the round-10 gate comparator): likelihood and moment k with 90% intervals, observed and NB zero and 80% shares at own mean and at mean 1.4, venue shares, cluster and top-1% statistics. Every number quoted in the main note comes from this file. |
| 59_r111_worlds_offspring.csv | 7391 | pooled offspring histograms of the six arms |
| 59_r111_clusters.csv | 27077 | the ten largest clusters of each replicate in each arm: offspring, distinct venues, share in one venue-day (720 rows) |
| 59_r112_repeat_infections.csv | 990 | repeat-infection correlations (16 weeks, 8 replicates) for world 1, world 2a and the round-10 gate cell, decomposed into all pairs, within-class pairs and within-others pairs |
| 59_r113_cluster_composition.csv | 59579 | R11-3 contact-tracing composition of the ten largest clusters per replicate across all six arms: same-household share, modal venue type and its share, distinct venue types, infectee age min, max, mean and range (720 rows) |
| 59_upload_index.md | this file | the index |

Notes:

1. **Four CSVs were uploaded twice.** The first upload covered five arms. While checking the note against the data I found that the round-6 closed-group arm `r67_M30` reaches likelihood k 0.330, which contradicts note 58's premise that the events cannot be matched, so that arm was added as world 3b and the affected files were regenerated. The superseded first versions are still in the folder, renamed so they cannot be confused with the current ones: `59_r111_worlds_SUPERSEDED_ignore.csv`, `59_r111_worlds_offspring_SUPERSEDED_ignore.csv`, `59_r111_clusters_SUPERSEDED_ignore.csv` and `59_r113_cluster_composition_SUPERSEDED_ignore.csv`. Please trash them; I cannot. `59_r112_repeat_infections.csv` was not affected and was uploaded once.
2. Not uploaded: run directories, traces, episode logs and HVI dumps (they stay in `superspreader/study/results/round11/`, and world 3b's in `results/round6/cal/r67_M30/`), and the study scripts (`superspreader/study/run_round11.py`, `analyze_round11.py`, `report_round11.py`).
3. Still outstanding from earlier rounds on Drive: `47_s1_summary_BAD_upload_ignore.csv` and `50_r80_hours_by_type_BAD_upload_ignore.csv` are superseded duplicates I cannot delete; please trash them too.
