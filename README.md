# SASPS — Crosswords: Strategy pattern vs condiționale

**Milestone 1: prototip și pilot exploratoriu, nu proiect final M3.**
Același joc de cuvinte încrucișate, două variante care diferă doar prin
dispatch-ul politicilor de indicii. Runtime-ul și testele folosesc Python stdlib.
Python 3.10+; mediul măsurat efectiv este Python 3.13.2 / macOS / arm64.

## Prezentare și demonstrație

Fișierul pentru susținerea fizică: [`presentation/SASPS_M1_Crosswords.pptx`](presentation/SASPS_M1_Crosswords.pptx).
12 slide-uri, diagrame editabile și note de prezentator, **9 minute 30 secunde**
planificate, plus 2 minute de întrebări. PDF-ul alăturat este numai copia vizuală
a slide-urilor, **nu articolul științific de la M3**.

Din folderul proiectului:

```bash
cd /Users/rnadolu/Desktop/SASPS-M1
python3 -m crosswords --variant strategy --seed 42
python3 -m crosswords --variant conditional --seed 42
```

Comenzi interactive: `clues`, `show`, `answer 1A CAL`, `hint 2A random`, `quit`.
Politici: `first`, `random`, `word`. `-` șterge o literă neprotejată; răspunsurile
sunt normalizate la majuscule ASCII. Literele obținute prin indicii sunt protejate;
un răspuns în conflict este respins atomic. Literele corecte nu sunt dezvăluite
din nou; cele greșite pot fi corectate prin indicii. Indiciile pe un cuvânt deja
rezolvat nu consumă RNG și nu cresc contorul. Câștigul cere toate cele 11 celule corecte.

Demo fără input, sigur pentru prezentare:

```bash
python3 -m crosswords --variant conditional --seed 42 --demo
python3 -m crosswords --variant strategy --seed 42 --demo
```

Grila 5×5 are patru definiții originale: CAL, DOR, LAC și CODUL. Motorul,
datele, regulile, UI-ul și algoritmii de indicii sunt comuni. În baseline,
`if/elif` selectează direct helper-ul; în Strategy, un registru selectează un
obiect cu interfața `HintStrategy`, care apelează același helper.
Nu duplicăm algoritmii și nu introducem deliberat dezavantaje în baseline.

## Reproducere

```bash
python3 -m unittest discover -v
python3 -m scripts.benchmark --repeats 30 --games 256 --warmups 3 --seed 2026 --output results/reproduced
python3 -m scripts.code_metrics
```

Rularea de mai sus păstrează datele inițiale din `results/m1`. Pentru a înlocui
explicit pilotul M1, folosește `--output results/m1`, apoi regenerează prezentarea.
Rezultatele temporale diferă între rulări; protocolul și checksum-ul stării/RNG
sunt reproductibile în același mediu Python.

Pilotul M1 conține 30 perechi, 2.048 apeluri/pereche/variantă, 3 încălziri per
variantă, cu ordine pseudoaleatoare reproductibilă în perechi. CSV-ul brut și
metadatele sunt în [`results/m1`](results/m1/REPORT.md).
**Este o măsurare exploratorie pe o singură mașină, fără inferență statistică.**
Cronometrăm apelul întreg de indiciu, nu costul izolat al dispatch-ului.
Efortul de extensie și memoria nu au fost încă măsurate.

## Regenerarea prezentării

Numai generarea PPTX/PDF necesită dependențe externe:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-presentation.txt
.venv/bin/python -m scripts.build_presentation
.venv/bin/python -m scripts.verify_release
```

Generatorul folosește datele reale din `results/m1/summary.json` și
`code_metrics.json`, produce PPTX cu note și un PDF de slide-uri din aceeași
descriere de layout. Verificatorul rulează testele și demo-urile, verifică
rezultatele brute, bounds/layout și notele PPTX și scrie un raport actual,
fără a pretinde randare identică în orice versiune PowerPoint.

## Structură

| Cale | Rol |
|---|---|
| `crosswords/engine.py`, `puzzle.py`, `policies.py` | Motor, grilă și algoritmi comuni |
| `crosswords/conditional.py`, `strategy.py` | Singura variație de design investigată |
| `tests/` | Reguli, erori atomice, echivalență și RNG |
| `scripts/` | Benchmark, metrici descriptive, generator și verificare |
| `results/m1/` | Date brute și dovezi reale M1 |
| `docs/` | Metodologie, arhitectură, plan și contribuții de confirmat |
| `presentation/` | PPTX obligatoriu, PDF de slide-uri, manifest |

## Git local și publicare personală

Repository țintă **privat**: https://github.com/nadolualex/sasps-crosswords .
Release-ul M1 are commit real și tag `M1`; nu există tag-uri M2/M3.
Identitatea locală folosește contul confirmat
`nadolualex` și adresa GitHub noreply verificată; nu reprezintă un nume academic
confirmat. Nu modificăm configurația globală și nu folosim contul Adobe.

Contul personal a fost autorizat și verificat ca `nadolualex`. Pentru o clonă
sau o publicare ulterioară, verifică din nou identitatea înainte de push.
Nu salva tokenuri în proiect și nu modifica configurația globală:

```bash
cd /Users/rnadolu/Desktop/SASPS-M1
# Elimină doar din acest shell variabilele care pot suprascrie contul keyring.
unset GH_TOKEN GITHUB_TOKEN
gh auth login --hostname github.com --git-protocol https --web
gh auth switch --hostname github.com --user nadolualex
gh api user --jq .login
```

**Oprește-te dacă ultima comandă nu afișează exact `nadolualex`.** Nu șterge
contul profesional din keyring și nu publica folosind autentificarea lui.
Repository-ul țintă există deja; **nu îl recrea**. Comenzi de verificare:

```bash
env -u GH_TOKEN -u GITHUB_TOKEN gh api repos/nadolualex/sasps-crosswords --jq '{full_name,private}'
git remote -v
git rev-parse main
git rev-list -n 1 M1
git -c credential.helper= -c 'credential.helper=!env -u GH_TOKEN -u GITHUB_TOKEN gh auth git-credential' ls-remote origin refs/heads/main refs/tags/M1
```

Pentru schimbări viitoare, după validare, folosește HTTPS și helper doar pe
comandă; nu folosi cheia SSH profesională:

```bash
git -c credential.helper= -c 'credential.helper=!env -u GH_TOKEN -u GITHUB_TOKEN gh auth git-credential' push origin main
```

Nu suprascrie istoricul și nu muta tag-ul `M1`. Nu publica suportul de curs/PDF-ul atașat, chei, tokenuri sau alte
materiale private. Acest proiect nu conține suportul de curs.

## Responsabilitate academică și proveniență

Prototipul, testele, documentația și prezentarea au fost pregătite cu asistență AI
GitHub Copilot. Nu sunt dovezi de muncă manuală a unor membri și nu reprezintă
ore/sprinturi istorice. Studentul trebuie să înțeleagă, să verifice și să adapteze
livrabilele, să confirme echipa și rolurile și să respecte politica de utilizare
AI și cerințele profesorului. Vezi [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md).
Numele academice și distribuția rolurilor rămân explicit de completat.
