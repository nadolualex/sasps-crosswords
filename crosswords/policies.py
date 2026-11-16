"""Algoritmii de indiciu, folosiți la fel de ambele variante."""

from dataclasses import dataclass
from random import Random
from typing import Protocol

from crosswords.puzzle import Cell

POLICY_NAMES = ("first", "random", "word")


@dataclass(frozen=True)
class HintContext:
    unresolved: tuple[Cell, ...]


class Dispatcher(Protocol):
    def select(self, policy: str, context: HintContext, rng: Random) -> tuple[Cell, ...]:
        ...


def first_cells(context: HintContext, rng: Random) -> tuple[Cell, ...]:
    return context.unresolved[:1]


def random_cells(context: HintContext, rng: Random) -> tuple[Cell, ...]:
    return (rng.choice(context.unresolved),) if context.unresolved else ()


def word_cells(context: HintContext, rng: Random) -> tuple[Cell, ...]:
    return context.unresolved
