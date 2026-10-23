# Note 72. The supplied literature review: what was used, what was checked, what differs

23 October 2026. ACT-049, drafting side. Companion to paper version 11 (Section 3.8, Section 5.20, Appendices B and D).

## 1. What the review is

A document of about 9,800 words, "Mathematical and Computational Modeling of Infectious Disease Superspreading", with a comparison table of modelling paradigms, a roster of 24 studies, sections on causes and on public health implications, and 105 works cited as links. I used it as a map of the literature. Every statement that entered the paper was checked against the primary paper, and I read the full text, or at least the abstract, of each work cited (Appendix B of the paper has the level of reading).

## 2. What it added to the paper

1. **Related work (Section 3.8).** Distribution families (Delaporte, Poisson-lognormal), estimation under under-reporting (Lloyd-Smith 2007, zero-truncated likelihood, phylogenetic estimation), compartmental structure (Meehan 2023), persistent against transient heterogeneity (Tkachenko 2021), network and venue models (Sneppen 2021, Nielsen 2021, Chang 2020), assortativity (Taube 2022), tracing direction (Juul and Strogatz 2023, Bradshaw 2021) and other pathogens (tuberculosis, dengue, mpox, Ebola, MERS).
2. **A new analysis suggested by it (Section 5.20).** The review's account of the Delaporte distribution led me to fit it, and the Poisson-lognormal, to the simulated offspring counts already delivered. Result: the baseline share separates the three worlds (about 0, 0.04 to 0.17 and 0.17 to 0.51), tracks the share of offspring outside events within 0.04 to 0.06, and removes the zero-share deficit of the events world. The published summary shares allow baseline shares from 0 to about 0.4, so they cannot exclude any world.
3. **A bound** (Appendix C44): a Delaporte baseline share cannot exceed minus the logarithm of the zero share over the mean offspring, 0.45 to 0.46 at the published values.
4. **A connection** (Appendix C45): the Erlang-stage result of Meehan 2023 is one case of the composition rule of Section 5.15.
5. **Two practice points and a qualification** in Section 7: fit a Delaporte beside the negative binomial, state the distribution assumed when claiming an estimator is unbiased under under-detection; the no-downward-bias result of Lloyd-Smith 2007 is for negative-binomial data and our Section 5.17 shows a downward bias for a mixture.

## 3. Differences between the review and the primary records

| Review statement | Primary record |
|---|---|
| "Brainard et al. (2024)": 592 events, 9,883 index cases, 67% zero, 3% above five | The same compilation as McKee et al. 2024 (reference 40 of the paper); Brainard et al. 2023 (reference 6) is a different, earlier review |
| "Morris et al. 2023" | Meehan et al. 2023, Scientific Reports |
| "Quang et al. 2023" (dengue) | Vazquez-Prokopec et al. 2023, PNAS Nexus |
| "Physical Review E critique (2023)" | Juul and Strogatz 2023, Physical Review E |
| Taube et al. proved assortative generation of superspreaders | The authors report a ratio above 1 in 12 of 18 trees and call the support preliminary; I found no significance test in the text read |
| Several sources are web pages, repository copies, ResearchGate pages and a Google Scholar profile (used for the Britton et al. result) | Not used; Britton et al. 2020 and Gomes et al. 2022 remain unread and are cited through Tkachenko 2021 |
| In-text numbers of citations | They do not all match the position of the entries in the list of works (for example, the number given to the backward-tracing study of Bradshaw et al. points to a different entry), so no statement was accepted from the review alone |

## 4. What the review did not change

None of the results of rounds 6 to 14 changes. The review's central claim that contact heterogeneity dominates biological variation rests on models with overdispersed contact numbers; in the frequency-dependent kernel of this study contact hours are bounded by the day and are not the relevant quantity, so the paper qualifies that reading and does not adopt it (Sections 3.8 and 7). The review's recommendation of occupancy caps relies on a density-dependent kernel; the paper states that in a frequency-dependent kernel they would not work, and lists the kernel as the main structural uncertainty (Section 6).

## 5. Open items that the review points to and the study has not done

1. The infector-infectee offspring ratio of Taube et al., which the three worlds predict differently (zero apart from shared settings in world 1, positive with a persistent class in world 2b). It needs the infector of each index case in the simulator output; a small round could add it.
2. Zero-truncated and Delaporte likelihoods applied to thinned data (Section 5.17).
3. A density-dependent kernel arm, to test whether occupancy caps and venue concentration change the individual-level $k$.
4. Tracing strategies in the three worlds.

I have not drafted instructions for these; say if you want a round 15 note.
