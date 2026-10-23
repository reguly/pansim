# ACT-049 Round 15 Upload Index (`74_*`)

Target Google Drive folder: `Work Hub\University Research\Aurora AI\Management\work-packages\ACT-049`
Local repository directory: `/home/ireguly/pansim/superspreader/` (committed to git).

All Round 15 deliverables (`74_*`) are in `superspreader/` and sized so every individual file is well below `2 MB` (the 9 infection-level export blocks `74_c_infections_<world>_reps<block>.csv` are `1.49–1.99 MB` each). Exact byte sizes, data row counts (excluding header for CSVs), and the first 16 hex digits of the SHA-256 checksum are listed below for verification (`sha256sum superspreader/74*`).

| File | Bytes | Data rows / Lines | SHA-256 (first 16) | Content |
| :--- | ---: | ---: | :--- | :--- |
| `74a_review_of_note73.md` | `13,867` | `78` lines | `45ab0573adbfc7f1` | Pre-run review of Note 73 (written before launching runs) |
| `74_round15_results.md` | `32,349` | `193` lines | `76316d7857019a76` | Full Round 15 report: Run C and Run D results and evaluation of predictions C(a)–C(e) and D(a)–D(e) |
| `74_upload_index.md` | — | — | — | This upload index |
| `74_c_cells_summary.csv` | `3,152` | `3` | `caad5c702f632e87` | Pooled Run C parent–child correlation, superspreader-pair excess, sibling ICC, venue-day share (`>=6`), and contact-tracing yield ratios across `w1:B1`, `w2b:B1`, `w3b:B1` |
| `74_c_parent_classes.csv` | `956` | `15` | `37078cbb5a00d8c9` | Conditional child mean offspring by parent offspring class (`1`, `2_to_5`, `6_to_9`, `10_or_more`, `all_children`) vs day-matched expectation |
| `74_c_subgroups.csv` | `1,470` | `11` | `bab75b0d6fc15692` | Run C parent–child statistics split by `same_household` vs `outside_household` and (for `w3b`) `inside_event` vs `outside_event` |
| `74_c_replicate_summary.csv` | `11,289` | `36` | `5999c9c069beda6e` | Per-replicate Run C summary across all 36 runs (`3 worlds x 12 seeds 77001..77012`) |
| `74_c_infections_w1_reps01_04.csv` | `1,816,871` | `32,031` | `4274181b51660399` | Infection-level export (`d <= 28`, with 14d and 42d offspring counts) for `w1:B1`, replicates `1..4` |
| `74_c_infections_w1_reps05_08.csv` | `1,521,685` | `26,927` | `2f285c98387f5001` | Infection-level export for `w1:B1`, replicates `5..8` |
| `74_c_infections_w1_reps09_12.csv` | `1,680,700` | `29,324` | `afaea8b058c1c4f6` | Infection-level export for `w1:B1`, replicates `9..12` |
| `74_c_infections_w2b_reps01_04.csv` | `1,783,756` | `30,300` | `f381d8ab19fe1b4b` | Infection-level export for `w2b:B1`, replicates `1..4` |
| `74_c_infections_w2b_reps05_08.csv` | `1,992,900` | `33,841` | `5278d87dbaa1355d` | Infection-level export for `w2b:B1`, replicates `5..8` |
| `74_c_infections_w2b_reps09_12.csv` | `1,488,243` | `25,043` | `d5760c39c6eb1072` | Infection-level export for `w2b:B1`, replicates `9..12` |
| `74_c_infections_w3b_reps01_04.csv` | `1,633,774` | `28,453` | `658ea52bb3cb4925` | Infection-level export for `w3b:B1`, replicates `1..4` |
| `74_c_infections_w3b_reps05_08.csv` | `1,813,854` | `31,584` | `9ac4163d11ef5fd5` | Infection-level export for `w3b:B1`, replicates `5..8` |
| `74_c_infections_w3b_reps09_12.csv` | `1,574,438` | `27,130` | `9af96ea3c6b4842f` | Infection-level export for `w3b:B1`, replicates `9..12` |
| `74_d_cells_summary.csv` | `7,615` | `9` | `1508147a9d3cec76` | Pooled Run D summary across `alpha in {1.0, 0.5, 0.0}` for `w1`, `w2b`, `w3b` (including 95% replicate-bootstrap CIs) |
| `74_d_replicate_summary.csv` | `26,363` | `108` | `b9be6acf5f99f6b6` | Per-replicate Run D summary (`9 cells x 12 seeds 77001..77012`) |
| `74_d_replicate_histograms.csv` | `106,364` | `3,719` | `182979554696a0cd` | Per-replicate days 1–10 index-case offspring histograms for all 9 Run D cells |
| `74_d_calibration_log.csv` | `2,711` | `34` | `d43362bd5172acf2` | Calibration trials on seeds `76001..76006` and final 12-seed attempts (`77001..77012`) for Run D |
