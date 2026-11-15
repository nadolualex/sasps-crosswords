# Metodologie comparativă — M1

## Întrebarea

Cum schimbă Strategy structura și extensibilitatea selecției de indicii într-un
joc Crosswords, față de un dispatcher `if/elif`, păstrând comportamentul identic?
Nu presupunem că pattern-ul este mai rapid sau obligatoriu pentru trei politici.

## Variabile și controale

Variabila independentă este mecanismul de dispatch/incapsulare:
`ConditionalDispatcher.select` versus `StrategyDispatcher.select` +
obiectele `HintStrategy`. Clasele concrete delegă către aceiași helperi puri
din `policies.py`; ele nu au algoritmi diferiți. În ambele cazuri, `Game`
construiește același `HintContext` și aplică aceleași actualizări ale stării.

Controale: aceeași grilă, definiții, ordinea celulelor, normalizare, validare,
reguli de protejare a literelor, contor, RNG local `random.Random`, seed,
comenzi, UI și timer. În benchmark, fiecare variantă pornește din jocuri noi,
cu aceleași seed-uri `2026 + index`; construcția obiectelor nu este cronometrată.
Nu există input/output sau calcul de checksum în regiunea cronometrată.

Politici:

| Politică | Semantica comună |
|---|---|
| `first` | Prima celulă nerezolvată din cuvânt, în ordinea definiției |
| `random` | O celulă nerezolvată aleasă uniform cu RNG-ul jocului |
| `word` | Toate celulele nerezolvate din cuvânt |

„Nerezolvată” înseamnă goală sau incorectă. Un cuvânt corect este no-op,
fără consum de RNG. Politică/definiție necunoscută și răspuns invalid produc
`ValueError`; UI afișează eroarea. Un răspuns ce contrazice o literă dezvăluită
este respins fără schimbări parțiale. Literele corecte introduse manual nu sunt
protejate automat și pot fi șterse. Politicile sunt alese de client prin CLI,
nu există selecție adaptivă ascunsă.

## Ipoteze și metrici

| ID | Ipoteză / criteriu | Măsurare | Stadiu |
|---|---|---|---|
| E0 | Evenimente, stări și erori identice pentru aceleași comenzi/seed-uri | Egalitate exactă, inclusiv `Random.getstate()` | Testat pe corpusul M1; nu probă formală |
| H1 | O politică nouă poate separa responsabilitățile în Strategy, cu cost de boilerplate | Fișiere/linii modificate, puncte de modificare, regresii; durată numai dacă observată real | Experiment de extensie planificat M2 |
| H2 | Strategy nu are un avantaj de timp presupus | Mediană, Q1/Q3 per apel; raport median per pereche | Pilot M1 exploratoriu |
| H3 | Clasele suplimentare pot avea cost inițial | Timp de construcție și memorie cu aceeași durată de viață | Planificat M2 |

`code_metrics.json` numără linii ne-goale/ne-comentariu, clase (incluzând
Protocol) și noduri AST `If` doar din metoda dispatcherului. Aceste numere
**nu** sunt o măsură globală a mentenabilității sau o comparație a complexității
întregului proiect. Condiționalele sunt un baseline rezonabil pentru trei cazuri;
mutarea lor într-un registru nu elimină toate condițiile din aplicație.

## Pilotul măsurat

Comanda exactă este în README și metadatele în `results/m1/summary.json`.
30 perechi × 256 jocuri × 8 apeluri = **61.440 apeluri cronometrate per variantă**.
3 încălziri complete per variantă, excluse din rezultate.
Ordinea A/B în fiecare pereche este amestecată cu seed fix; nu este paralelă.
GC este colectat înainte de fiecare lot și dezactivat numai în regiunea
cronometrată, apoi restaurat. Folosim `time.perf_counter_ns`.
Cele 8 comenzi sunt explicit în `WORKLOAD`; includ politici mixte și no-op-uri.

Verificarea necronometrată compară fiecare eveniment și fiecare snapshot pentru
toate cele 256 jocuri. Fiecare lot măsurat este apoi verificat prin SHA-256
al snapshot-urilor finale, incluzând RNG. Rândurile CSV includ ordinea,
durata, numărul de apeluri, ns/apel și checksum. Raportul Strategy/condiționale
este mediana rapoartelor în perechi, **nu raportul medianelor marginale**.

## Amenințări la validitate

Un singur puzzle mic, un singur workload, un singur interpreter/proces/host.
CPU, temperatură și procese concurente nu sunt controlate complet. Cele 30
perechi sunt repetări tehnice, nu 30 utilizatori independenți. Apelul măsurat
include mult motor comun, deci nu cuantifică separat costul dispatch-ului.
Construcția registrului/obiectelor este exclusă; acest cost trebuie evaluat separat.
Nu raportăm p-value, semnificație, interval de încredere sau concluzie cauzală
generală. Cifrele negative sau aproape egale sunt rezultate acceptabile.
Reproducerea în aceeași versiune Python păstrează stările, nu timpul exact.

## M2 și M3, încă neexecutate

M2 (săptămâna 12): mai multe grile și distribuții de politici; loturi și seed-uri
publicate; replicări în procese separate cu protocol predefinit; măsurarea
construcției/memoriei; o extensie controlată („ultima literă nerezolvată”) în
ambele variante folosind același helper și aceleași teste. Se păstrează diffs
reale și regresiile; nu se inventează timpi de dezvoltare sau participanți.
Stabilim înainte de rulare unitatea de analiză și intervalele de încredere
potrivite replicărilor independente. Nu selectăm doar rulările favorabile.

M3 (săptămâna 14): completarea experimentelor, discuția limitelor și a
rezultatelor negative, PPTX final și **articol științific PDF separat**.
Tag-urile M2/M3 se creează numai atunci. M1 nu pretinde livrarea articolului.

## Referințe

1. Refactoring.Guru, „Strategy”: https://refactoring.guru/design-patterns/strategy
   — definiție, context și interfață; consultat 15.11.2026.
2. pyperf, „Run benchmarks”: https://pyperf.readthedocs.io/en/latest/run_benchmark.html
   — încălzire, replicări/procese și zgomot; consultat 15.11.2026.
   Pilotul folosește stdlib, **nu pyperf**.

Suportul de curs a servit drept context al disciplinei; nu este copiat și nu
este tratat drept enunț al temei. Tema confirmată este Crosswords.
