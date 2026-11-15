# Rezultate M1 — exploratorii

Rulare reală UTC: 2026-11-15T18:33:53.113576+00:00.

30 perechi × 256 jocuri × 8 apeluri; 3 încălziri per variantă. Seed: 2026.

| Variantă | Mediană µs/apel | Q1–Q3 µs/apel |
|---|---:|---:|
| conditional | 1.100 | 1.078–1.167 |
| strategy | 1.162 | 1.139–1.218 |

Raport median pereche Strategy / condiționale: 1.044. Peste 1 înseamnă Strategy mai lent în acest workload.

Nu este o concluzie statistică și nu demonstrează superioritatea unui design. Se măsoară întregul apel de indiciu, nu doar dispatch-ul. Algoritmii și stările finale/RNG sunt identici; verificările și crearea jocurilor sunt în afara cronometrării.

Date brute: `raw.csv`; mediu, parametri, limite și checksum: `summary.json`. Aceeași comandă reproduce protocolul, nu valori temporale identice.
