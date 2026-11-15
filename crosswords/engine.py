from dataclasses import dataclass
from random import Random

from crosswords.conditional import ConditionalDispatcher
from crosswords.policies import Dispatcher, HintContext
from crosswords.puzzle import Cell, DEMO_PUZZLE, Puzzle
from crosswords.strategy import StrategyDispatcher


@dataclass(frozen=True)
class HintResult:
    entry_id: str
    policy: str
    revealed: tuple[tuple[Cell, str], ...]


class Game:
    def __init__(self, dispatcher: Dispatcher, seed: int = 0, puzzle: Puzzle = DEMO_PUZZLE):
        self.dispatcher = dispatcher
        self.puzzle = puzzle
        self.rng = Random(seed)
        self.letters: dict[Cell, str] = {cell: "" for cell in puzzle.cells}
        self.locked: set[Cell] = set()
        self.hints_used = 0

    @property
    def solved(self) -> bool:
        return all(self.letters[cell] == self.puzzle.rows[cell[0]][cell[1]]
                   for cell in self.puzzle.cells)

    def answer(self, entry_id: str, text: str) -> None:
        entry = self.puzzle.entry(entry_id)
        value = text.strip().upper()
        if len(value) != len(entry.cells) or any(
            c != "-" and not ("A" <= c <= "Z") for c in value
        ):
            raise ValueError("Raspunsul trebuie sa aiba lungimea ceruta si numai A-Z / -.")
        updates = dict(zip(entry.cells, ("" if c == "-" else c for c in value)))
        if any(cell in self.locked and letter != self.letters[cell]
               for cell, letter in updates.items()):
            raise ValueError("Nu se pot modifica sau sterge literele dezvaluite.")
        self.letters.update(updates)

    def hint(self, entry_id: str, policy: str) -> HintResult:
        entry = self.puzzle.entry(entry_id)
        context = HintContext(tuple(
            cell for cell in entry.cells
            if self.letters[cell] != self.puzzle.rows[cell[0]][cell[1]]
        ))
        selected = self.dispatcher.select(policy, context, self.rng)
        revealed = tuple((cell, self.puzzle.rows[cell[0]][cell[1]]) for cell in selected)
        for cell, letter in revealed:
            self.letters[cell] = letter
            self.locked.add(cell)
        if revealed:
            self.hints_used += 1
        return HintResult(entry_id, policy, revealed)

    def snapshot(self) -> tuple:
        return (tuple(sorted(self.letters.items())), tuple(sorted(self.locked)),
                self.hints_used, self.solved, self.rng.getstate())

    def render(self) -> str:
        return "\n".join(" ".join(
            "#" if c == "#" else self.letters[(r, col)] or "."
            for col, c in enumerate(row)
        ) for r, row in enumerate(self.puzzle.rows))


def create_game(variant: str, seed: int = 0) -> Game:
    if variant == "conditional":
        return Game(ConditionalDispatcher(), seed)
    if variant == "strategy":
        return Game(StrategyDispatcher(), seed)
    raise ValueError(f"Varianta necunoscuta: {variant}")
