# ACT-049 round 14 upload index (`69_*`)

Drive folder: ACT-049. On Drive: `69a_review_of_note68.md` (5,045 bytes), `69_round14_results.md` (23,862 bytes), this file, `69_b_calibration_log.csv`, `69_tuning_log.csv`. All other files are **local only**: they are in the git repository `pansim`, directory `superspreader/` (branch `cursor/round5-results-a0f6`) and need a manual copy to the Drive folder.

**Why the per-replicate files are not uploaded (a departure from note 68).** The connector takes file content as text typed into the call, so a file has to be transcribed. A test piece (`69_a_replicate_summary_part2.csv`, 14,207 bytes) came back one byte short on Drive (14,206): one of the 17-digit numbers had lost a digit. I deleted that piece (moved to trash) and did not upload the other per-replicate files in this way, because a silent transcription error in a research file is worse than a missing file. The round-13 per-replicate files appeared in the folder after round 13 (not uploaded by me); the same copy is needed here. Sizes, row counts and the first 16 hex digits of the SHA-256 of each file are given below so that a copy can be checked (`sha256sum`). Splitting by cell is not needed for a file copy (the largest is 136 KB).

| File | Where | Bytes | Data rows | SHA-256 (first 16) | Content |
|---|---|---|---|---|---|
| `69_a_cells_summary.csv` | local only | 18,757 | 12 | `8ee1930a8fb751fd` | pooled statistics with 90% intervals, run A cells and the round-13 cells recomputed |
| `69_b_cells_summary.csv` | local only | 15,805 | 10 | `a5bb487bdc69e650` | pooled statistics with 90% intervals, B1, B2 and the round-12 reference cells |
| `69_runA_two_set.csv` | local only | 6,078 | 84 | `61a08eeb08aa9b5b` | run A against round 13: all 14 statistics per cell (84 comparisons) |
| `69_a_replicate_summary.csv` | local only | 51,286 | 144 | `629f63439d1e82ab` | per replicate, run A and round-13 N3 cells |
| `69_a_replicate_histograms.csv` | local only | 135,700 | 4497 | `6764f656edc660f6` | per replicate offspring histograms, run A and round-13 N3 cells |
| `69_b_replicate_summary.csv` | local only | 66,821 | 192 | `3078d8b98499b94f` | per replicate, B1, B2 (24 or 36 replicates), reference cells |
| `69_b_replicate_histograms.csv` | local only | 109,234 | 4171 | `3cf30adc0b5eaf41` | per replicate offspring histograms, B cells |
| `69_a_calibration_log.csv` | local only | 2,276 | 44 | `cae761c546aefa2f` | calibration iterations of the run-A cells (and the round-13 cells) |
| `69_b_calibration_log.csv` | Drive | 1,275 | 26 | `2b8dd25fde3eccb7` | calibration iterations of the B1 final cells and references |
| `69_tuning_log.csv` | Drive | 2,461 | 31 | `92c3b6c4618721e4` | B1 and B2 trials and final attempts, including the extended world-3b search |

The results file `69_round14_results.md` and the review were checked by size against the local copies (23,862 and 5,045 bytes: equal).
