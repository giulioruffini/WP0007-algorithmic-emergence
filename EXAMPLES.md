# Coding conventions and checks

## The glider code captures a recurring object

A microstate contains a 256 by 256 periodic binary grid following Conway’s Game of Life and
an independent 4096-bit cyclic register. The observer retains 32 complete grid frames;
the objective requires the grid and none of the register. An isolated five-cell glider
returns to its original shape after four updates, translated one cell in each coordinate.
The model reconstructs the movie from position, phase, and direction.

The primary incumbent stores the five live-cell positions and simulates the known Life
rule. Both codes reconstruct the same retained movie, so discarding the independent
register contributes none of the compared saving. The acquired source includes the
projection, encoder, decoder, and literal fallback. Its complete file,
`code/example_b_codec.py`, is 2366 bytes, with SHA-256
`cd510a712f42640dba798a7d07c904b547a41c08efb3c13f4f2f7c67efda3155`.
A 23-bit length header gives an acquisition cost of 18,951 bits. This is an unminimized
implementation cost, not an estimate of Kolmogorov complexity. The shared frame supplies
Python, the generic module interface, Life, and the geometry; charging the module’s own
copy of Life is conservative. Editing this file changes the acquisition cost.

| Quantity, in bits | Construction: 294 runs | Test: two later runs |
|---|---:|---:|
| Acquired source and length header | 18,951 | 0 |
| Coordinates and mode flags | 6,174 | 42 |
| Corrections | 0 | 0 |
| Complete code | 25,125 | 42 |
| Sparse initial-grid simulation baseline | 25,284 | 172 |
| Saving | 159 | 130 |
| Required margin | 128 | 128 |

Each run costs 21 bits once the model is held, versus 86 bits for the sparse incumbent.
The 65-bit difference repays acquisition after 292 runs with 29 bits to spare; 294 runs
are needed for the 128-bit margin. Both codes are applied separately to each run, with
run counts and boundaries shared. A continuing run whose last grid is already shared is
a different protocol: its one-bit simulation match flag leaves no coordinate saving.
Appendix B.2 preserves the alternative dense-grid comparison and the separate accounting
for restoring the omitted register.

The verifier checks 240 combinations of grid size, position, phase, and direction against
an independent Life implementation, including wraparound, literal escapes, the declared
baselines, and the minimum run counts for repayment and both margins.

## The cellular-automaton code tests a coarse law

The microscopic system is elementary cellular automaton rule 146 on a periodic ring of
360 binary cells. Each output bit depends on a cell and its two nearest neighbors.
Wolfram’s number encodes its eight-bit update table; rule 146 outputs 1 for neighborhoods
001, 100, and 111, and 0 otherwise. Every three microscopic steps, a fixed readout maps
120 aligned triples to a 120-bit row. Forty coarse updates plus the first row give 4,920
retained bits.

For the fully occupied-block task, the readout is AND. Israeli and Goldenfeld’s exact
coarse rule is 128. For the nonempty-block task, the readout is OR. The search examines all
256 elementary rules, minimizes one-step bit errors, and breaks ties by rule number.
It selects rule 182 for the displayed OR record. The two readouts define different tasks;
each task and readout are fixed before its model search.

For each comparison the prior frame supplies rule 146, the task’s readout, geometry,
timing, and a generic interpreter. The incumbent sends a mode flag and the 360-bit initial
microscopic row: 361 bits. The acquired module contains two eight-bit tables, each with a
seven-bit length header: 30 bits. It stores its own copy of the supplied readout, charged
conservatively. This table cost presupposes the interpreter and is not comparable to the
glider’s source-module cost without specifying their different prior frames.

A model code contains a flag and the initial coarse row, costing 121 bits before corrections.
A correction list sends the gamma code of the number of errors plus one, followed by sorted
13-bit positions of the bits to flip. This is a lossless code even when a model is inaccurate.

| Quantity, in bits | AND, rule 128 | OR, rule 182 |
|---|---:|---:|
| Acquisition | 30 | 30 |
| Initial coarse row and flag | 121 | 121 |
| Construction corrections | 0 | 26,307 |
| Complete construction code | 151 | 26,458 |
| Construction baseline | 361 | 361 |
| Construction saving | 210 | −26,097 |
| Complete test code, model held | 121 | 27,561 |
| Test baseline | 361 | 361 |
| Test saving | 240 | −27,200 |

The construction and test initial states use seeds 7 and 23 in the verifier. Those seeds
and their generating recipe are not supplied to either decoder. The selected model is
held fixed for the test. AND passes both 128-bit margins; the OR code fails both.

All 512 nine-bit microscopic light cones verify AND closure exactly. The OR transitions
contain 1,476 conflicts against the first observed successor for each neighborhood,
traversing the record by time and cell position. This count differs from rule 182’s 1,370
one-step errors. Autonomous reconstruction disagrees at 2,022 movie bits and 54 of the
120 final-row cells (45%). The verifier checks reconstruction, escapes, fresh-run reuse,
and all 256 candidates with the declared correction code. Failure of this search does
not exclude models using memory, additional state, or another code.

## References and scope

The examples use [Gardner’s 1970 introduction to Conway’s Life](https://doi.org/10.1038/scientificamerican1070-120),
[Wolfram’s rule convention](https://www.wolframscience.com/nks/p53--more-cellular-automata/),
and [Israeli and Goldenfeld’s 2006 coarse-graining construction](https://doi.org/10.1103/PhysRevE.73.026203).
The finite checks illustrate acquisition and reuse; they neither compute shortest descriptions
nor prove the paper’s uniform impossibility theorems. Ordinary Life need not be reversible.
