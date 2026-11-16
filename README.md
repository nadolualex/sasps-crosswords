# Crosswords: Strategy sau if/elif?

Autori: Nadolu Alex și Dalya Tobescu (SASPS, Milestone 1).

Același joc de cuvinte încrucișate, în două variante. Grila, regulile și indiciile
sunt la fel. Diferă doar cum e aleasă politica de indiciu: `if/elif` sau Strategy.

La M1 avem prototipul, testele și o primă măsurătoare. Restul experimentelor și
articolul rămân pentru M2 și M3.

## Rulare

Python 3.10 sau mai nou, fără pachete externe pentru joc, teste și benchmark.

```bash
python3 -m crosswords --variant strategy --seed 42
python3 -m crosswords --variant conditional --seed 42
```

Comenzi în joc: `clues`, `show`, `answer 1A CAL`, `hint 2A random`, `quit`.
Politicile de indiciu sunt `first` (prima literă lipsă), `random` (o literă la
întâmplare) și `word` (tot cuvântul). Un `-` într-un răspuns șterge litera de
pe poziția respectivă.

Câteva reguli:

- literele date prin indiciu rămân blocate, iar un răspuns care le contrazice este respins;
- un indiciu corectează și literele greșite, dar nu atinge literele deja corecte;
- un indiciu pe un cuvânt rezolvat nu face nimic și nu consumă numere aleatoare;
- grila e câștigată când toate cele 11 celule sunt corecte.

Demonstrație fără input, care rezolvă grila:

```bash
python3 -m crosswords --variant conditional --seed 42 --demo
python3 -m crosswords --variant strategy --seed 42 --demo
```

Grila 5×5 are patru definiții: CAL, DOR, LAC și CODUL.

## Teste și măsurători

```bash
python3 -m unittest discover -v
python3 -m scripts.benchmark --repeats 30 --games 256 --warmups 3 --seed 2026 --output results/reproduced
python3 -m scripts.code_metrics
```

Comanda de benchmark scrie în `results/reproduced`, ca să nu suprascrie datele
din `results/m1`. Timpii diferă de la o rulare la alta; verificarea stării și a
numerelor aleatoare trebuie să iasă la fel.

Prima măsurătoare (30 de perechi, 256 de jocuri, 8 apeluri de indiciu pe joc) e
descrisă în [`results/m1/REPORT.md`](results/m1/REPORT.md). A rulat pe un singur
calculator, într-un singur scenariu, așa că nu tragem concluzii din ea. Detalii în
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## Prezentarea

Fișierul pentru susținere este [`presentation/SASPS_M1_Crosswords.pptx`](presentation/SASPS_M1_Crosswords.pptx):
12 slide-uri cu note, pentru 9 minute și 30 de secunde. PDF-ul din același folder
e o copie a slide-urilor, nu articolul de la M3.

Ca să o regenerăm, avem nevoie de `python-pptx`, `reportlab` și `pypdf`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install python-pptx reportlab pypdf
.venv/bin/python -m scripts.build_presentation
.venv/bin/python -m scripts.verify_release
```

`verify_release` rulează testele și demo-urile, recalculează sumarul din datele
brute, verifică PPTX-ul și PDF-ul și rescrie `results/m1/validation.json`.

## Structura proiectului

| Cale | Ce conține |
|---|---|
| `crosswords/` | motorul, grila, politicile și cele două variante de selecție |
| `tests/` | teste de reguli, erori și echivalență între variante |
| `scripts/` | benchmark, metrici de cod, generator de prezentare, verificare |
| `results/m1/` | date brute, rapoarte și loguri de la M1 |
| `docs/` | metodologie, arhitectură, plan, contribuții |
| `presentation/` | PPTX, PDF cu slide-urile, manifest |

## Git

Codul e pe https://github.com/nadolualex/sasps-crosswords. Versiunea de la M1 are
tag-ul `M1`. Tag-urile M2 și M3 le punem când ajungem acolo. Suportul de curs nu
e în repository.

Împărțirea muncii e în [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md).
