# ACT-049 Round 13 upload index (`66_*`), final state (N0, N4, N1 items 1 to 3, N2, N3, N5 done)

Drive folder: ACT-049. Files marked **Drive** were uploaded through the Drive connector. The connector takes file content as text inside the call, so large CSV files could not be uploaded; those are marked **local only**: they are in the git repository `pansim`, directory `superspreader/` (branch `cursor/round5-results-a0f6`) and need a manual copy to Drive (or tell me a smaller form you can use, for example only rounds 10 to 12 for N0). The earlier checkpoint versions are on Drive under the names `66_round13_results_checkpoint.md`, `66_upload_index_checkpoint.md`, `66_n1_calibration_log_checkpoint.csv`.

| File | Where | Content |
|---|---|---|
| `66a_review_of_note65.md` | Drive | review of note 65 |
| `66_round13_results.md` | Drive | main results: predictions, N1 cells, between-set SD, N2, N3, N5 |
| `66_upload_index.md` | Drive | this index |
| `66_n1_calibration_log.csv` | Drive | every calibration iteration of all N1 cells (sets 77, 78, 79, 68) |
| `66_n1_between_set_sd.csv` | Drive | between-set SD against within-set SE per world and statistic |
| `66_n3_tuning_log.csv` | Drive | N3 trials |
| `66_n5_vs_n1_range.csv` | Drive | N5 against the range of the N1 sets |
| `66_n4_noise_summary.csv` | Drive | N4 draw SD against replicate SE |
| `66_round13_results_checkpoint.md` | Drive | first report, to the checkpoint (contains the N0 and N4 description) |
| `66_n1_cells_summary.csv`, `66_n2_cells_summary.csv`, `66_n3_cells_summary.csv`, `66_n5_cells_summary.csv` | local only | pooled statistics with bootstrap intervals for each cell |
| `66_n2_derivatives.csv` | local only | N2 changes per statistic (tabulated in the main file) |
| `66_n1_checkpoint_pairs.csv` | local only | two-set comparisons of the checkpoint |
| `66_n{1,2,3,5}_replicate_summary.csv`, `66_n{1,2,3,5}_replicate_histograms.csv`, `66_n{2,3,5}_calibration_log.csv` | local only | per replicate files and calibration logs of the cells |
| `66_n0_replicate_summary.csv`, `66_n0_replicate_histograms.csv`, `66_n0_repeat_pairs_by_replicate.csv` | local only | N0 (101 arms, 1,152 replicates; 0.4 MB, 0.7 MB, 2.7 MB) |
| `66_n4_thinning_draws.csv`, `66_n4_thinning_draws_pooled.csv` | local only | N4 (1.4 MB, 0.1 MB) |
