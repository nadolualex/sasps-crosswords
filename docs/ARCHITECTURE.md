# Arhitectură și variante

```mermaid
flowchart TD
    CLI["CLI comun: răspuns / indiciu"] --> Game["Game: validare + stare + RNG"]
    Game --> Port["Dispatcher.select(policy, context, rng)"]
    Port --> C["ConditionalDispatcher: if / elif"]
    Port --> S["StrategyDispatcher: registru de HintStrategy"]
    S --> F["FirstLetterStrategy"]
    S --> R["RandomLetterStrategy"]
    S --> W["WordStrategy"]
    C --> Helpers["Helperi comuni: first_cells / random_cells / word_cells"]
    F --> Helpers
    R --> Helpers
    W --> Helpers
    Helpers --> Selected["Celule selectate"]
    Selected --> Apply["Game: actualizare + protejare + contor"]
```

`Game` este contextul aplicației și depinde de un Protocol `Dispatcher`.
În varianta Strategy, selecția după cheia primită de la client aparține
dispatcherului; obiectul concret satisface Protocol-ul `HintStrategy`.
Registrul este creat o dată per joc, strategiile sunt fără stare.
Algoritmul poate fi înlocuit fără schimbarea motorului. În baseline, același
contract public este implementat prin `if/elif`, fără cod redundant.

```mermaid
sequenceDiagram
    participant Client as CLI
    participant Game
    participant Dispatch as Dispatcher
    participant Policy as Helper comun
    Client->>Game: hint("2A", "random")
    Game->>Game: validează definiția; construiește HintContext
    Game->>Dispatch: select(policy, context, rng)
    Dispatch->>Policy: random_cells(context, rng)
    Policy-->>Dispatch: celule selectate
    Dispatch-->>Game: aceleași celule în ambele variante
    Game->>Game: scrie soluția, protejează, contor dacă există delta
    Game-->>Client: HintResult
```

Politica necunoscută este respinsă înainte de folosirea RNG/mutarea stării.
Cu definiție necunoscută, validarea se oprește înainte de dispatch. Grila este
validată structural: definiții unice, toate secvențele orizontale/verticale
de minimum două celule, fără celule neacoperite. Toate literele de la o
intersecție au o singură sursă de adevăr în `Game.letters`.

Diagramele principale sunt și **forme vizibile/editabile în PPTX**, nu
dependente de randarea Mermaid.
