# Metodologie

## Ce comparăm

Vrem să vedem ce se schimbă când alegerea politicii de indiciu se face prin
Strategy în loc de `if/elif`. Nu pornim de la ideea că Strategy e mai rapid sau
mai bun; pentru doar trei politici, varianta cu `if/elif` poate fi suficientă.

Singura diferență dintre variante este dispatcherul:

- `ConditionalDispatcher.select` alege cu `if/elif` și apelează direct funcția politicii;
- `StrategyDispatcher.select` caută într-un dicționar un obiect `HintStrategy`, care
  apelează aceeași funcție.

Funcțiile politicilor stau în `policies.py` și sunt folosite de ambele variante,
deci algoritmii sunt identici. La fel sunt grila, definițiile, validarea
răspunsurilor, blocarea literelor, contorul de indicii și interfața.

## Politici

| Politică | Ce dezvăluie |
|---|---|
| `first` | prima celulă nerezolvată din cuvânt |
| `random` | o celulă nerezolvată aleasă cu generatorul jocului |
| `word` | toate celulele nerezolvate din cuvânt |

O celulă e „nerezolvată” dacă e goală sau greșită. Un cuvânt deja corect nu
schimbă nimic și nu consumă numere aleatoare. O politică sau o definiție
necunoscută, ca și un răspuns invalid, dau `ValueError` și lasă jocul neschimbat.

## Ce verificăm

| | Întrebare | Cum măsurăm | Stadiu |
|---|---|---|---|
| E0 | Dau variantele aceleași rezultate, erori și numere aleatoare? | comparăm exact evenimentele și starea, inclusiv `Random.getstate()` | testat pe cazurile din `tests/` |
| H1 | Cât cod trebuie schimbat pentru o politică nouă? | fișiere și linii modificate, teste care pică | planificat pentru M2 |
| H2 | Cât durează un apel de indiciu? | mediană și Q1–Q3 pe apel, raport median pe perechi | prima măsurătoare, M1 |
| H3 | Cât costă crearea jocului? | timp și memorie la construcție | planificat pentru M2 |

`code_metrics.json` numără linii, clase și noduri `If` doar în fișierele
dispatcherelor. Sunt numere descriptive; nu spun care variantă se întreține mai ușor.

## Prima măsurătoare

Parametrii sunt în `results/m1/summary.json`: 30 de perechi, 256 de jocuri, 8 apeluri
de indiciu pe joc (2.048 de apeluri pe pereche, 61.440 pe variantă), 3 runde de
încălzire pe variantă care nu intră în rezultate, seed 2026.

Fiecare pereche începe cu jocuri noi, cu aceleași seed-uri în ambele variante. Ordinea
(care variantă rulează prima) e amestecată cu un seed fix. Cronometrăm doar
apelurile de indiciu, cu `time.perf_counter_ns` și cu garbage collector-ul oprit pe
durata măsurătorii. Crearea jocurilor, afișarea și verificările nu sunt incluse.

Înainte de măsurare, `benchmark.py` compară evenimentele și starea celor 256 de
jocuri în ambele variante, iar după fiecare rundă verifică un hash al stării finale.
Raportul din sumar e mediana rapoartelor Strategy/condiționale calculate pe fiecare
pereche, nu raportul dintre cele două mediane.

## Limite

- un singur puzzle mic, un singur scenariu, un singur calculator și un singur proces;
- procesele din fundal și frecvența procesorului nu sunt controlate;
- cele 30 de perechi sunt repetări ale aceluiași scenariu, nu eșantioane independente;
- timpul măsurat include tot apelul de indiciu, nu doar dispatch-ul;
- nu raportăm p-values, intervale de încredere sau concluzii generale;
- un rezultat în care variantele ies aproape la fel e un rezultat valid.

## Ce urmează

**M2 (săptămâna 12):** mai multe grile și combinații de politici, rulări în procese
separate (pyperf e un model bun pentru asta), măsurători de construcție și memorie
și o extensie făcută în ambele variante, de pildă o politică „ultima literă
nerezolvată”. Stabilim analiza înainte de rulări și publicăm toate rezultatele.

**M3 (săptămâna 14):** analiza finală cu limitele ei, prezentarea finală și articolul
științific în PDF. Tag-urile M2 și M3 le facem la livrare.

## Surse

1. Refactoring.Guru, „Strategy”: https://refactoring.guru/design-patterns/strategy (consultat 15.11.2026).
2. pyperf, „Run benchmarks”: https://pyperf.readthedocs.io/en/latest/run_benchmark.html
   (consultat 15.11.2026). Am folosit doar ideile despre încălzire și zgomot;
   măsurătoarea M1 e scrisă cu biblioteca standard, nu cu pyperf.
