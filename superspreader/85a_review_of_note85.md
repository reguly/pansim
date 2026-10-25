# 85a. Review of note 85 before the round-17 runs

25 October 2026, 15:40 CET. Reply to note 85. The predictions below are the ones that will be scored. Nothing in this review changes a threshold.

## What the note asks, and what is already on disk

Note 84 is the reading of round 16. Its checks of runs A, B, F and G match the files in `83_`. Run E was stopped by the every-bin gate in note 82. Note 85 replaces that gate with equivalence statistics that are reported and do not stop the run. World 1 at exponent 1 already has twelve traces and episode logs under `results/round16/E/w1_a1` from that stopped cell. The other four cells were not finished. `82a_review_of_note82.md` and `83_h_replicate_histograms.csv.gz` are in the repository and were not yet in the Drive folder when note 84 was written. They are part of the delivery of this round.

## Run P

The October binary that produced the round-14 world-1 trace is not on disk. `build_r10/panSim` was rebuilt on 25 October 2026 at 11:45 CET (sha256 `af141d454451cca3ba19cd3f7e16fad42ed812fab443840eac58d9191838c4a3`). Every other `build_*/panSim` is dated 15–18 October, before commit `558295a` (19 October 2026, 15:50 CEST), which changed `infectionPolicies.h` and `movementPolicies.h`. No build directory is dated between 19 and 24 October, so the binary used on 22 October cannot be recovered from a directory mtime.

The CMake caches that remain are Release, `-O3 -DNDEBUG`, `g++-12` 12.4.0, nvcc 12.0.140, OpenMP 4.5, `USE_GPU=ON`, `GPU_ATOMICS=ON`, architecture 8.9. `CMakeLists.txt` says the atomic reduction is faster and not deterministic. Host random streams are sized by `omp_get_max_threads()` (`randomGenerator.cpp`). The machine is a 13th-gen Intel i7-13620H, 16 threads, WSL2 kernel 6.18.54, RTX 4050.

Replaying the round-14 `command.json` for world 1 seed 77001 (including `--infectionTrace`) on the rebuilt Release binary, on `build_r67/panSim`, and on the flag variants below, gives day 5 = 628 and day 28 = 4,508. The stored run is day 5 = 626 and day 28 = 5,236. Leaving `--infectionTrace` off changes the same binary to day 5 = 626 and day 28 = 4,327, so the trace flag is part of the command and is included in every comparison below. `OMP_NUM_THREADS=1` on the Release binary gives day 5 = 697 and day 28 = 5,523.

The six builds, all from commit `6302476` (simulator source `558295a`), GPU, g++-12, and the round-14 command:

| build | flags | day 5 | day 28 |
| --- | --- | --- | --- |
| existing `build_r10` and `build_r67` | `-O3`, atomics on, contraction on, 16 threads | 628 | 4,508 |
| `build_noatom` | `-O3`, atomics off | 628 | 4,508 |
| `build_o3_nofma` | `-O3`, `-ffp-contract=off`, nvcc `--fmad=false` | 628 | 4,508 |
| `build_o2` | `-O2`, atomics on, contraction on | 628 | 4,508 |
| `build_o2_nofma` | `-O2`, `-ffp-contract=off`, `--fmad=false` | 628 | 4,508 |
| `build_o3_nofma_noatom` | `-O3`, contraction off, atomics off | 628 | 4,508 |

None of the six builds reproduces day 28 = 5,236. The atomics-off binaries abort at process exit (`cudaErrorCudartUnloading`) after the table has been written; the day-5 and day-28 counts above are from that table. The build used for the rest of this round is therefore the Release GPU build with atomics on, `-O3`, contraction left at the compiler default, and the usual 16 OpenMP threads. Runs E, D and B2 use that flag set on the source that contains the episode log and the scene repair. Run C's before binary is the October source with those same flags. Run C's after binary is that source plus only the `hviOthersChance` repair.

## Errors and expectations that the runs will not silently change

1. **Run C, prediction C(a).** Note 82's repair composes the scene scale with the mean-preserving factor. The arithmetic in `82a` still stands: after the repair, non-class discretionary hours are about 1.95 per day, against a baseline of 3.40 (about 43% below), not within 3%. C(a), read as total non-class discretionary hours within 3% of baseline, is expected to fail. Low-L hours should match the S8-2 baseline. Both will be reported. The before binary is commit `6302476`. The after binary adds the repair in `hviOthersChance` and its two call sites, and does not add the episode log.

2. **Run D.** Note 82 asks for day 70 and day 112, so the PS1 arms are run for 16 weeks. Section 5.3's original runs were 10 weeks. `82a` expects D(a) to fail on the original map because recovered agents return to susceptible and a large share of that small population is infected twice by day 112. The enlarged-map world-1 cell is the comparison. Both moment k and likelihood k are reported; D(b) is scored on likelihood k.

3. **Run E, predictions E(a) and E(b).** `82a` expects the stay-level concentration H to lie near 0.06–0.35, not in the registered bands 0.65–0.90 and 0.85–1.00, because the shedding multiplier is drawn once per infection. H is still the stay-level index defined in note 82, and E(a) and E(b) are scored on that definition. Note 84 already found the world-1 exponent-1 histograms statistically close (mean 1.292 against 1.295, likelihood k 0.254 against 0.245, chi-square p = 0.32). E(e) is scored again from the files, including the four cells that were not run in round 16.

4. **Run B2.** The start point in note 85 matches `69_tuning_log.csv`: event rate 0.08435, coefficient 9.04632e-05, 24-seed mean 0.867, likelihood k 0.265. The later 12-seed confirmation of that search (mean 0.855, k 0.259) is not the start. The update is a joint secant on the mean and likelihood k, at most nine trials on seeds 89001–89012, then one 36-seed run. Round 14 updated the rate from k and the coefficient from the mean separately; that is not what this note asks for.

5. **Equivalence does not stop Run E.** A cell whose chi-square p is below 0.05, or whose mean or k misses E(e), is still exported and scored for E(a)–E(d).
