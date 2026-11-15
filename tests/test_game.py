import random
import unittest

from crosswords.engine import create_game
from crosswords.policies import POLICY_NAMES
from crosswords.puzzle import DEMO_PUZZLE, Entry, Puzzle

VARIANTS = ("conditional", "strategy")


class GameRulesTests(unittest.TestCase):
    def test_initial_grid(self):
        for variant in VARIANTS:
            game = create_game(variant)
            self.assertEqual(len(game.letters), 11)
            self.assertFalse(game.solved)
            self.assertEqual(game.hints_used, 0)

    def test_correct_answers_solve(self):
        for variant in VARIANTS:
            game = create_game(variant)
            for entry in game.puzzle.entries:
                game.answer(entry.id, game.puzzle.solution(entry))
            self.assertTrue(game.solved)

    def test_crossing_is_shared(self):
        for variant in VARIANTS:
            game = create_game(variant)
            game.answer("1A", "CAL")
            self.assertEqual(game.letters[(0, 0)], "C")
            game.answer("1D", "CODUL")
            self.assertEqual(game.letters[(4, 0)], "L")

    def test_lowercase_and_erasure(self):
        for variant in VARIANTS:
            game = create_game(variant)
            game.answer("1A", " cal ")
            self.assertEqual(game.letters[(0, 1)], "A")
            game.answer("1A", "---")
            self.assertEqual(game.letters[(0, 1)], "")

    def test_invalid_answer_atomic(self):
        for variant in VARIANTS:
            for text in ("", "CA", "CALS", "C1L", "CĂL", "C L"):
                with self.subTest(variant=variant, text=text):
                    game = create_game(variant)
                    before = game.snapshot()
                    with self.assertRaises(ValueError):
                        game.answer("1A", text)
                    self.assertEqual(before, game.snapshot())

    def test_locked_cell_conflict_atomic(self):
        for variant in VARIANTS:
            game = create_game(variant)
            game.hint("1A", "first")
            for text in ("XAL", "---"):
                before = game.snapshot()
                with self.assertRaises(ValueError):
                    game.answer("1A", text)
                self.assertEqual(before, game.snapshot())
            game.answer("1A", "CAL")

    def test_first_skips_correct_and_repairs_wrong(self):
        for variant in VARIANTS:
            game = create_game(variant)
            game.answer("1A", "CX-")
            event = game.hint("1A", "first")
            self.assertEqual(event.revealed, (((0, 1), "A"),))

    def test_word_reveals_only_unresolved(self):
        for variant in VARIANTS:
            game = create_game(variant)
            game.answer("1A", "C--")
            event = game.hint("1A", "word")
            self.assertEqual(event.revealed, (((0, 1), "A"), ((0, 2), "L")))
            self.assertEqual(game.hints_used, 1)

    def test_completed_entry_noop_without_rng_consumption(self):
        for variant in VARIANTS:
            game = create_game(variant)
            game.answer("1A", "CAL")
            for policy in POLICY_NAMES:
                before = game.snapshot()
                self.assertEqual(game.hint("1A", policy).revealed, ())
                self.assertEqual(before, game.snapshot())

    def test_unknown_policy_and_entry_atomic(self):
        for variant in VARIANTS:
            game = create_game(variant)
            for entry_id, policy in (("1A", "bad"), ("bad", "random"), ("1A", "")):
                before = game.snapshot()
                with self.assertRaises(ValueError):
                    game.hint(entry_id, policy)
                self.assertEqual(before, game.snapshot())
            with self.assertRaises(ValueError):
                game.answer("bad", "CAL")

    def test_random_reproducible(self):
        for variant in VARIANTS:
            for seed in range(30):
                a, b = create_game(variant, seed), create_game(variant, seed)
                for _ in range(5):
                    self.assertEqual(a.hint("1D", "random"), b.hint("1D", "random"))
                    self.assertEqual(a.snapshot(), b.snapshot())
                self.assertEqual(len(a.locked), 5)

    def test_invalid_variant(self):
        with self.assertRaises(ValueError):
            create_game("bad")


class EquivalenceTests(unittest.TestCase):
    def test_all_policies_all_entries_many_seeds(self):
        for seed in range(100):
            for policy in POLICY_NAMES:
                a, b = (create_game(v, seed) for v in VARIANTS)
                for entry in DEMO_PUZZLE.entries:
                    for _ in range(len(entry.cells) + 1):
                        self.assertEqual(a.hint(entry.id, policy), b.hint(entry.id, policy))
                        self.assertEqual(a.snapshot(), b.snapshot())

    def test_mixed_commands_with_errors_and_rng(self):
        for seed in range(100):
            schedule = random.Random(seed + 1000)
            a, b = (create_game(v, seed) for v in VARIANTS)
            for _ in range(100):
                entry_id = schedule.choice(("1A", "2A", "3A", "1D", "bad"))
                if schedule.random() < 0.6:
                    args = (entry_id, schedule.choice((*POLICY_NAMES, "bad")))
                    method = "hint"
                else:
                    args = (entry_id, schedule.choice(("CAL", "DOR", "LAC", "CODUL", "---", "?", "XXX")))
                    method = "answer"
                outcomes = []
                for game in (a, b):
                    try:
                        outcomes.append(("ok", getattr(game, method)(*args)))
                    except ValueError as error:
                        outcomes.append(("error", str(error)))
                self.assertEqual(outcomes[0], outcomes[1])
                self.assertEqual(a.snapshot(), b.snapshot())


class PuzzleValidationTests(unittest.TestCase):
    def test_invalid_shapes_and_symbols(self):
        for rows in ((), ("",), ("AB", "C"), ("A?",), ("aB",)):
            with self.assertRaises(ValueError):
                Puzzle(rows, ())

    def test_missing_or_duplicate_entries(self):
        with self.assertRaises(ValueError):
            Puzzle(DEMO_PUZZLE.rows, DEMO_PUZZLE.entries[:-1])
        with self.assertRaises(ValueError):
            Puzzle(DEMO_PUZZLE.rows, DEMO_PUZZLE.entries + (DEMO_PUZZLE.entries[0],))

    def test_invalid_cells_rejected(self):
        with self.assertRaises(ValueError):
            Puzzle(("AB",), (Entry("1A", "invalid", ((0, 0), (0, 2))),))

    def test_orphan_cell_rejected(self):
        with self.assertRaises(ValueError):
            Puzzle(("A",), ())


if __name__ == "__main__":
    unittest.main()
