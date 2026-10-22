# ACT-049 Round 13 upload index (`66_*`), state at the checkpoint

Target Drive folder: ACT-049. Files marked **Drive** are uploaded through the Drive connector; files marked **local only** are too large to pass through the connector (it takes file content as text in the call) and are in the git repository `pansim`, directory `superspreader/` (commit history of the `cursor/round5-results-a0f6` branch); they need a manual copy.

| File | Bytes | Where | Content |
|---|---|---|---|
| `66a_review_of_note65.md` | about 10,000 | Drive | review of note 65 |
| `66_round13_results.md` | about 17,000 | Drive | N0, N4, N1 items 1 and 2, predictions, checkpoint |
| `66_upload_index.md` | this file | Drive | index |
| `66_n1_cells_summary.csv` | 16,257 | Drive | pooled statistics with replicate-bootstrap intervals for each N1 cell (+ round-12 and round-6 sets) |
| `66_n1_calibration_log.csv` | 1,794 | Drive | every calibration iteration |
| `66_n1_checkpoint_pairs.csv` | 9,964 | Drive | between-set differences, z and SD over SE |
| `66_n4_noise_summary.csv` | 9,265 | Drive | draw SD against replicate SE |
| `66_n1_replicate_summary.csv` | 55,003 | local only | per replicate, N1 cells |
| `66_n1_replicate_histograms.csv` | 132,255 | local only | per replicate offspring histograms, N1 cells |
| `66_n0_replicate_summary.csv` | 401,523 | local only | N0: 101 arms |
| `66_n0_replicate_histograms.csv` | 660,039 | local only | N0 histograms |
| `66_n0_repeat_pairs_by_replicate.csv` | 2,685,036 | local only | N0 repeat pairs |
| `66_n4_thinning_draws.csv` | 1,414,592 | local only | N4 per replicate and draw |
| `66_n4_thinning_draws_pooled.csv` | 119,638 | local only | N4 pooled per draw (Table 5.17a analogue) |
