# Prima măsurătoare M1 (preliminară)

Rulată la 2026-11-15T18:33:53.113576+00:00 (UTC).

30 perechi, 256 jocuri, 8 apeluri pe joc; 3 runde de încălzire pe variantă. Seed: 2026.

| Variantă | Mediană µs/apel | Q1–Q3 µs/apel |
|---|---:|---:|
| conditional | 1.100 | 1.078–1.167 |
| strategy | 1.162 | 1.139–1.218 |

Raport median pe perechi, Strategy / if-elif: 1.044. Peste 1 înseamnă că Strategy a ieșit mai lent în acest test.

Rezultatul nu e o concluzie statistică și nu arată că un design e mai bun decât altul. Se măsoară tot apelul de indiciu, nu doar alegerea politicii. Algoritmii, starea finală și numerele aleatoare sunt la fel în ambele variante; crearea jocurilor și verificările nu sunt cronometrate.

Datele brute sunt în `raw.csv`, iar parametrii, limitele și checksum-ul în `summary.json`. Aceeași comandă repetă protocolul, dar nu va da exact aceiași timpi.
