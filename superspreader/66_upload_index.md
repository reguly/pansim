# ACT-049 Round 13 upload index (`66_*`), state at the checkpoint

Drive folder: ACT-049. Files marked **Drive** were uploaded through the Drive connector. The connector takes file content as text inside the call, so large CSV files could not be uploaded; those are marked **local only**: they are in the git repository `pansim`, directory `superspreader/` (branch `cursor/round5-results-a0f6`, commits "Round 13 N0", "Round 13 N4", "Round 13 N1 items 1-2") and need a manual copy to Drive (or tell me a smaller form you can use, for example only rounds 10 to 12 for N0).

| File | Bytes | Where | Content |
|---|---|---|---|
| `66a_review_of_note65.md` | 7,632 | Drive | review of note 65 |
| `66_round13_results.md` | 17,889 | Drive | N0, N4, N1 items 1 and 2, predictions, checkpoint tables, cell table, calibration iterations of the 78001 set |
| `66_upload_index.md` | this file | Drive | index |
| `66_n1_calibration_log.csv` | 1,794 | Drive | every calibration iteration, all N1 cells and the round-12 and round-6 sets |
| `66_n4_noise_summary.csv` | 9,265 | Drive | draw SD against replicate SE, per world, scheme and rate |
| `66_n1_cells_summary.csv` | 16,257 | local only | pooled statistics with replicate-bootstrap 5th and 95th percentiles and bootstrap SD for every N1 cell |
| `66_n1_checkpoint_pairs.csv` | 9,964 | local only | all between-set comparisons (table in the results file covers the same numbers except the world-1 frozen duplicate) |
| `66_n1_replicate_summary.csv` | 55,003 | local only | per replicate, N1 cells |
| `66_n1_replicate_histograms.csv` | 132,255 | local only | per replicate offspring histograms, N1 cells |
| `66_n0_replicate_summary.csv` | 401,523 | local only | N0: 101 arms, 1,152 replicates |
| `66_n0_replicate_histograms.csv` | 660,039 | local only | N0 histograms |
| `66_n0_repeat_pairs_by_replicate.csv` | 2,685,036 | local only | N0 repeat pairs (66,477 rows) |
| `66_n4_thinning_draws.csv` | 1,414,592 | local only | N4 per replicate and draw (5,760 rows) |
| `66_n4_thinning_draws_pooled.csv` | 119,638 | local only | N4 pooled per draw (480 rows; Table 5.17a analogue) |

Not run, waiting for your checkpoint reading: N1 item 3 (seed set 79001 to 79012), N2, N3, N5.
