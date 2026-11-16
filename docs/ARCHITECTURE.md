# Arhitectura

```mermaid
flowchart TD
    CLI["CLI: răspunsuri și indicii"] --> Game["Game: validare, stare, RNG"]
    Game --> Port["Dispatcher.select(policy, context, rng)"]
    Port --> C["ConditionalDispatcher: if / elif"]
    Port --> S["StrategyDispatcher: dicționar de HintStrategy"]
    S --> F["FirstLetterStrategy"]
    S --> R["RandomLetterStrategy"]
    S --> W["WordStrategy"]
    C --> Helpers["policies.py: first_cells, random_cells, word_cells"]
    F --> Helpers
    R --> Helpers
    W --> Helpers
    Helpers --> Game
```

`Game` ține grila, literele scrise, celulele blocate, contorul de indicii și
generatorul `Random`. Pentru un indiciu, construiește un `HintContext` cu celulele
nerezolvate ale cuvântului și cere unui dispatcher să aleagă celulele de dezvăluit.
Apoi scrie literele, le blochează și crește contorul. Dispatcherul este singura
piesă care diferă între variante.

```mermaid
sequenceDiagram
    participant CLI
    participant Game
    participant Dispatcher
    participant Policy as policies.py
    CLI->>Game: hint("2A", "random")
    Game->>Game: caută definiția, construiește HintContext
    Game->>Dispatcher: select("random", context, rng)
    Dispatcher->>Policy: random_cells(context, rng)
    Policy-->>Dispatcher: celulele alese
    Dispatcher-->>Game: aceleași celule în ambele variante
    Game->>Game: scrie și blochează literele
    Game-->>CLI: HintResult
```

O definiție sau o politică necunoscută oprește apelul înainte să se atingă starea
sau generatorul aleator. `Puzzle` verifică la creare că grila e dreptunghiulară,
că definițiile sunt unice, că acoperă toate cuvintele de cel puțin două litere
și că nu rămâne nicio celulă fără definiție. Literele din intersecții există o
singură dată, în `Game.letters`.

Diagrama principală apare și în prezentare, desenată cu forme PowerPoint editabile.
