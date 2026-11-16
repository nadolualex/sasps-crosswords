# Crosswords: Strategy or if/elif?

Nadolu Alex and Dalya Tobescu. SASPS, milestone 1.

Same crossword, two versions. The grid, the rules, and the hint algorithms are shared. The only difference is how the game picks a hint: `if/elif`, or the Strategy pattern.

This is M1: a working prototype, tests, and a first timing run. The rest of the experiments, and the paper, are for M2 and M3.

## Run

Python 3.10 or newer. The game, the tests, and the benchmark use only the standard library.

```bash
python3 -m crosswords --variant strategy --seed 42
python3 -m crosswords --variant conditional --seed 42
```

Commands: `clues`, `show`, `answer 1A CAL`, `hint 2A random`, `quit`.

Hint policies are `first` (first missing letter), `random` (one letter at random), and `word` (the whole word). A `-` in an answer clears that cell.

- A hinted letter stays locked. An answer that contradicts it is rejected.
- A hint fixes wrong letters and leaves correct ones alone.
- A hint on a solved word does nothing, and does not draw a random number.
- The grid is won when all 11 cells are correct.

Demo, no typing. It solves the grid:

```bash
python3 -m crosswords --variant conditional --seed 42 --demo
python3 -m crosswords --variant strategy --seed 42 --demo
```

The grid is 5×5, with four entries: CAL, DOR, LAC, and CODUL.

## Tests and timings

```bash
python3 -m unittest discover -v
python3 -m scripts.benchmark --repeats 30 --games 256 --warmups 3 --seed 2026 --output results/reproduced
python3 -m scripts.code_metrics
```

The benchmark writes to `results/reproduced`, so it does not overwrite `results/m1`. Times change from run to run. The final state and the random numbers should not.

The first run (30 pairs, 256 games, 8 hint calls per game) is in [`results/m1/REPORT.md`](results/m1/REPORT.md). One machine, one workload. Not a conclusion. See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## Slides

Talk from [`presentation/SASPS_M1_Crosswords.pptx`](presentation/SASPS_M1_Crosswords.pptx): 12 slides with notes, planned for 9 minutes 30 seconds. The PDF in the same folder is a copy of the slides, not the M3 paper.

Rebuild needs `python-pptx`, `reportlab`, and `pypdf`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install python-pptx reportlab pypdf
.venv/bin/python -m scripts.build_presentation
.venv/bin/python -m scripts.verify_release
```

`verify_release` runs the tests and demos, checks the raw results, checks the PPTX and PDF, and rewrites `results/m1/validation.json`.

## Layout

| Path | What is there |
|---|---|
| `crosswords/` | engine, grid, policies, both ways of picking a hint |
| `tests/` | rules, errors, and checks that the two versions match |
| `scripts/` | benchmark, code counts, slide builder, release check |
| `results/m1/` | raw timings and the M1 reports |
| `docs/` | methodology, architecture, plan, contributions |
| `presentation/` | PPTX, slide PDF, manifest |

Code: https://github.com/nadolualex/sasps-crosswords. The M1 snapshot is the `M1` tag. M2 and M3 tags come when we get there. The course handout is not in the repo.

Who did what is in [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md).
