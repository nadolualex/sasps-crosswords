"""Paired, repeatable full-engine hint workload; no statistical inference."""

import argparse
import csv
from datetime import datetime, timezone
import gc
import hashlib
import json
import platform
from pathlib import Path
import random
import statistics
import sys
from time import perf_counter_ns

from crosswords.engine import Game, create_game

WORKLOAD = (
    ("1A", "first"), ("2A", "random"), ("1D", "random"), ("3A", "word"),
    ("1A", "random"), ("1D", "word"), ("2A", "first"), ("2A", "word"),
)
VARIANTS = ("conditional", "strategy")


def prepare(variant: str, games: int, seed: int) -> list[Game]:
    return [create_game(variant, seed + index) for index in range(games)]


def run(games: list[Game]) -> None:
    for game in games:
        for entry_id, policy in WORKLOAD:
            game.hint(entry_id, policy)


def digest(games: list[Game]) -> str:
    return hashlib.sha256(repr([game.snapshot() for game in games]).encode()).hexdigest()


def check_equivalence(games: int, seed: int) -> str:
    a, b = (prepare(variant, games, seed) for variant in VARIANTS)
    for ga, gb in zip(a, b):
        for entry_id, policy in WORKLOAD:
            if ga.hint(entry_id, policy) != gb.hint(entry_id, policy):
                raise RuntimeError("Evenimentele variantelor difera.")
            if ga.snapshot() != gb.snapshot():
                raise RuntimeError("Starile / RNG ale variantelor difera.")
    return digest(a)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=30)
    parser.add_argument("--games", type=int, default=256)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("results/m1"))
    args = parser.parse_args()
    if args.repeats < 2 or args.games < 1 or args.warmups < 0:
        parser.error("repeats >= 2, games >= 1, warmups >= 0")
    expected = check_equivalence(args.games, args.seed)
    for _ in range(args.warmups):
        for variant in VARIANTS:
            run(prepare(variant, args.games, args.seed))
    rows = []
    order_rng = random.Random(args.seed)
    for trial in range(args.repeats):
        order = list(VARIANTS)
        order_rng.shuffle(order)
        for order_index, variant in enumerate(order):
            batch = prepare(variant, args.games, args.seed)
            gc.collect()
            was_enabled = gc.isenabled()
            gc.disable()
            try:
                start = perf_counter_ns()
                run(batch)
                elapsed = perf_counter_ns() - start
            finally:
                if was_enabled:
                    gc.enable()
            observed = digest(batch)
            if observed != expected:
                raise RuntimeError("Checksum diferit dupa rularea masurata.")
            rows.append({
                "trial": trial + 1, "order": order_index + 1, "variant": variant,
                "elapsed_ns": elapsed, "calls": args.games * len(WORKLOAD),
                "ns_per_call": elapsed / (args.games * len(WORKLOAD)),
                "state_sha256": observed,
            })
    values = {
        variant: [row["ns_per_call"] for row in rows if row["variant"] == variant]
        for variant in VARIANTS
    }
    metrics = {}
    for variant, sample in values.items():
        quartiles = statistics.quantiles(sample, n=4, method="inclusive")
        metrics[variant] = {
            "median_ns_per_call": statistics.median(sample),
            "q1_ns_per_call": quartiles[0],
            "q3_ns_per_call": quartiles[2],
            "min_ns_per_call": min(sample),
            "max_ns_per_call": max(sample),
        }
    ratios = [s / c for c, s in zip(values["conditional"], values["strategy"])]
    summary = {
        "status": "exploratory_single_machine_no_statistical_inference",
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "timer": "time.perf_counter_ns",
        "gc": "disabled only during timing; collected before each timed batch",
        "seed": args.seed,
        "repeats": args.repeats,
        "games_per_trial": args.games,
        "warmups_per_variant": args.warmups,
        "calls_per_trial": args.games * len(WORKLOAD),
        "workload": WORKLOAD,
        "excludes": ["game/dispatcher construction", "I/O", "checksum", "correctness checks"],
        "includes": ["context creation", "dispatch", "policy algorithm", "state mutation"],
        "equivalence_state_sha256": expected,
        "metrics": metrics,
        "median_paired_strategy_over_conditional": statistics.median(ratios),
        "limitations": [
            "One tiny puzzle, one workload and one machine.",
            "Fixed seeds and identical games are intentional controls, not independent users.",
            "Timing noise, CPU frequency and competing processes are uncontrolled.",
            "Full-engine timings do not isolate dispatch cost numerically.",
            "No p-values, confidence intervals or general performance claims.",
            "Construction/memory cost and extension effort are not measured at M1.",
        ],
    }
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "raw.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    c, s = (metrics[v]["median_ns_per_call"] / 1000 for v in VARIANTS)
    report = (
        "# Rezultate M1 — exploratorii\n\n"
        f"Rulare reală UTC: {summary['measured_at_utc']}.\n\n"
        f"{args.repeats} perechi × {args.games} jocuri × {len(WORKLOAD)} apeluri; "
        f"{args.warmups} încălziri per variantă. Seed: {args.seed}.\n\n"
        "| Variantă | Mediană µs/apel | Q1–Q3 µs/apel |\n"
        "|---|---:|---:|\n"
    )
    for variant in VARIANTS:
        m = metrics[variant]
        report += (f"| {variant} | {m['median_ns_per_call'] / 1000:.3f} | "
                   f"{m['q1_ns_per_call'] / 1000:.3f}–{m['q3_ns_per_call'] / 1000:.3f} |\n")
    report += (
        f"\nRaport median pereche Strategy / condiționale: "
        f"{summary['median_paired_strategy_over_conditional']:.3f}. "
        "Peste 1 înseamnă Strategy mai lent în acest workload.\n\n"
        "Nu este o concluzie statistică și nu demonstrează superioritatea unui design. "
        "Se măsoară întregul apel de indiciu, nu doar dispatch-ul. "
        "Algoritmii și stările finale/RNG sunt identici; "
        "verificările și crearea jocurilor sunt în afara cronometrării.\n\n"
        "Date brute: `raw.csv`; mediu, parametri, limite și checksum: `summary.json`. "
        "Aceeași comandă reproduce protocolul, nu valori temporale identice.\n"
    )
    (args.output / "REPORT.md").write_text(report, encoding="utf-8")
    print(f"Rezultate: {args.output}; conditional={c:.3f} us; strategy={s:.3f} us")


if __name__ == "__main__":
    main()
