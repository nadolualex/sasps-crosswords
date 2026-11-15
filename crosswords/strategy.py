from random import Random
from typing import Protocol

from crosswords.policies import HintContext, first_cells, random_cells, word_cells
from crosswords.puzzle import Cell


class HintStrategy(Protocol):
    def select(self, context: HintContext, rng: Random) -> tuple[Cell, ...]:
        ...


class FirstLetterStrategy:
    def select(self, context: HintContext, rng: Random) -> tuple[Cell, ...]:
        return first_cells(context, rng)


class RandomLetterStrategy:
    def select(self, context: HintContext, rng: Random) -> tuple[Cell, ...]:
        return random_cells(context, rng)


class WordStrategy:
    def select(self, context: HintContext, rng: Random) -> tuple[Cell, ...]:
        return word_cells(context, rng)


class StrategyDispatcher:
    def __init__(self) -> None:
        self.strategies: dict[str, HintStrategy] = {
            "first": FirstLetterStrategy(),
            "random": RandomLetterStrategy(),
            "word": WordStrategy(),
        }

    def select(self, policy: str, context: HintContext, rng: Random) -> tuple[Cell, ...]:
        if policy not in self.strategies:
            raise ValueError(f"Politica necunoscuta: {policy}")
        return self.strategies[policy].select(context, rng)
