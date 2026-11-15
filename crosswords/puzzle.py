from dataclasses import dataclass

Cell = tuple[int, int]


@dataclass(frozen=True)
class Entry:
    id: str
    clue: str
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class Puzzle:
    rows: tuple[str, ...]
    entries: tuple[Entry, ...]

    def __post_init__(self) -> None:
        if not self.rows or not self.rows[0]:
            raise ValueError("Grila nu poate fi goala.")
        width = len(self.rows[0])
        if any(len(row) != width for row in self.rows):
            raise ValueError("Grila trebuie sa fie dreptunghiulara.")
        if any(c != "#" and not ("A" <= c <= "Z") for row in self.rows for c in row):
            raise ValueError("Solutiile folosesc numai A-Z si #.")
        if len({entry.id for entry in self.entries}) != len(self.entries):
            raise ValueError("Identificatorii definitiilor trebuie sa fie unici.")
        runs = set()
        for dr, dc in ((0, 1), (1, 0)):
            for r, row in enumerate(self.rows):
                for c, value in enumerate(row):
                    if value == "#":
                        continue
                    pr, pc = r - dr, c - dc
                    if pr >= 0 and pc >= 0 and self.rows[pr][pc] != "#":
                        continue
                    cells = []
                    nr, nc = r, c
                    while nr < len(self.rows) and nc < width and self.rows[nr][nc] != "#":
                        cells.append((nr, nc))
                        nr, nc = nr + dr, nc + dc
                    if len(cells) > 1:
                        runs.add(tuple(cells))
        declared = [entry.cells for entry in self.entries]
        if len(set(declared)) != len(declared) or set(declared) != runs:
            raise ValueError("Definitiile trebuie sa acopere exact cuvintele grilei.")
        covered = {cell for entry in self.entries for cell in entry.cells}
        if covered != set(self.cells):
            raise ValueError("Exista celule fara definitie.")

    @property
    def cells(self) -> tuple[Cell, ...]:
        return tuple(
            (r, c)
            for r, row in enumerate(self.rows)
            for c, value in enumerate(row)
            if value != "#"
        )

    def entry(self, entry_id: str) -> Entry:
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        raise ValueError(f"Definitie necunoscuta: {entry_id}")

    def solution(self, entry: Entry) -> str:
        return "".join(self.rows[r][c] for r, c in entry.cells)


DEMO_PUZZLE = Puzzle(
    rows=("CAL##", "O####", "DOR##", "U####", "LAC##"),
    entries=(
        Entry("1A", "Animal domestic folosit la calarie (3)", ((0, 0), (0, 1), (0, 2))),
        Entry("2A", "Sentiment de lipsa a unei persoane dragi (3)", ((2, 0), (2, 1), (2, 2))),
        Entry("3A", "Intindere de apa statatoare (3)", ((4, 0), (4, 1), (4, 2))),
        Entry("1D", "Setul de instructiuni al programului, cu articol hotarat (5)",
              ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0))),
    ),
)
