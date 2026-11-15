import argparse
import shlex

from crosswords.engine import Game, create_game


def execute(game: Game, command: str) -> bool:
    parts = shlex.split(command)
    if not parts:
        return True
    if parts == ["quit"]:
        return False
    if parts == ["show"]:
        print(game.render())
    elif parts == ["clues"]:
        for entry in game.puzzle.entries:
            print(f"{entry.id}: {entry.clue}")
    elif len(parts) == 3 and parts[0] == "answer":
        game.answer(parts[1], parts[2])
        print(game.render())
    elif len(parts) == 3 and parts[0] == "hint":
        result = game.hint(parts[1], parts[2])
        print(f"Indiciu: {result.revealed or 'cuvant deja rezolvat'}")
        print(game.render())
    else:
        raise ValueError("Comenzi: show | clues | answer ID TEXT | hint ID first/random/word | quit")
    if game.solved:
        print(f"Felicitari! Grila rezolvata. Indicii folosite: {game.hints_used}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Crosswords: conditionale versus Strategy")
    parser.add_argument("--variant", choices=("conditional", "strategy"), default="strategy")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--demo", action="store_true", help="Ruleaza un scenariu fara input.")
    args = parser.parse_args()
    game = create_game(args.variant, args.seed)
    print(f"Crosswords | {args.variant} | seed={args.seed}")
    execute(game, "clues")
    execute(game, "show")
    if args.demo:
        for command in ("hint 1A first", "hint 2A random", "hint 1D word",
                        "answer 1A CAL", "answer 2A DOR", "answer 3A LAC"):
            print(f"> {command}")
            execute(game, command)
        if not game.solved:
            raise RuntimeError("Scenariul demo nu a rezolvat grila.")
        return
    print("Ajutor: show | clues | answer 1A CAL | hint 1A random | quit")
    while True:
        try:
            command = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nJoc inchis.")
            break
        try:
            if not execute(game, command):
                break
        except ValueError as error:
            print(f"Eroare: {error}")


if __name__ == "__main__":
    main()
