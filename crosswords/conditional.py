from random import Random

from crosswords.policies import HintContext, first_cells, random_cells, word_cells
from crosswords.puzzle import Cell


class ConditionalDispatcher:
    def select(self, policy: str, context: HintContext, rng: Random) -> tuple[Cell, ...]:
        if policy == "first":
            return first_cells(context, rng)
        elif policy == "random":
            return random_cells(context, rng)
        elif policy == "word":
            return word_cells(context, rng)
        raise ValueError(f"Politica necunoscuta: {policy}")
