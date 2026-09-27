# WP0007 — algorithmic emergence

Code for **From “More Is Different” to Algorithmic Emergence: Regularity, Compression,
and the Limits of Discovery**, by Giulio Ruffini, Francesca Castaldo, Kaiti, and Klaus.
The [paper’s preprint DOI](https://doi.org/10.5281/zenodo.21008465) follows the paper across
revisions. These examples accompany the forthcoming revised Section 5.3 and Appendix B.2.

## Reproduce the worked-example numbers

Python 3.8 or later, with no third-party packages, is sufficient:

```sh
python3 reproduce.py
```

The command runs both independent numerical verifiers, checks their results against the
recorded JSON, and asserts every entry in the worked-example tables. It exits with an
error if a check fails. The observations are synthetic; no download or external service
is used. The model-source byte count is part of the glider account, so keep the codec
file unchanged when reproducing that count.

| File | Paper location and output |
|---|---|
| `code/example_b_codec.py` | Section 5.3 and Appendix B.2: lossless glider codec and escape branch |
| `code/check_example_b.py` | Figure 5 and glider table (Entropy A2; BCOM 3): independent Life evolution, 240 configurations, coding costs, and reuse thresholds |
| `code/ca_examples.py` | Figure 6 and CA table (Entropy A3; BCOM 4): all 256 elementary rules, exact AND closure, OR search failure, construction and separate-run test |
| `reproduce.py` | Both recorded result files and every entry in `results/paper_tables.json` |
| `code/render_ca_example.py` | Figure 6 as vector PDF and PNG |
| `code/render_glider.tex` | Figure 5 experiment chain and five glider frames as a standalone vector drawing |

`results/` contains the verified outputs. The command prints its results and does not
replace the reference files. The explanations and coding conventions are in
[EXAMPLES.md](EXAMPLES.md).

## The pictures serve distinct questions

The glider model captures a recurring object. Its coordinates reconstruct past frames
and predict future positions. Compared with the sparse initial-state simulator, one run
does not repay the implementation; sufficient reuse does.

The cellular automaton compares two observation tasks on the same rule-146 microscopic
run. Fully occupied triples follow the closed rule 128. Nonempty triples do not admit
an exact elementary-rule fit on the observed transitions. The selected rule’s correction
code fails the declared compression margins. This failure concerns the specified model
class and code; it does not prove incompressibility or exclude other model classes.

The paper’s shift-register witness addresses a different question: residual information
retained from the initial state. It remains beside Theorem 1. These finite examples do
not establish the general discovery or optimality barriers.

## Figure reproduction

The committed PDFs are vector graphics. To redraw the CA figure, install NumPy and
Matplotlib and run:

```sh
python3 code/render_ca_example.py
```

For the glider figure, a TeX Live installation with TikZ and the standalone class suffices:

```sh
latexmk -xelatex -outdir=figures code/render_glider.tex
```

The optional `--figcheck-dir` switch of the CA renderer enables a development layout
checker; it is unnecessary for either numerical reproduction or drawing the figure.

## Formalization and versions

Lean proofs remain in [KTAIT](https://github.com/giulioruffini/KTAIT). Its
[AlgorithmicEmergence.lean](https://github.com/giulioruffini/KTAIT/blob/main/KTAIT/AlgorithmicEmergence.lean)
contains `no_compression_improver`, `identification_barrier`, and
`relational_optimality_barrier`. The paper’s Appendix F
specifies which declarations support each claim and which claims remain at paper level.
No Lean sources or additional formalization claims are introduced here.

The main branch tracks the code for the next manuscript revision. At submission, a tag
will bind it to the manuscript version and a Zenodo software DOI will identify that
release. No software release DOI has been minted yet. The paper DOI above identifies
the paper, not this software. Tags will not be moved; corrections will receive new releases.

## Licensing and citation

Code is licensed under **Apache-2.0**. Data, figures, and repository text are licensed under
**CC-BY-4.0**. This is the BCOM paper-companion exception to proprietary-by-default, adopted
on **September 27, 2026**. See [LICENSE](LICENSE) and the full texts in `LICENSES/`.

Use [CITATION.cff](CITATION.cff) for the preferred paper citation. It will carry the software
DOI after the first release. The examples draw on
[Gardner’s introduction to Conway’s Life](https://doi.org/10.1038/scientificamerican1070-120),
[Wolfram’s elementary-rule convention](https://www.wolframscience.com/nks/p53--more-cellular-automata/),
and [Israeli and Goldenfeld’s coarse-graining construction](https://doi.org/10.1103/PhysRevE.73.026203).
No third-party papers or datasets are redistributed.
