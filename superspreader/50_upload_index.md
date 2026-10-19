# 50 upload index (round 8)

18 October 2026. Everything is in this Drive folder; every file is under 1 MB and was uploaded whole. File sizes on Drive equal the local sizes for every file except the main note (see the first item below).

Items to know:

1. `50_round8_results.md` is 22,041 bytes on Drive and 22,040 bytes locally. I did not find the one-byte difference (all numbers and tables were pasted from the generated file); the content is otherwise the generated note.
2. One earlier upload of `50_r80_hours_by_type.csv` was truncated by a transcription error (8,349 bytes instead of 8,400). I renamed it `50_r80_hours_by_type_BAD_upload_ignore.csv` (I cannot delete) and uploaded the correct file under the proper name. Please ignore or delete the renamed file. The earlier renamed `47_s1_summary_BAD_upload_ignore.csv` is still there too.
3. `50a_review_of_note49.md` was uploaded before the infection runs.

| File | Bytes | Content |
|---|---|---|
| 50_round8_results.md | 22040 local, 22041 Drive | main note: headline, deviations first, R8-0, predictions scored, arm tables, summary row, S8-5, plain-terms reading |
| 50a_review_of_note49.md | 8408 | review of note 49 and the registered predictions |
| 50_r80_hours_by_type.csv | 8400 | R8-0: hours per agent-day by physical venue type, class and others, five movement variants |
| 50_r80_predictions.csv | 2585 | R8-0: predicted offspring ratio, CV^2 of weights, predicted k and acceptance range for every arm |
| 50_r80_productivity.csv | 207 | relative offspring weight per hour by venue type used by the predictor |
| 50_s8_summary.csv | 13654 | every S8-1 to S8-4 arm: shape measures with 90% bootstrap intervals, class shares, observed against predicted |
| 50_s8_offspring.csv | 4525 | offspring histograms of every arm |
| 50_s85_summary.csv | 1584 | S8-5: cap, scale-all and closure in two cells, with 90% intervals |

Not uploaded: run directories, traces and mobility logs (stay in `superspreader/study/results/round8/`), the L-modified location files (14 MB each; `build_r8_inputs.py` regenerates them), the code (`superspreader/study/`, uncommitted).
