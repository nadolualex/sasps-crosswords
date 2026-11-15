"""Run release checks and persist their real outputs; raises on any failure."""

import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pypdf import PdfReader

from scripts.benchmark import check_equivalence
from scripts.build_presentation import AUTHORS, build_pages
from scripts.code_metrics import collect

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/m1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def command(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    require(result.returncode == 0, f"{args}: {result.stdout}\n{result.stderr}")
    return result.stdout + result.stderr


def main() -> None:
    require(Path.cwd() == ROOT, "Ruleaza verificatorul din radacina proiectului.")
    test_output = command("-m", "unittest", "discover", "-v")
    match = re.search(r"Ran (\d+) tests", test_output)
    require(match is not None, "Lipseste numarul testelor.")
    test_count = int(match.group(1))
    (RESULTS / "tests.txt").write_text(test_output, encoding="utf-8")
    demos = {
        variant: command("-m", "crosswords", "--variant", variant, "--seed", "42", "--demo")
        for variant in ("conditional", "strategy")
    }
    require(demos["conditional"].splitlines()[1:] == demos["strategy"].splitlines()[1:],
            "Demo-urile difera dincolo de antet.")
    for variant, output in demos.items():
        require("Grila rezolvata. Indicii folosite: 3" in output, "Demo incomplet.")
        (RESULTS / f"demo_{variant}.txt").write_text(output, encoding="utf-8")
    summary = json.loads((RESULTS / "summary.json").read_text(encoding="utf-8"))
    with (RESULTS / "raw.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == 2 * summary["repeats"], "Numar incorect de randuri brute.")
    expected = check_equivalence(summary["games_per_trial"], summary["seed"])
    require(expected == summary["equivalence_state_sha256"], "Checksum nereproductibil.")
    samples = {"conditional": [], "strategy": []}
    ratios = []
    for trial in range(1, summary["repeats"] + 1):
        pair = [row for row in rows if int(row["trial"]) == trial]
        require(len(pair) == 2 and {r["variant"] for r in pair} == set(samples),
                "Pereche invalida.")
        require({int(row["order"]) for row in pair} == {1, 2}, "Ordine invalida.")
        per_variant = {}
        for row in pair:
            require(row["state_sha256"] == expected, "Checksum brut invalid.")
            require(int(row["calls"]) == summary["calls_per_trial"], "Numar apeluri invalid.")
            measured = int(row["elapsed_ns"]) / int(row["calls"])
            require(measured > 0 and math.isclose(measured, float(row["ns_per_call"])),
                    "Durata bruta inconsistenta.")
            samples[row["variant"]].append(measured)
            per_variant[row["variant"]] = measured
        ratios.append(per_variant["strategy"] / per_variant["conditional"])
    for variant, values in samples.items():
        quartiles = statistics.quantiles(values, n=4, method="inclusive")
        recomputed = {
            "median_ns_per_call": statistics.median(values),
            "q1_ns_per_call": quartiles[0], "q3_ns_per_call": quartiles[2],
            "min_ns_per_call": min(values), "max_ns_per_call": max(values),
        }
        require(recomputed == summary["metrics"][variant], "Sumar temporal invalid.")
    require(statistics.median(ratios) == summary["median_paired_strategy_over_conditional"],
            "Raport pereche invalid.")
    metrics = json.loads((RESULTS / "code_metrics.json").read_text(encoding="utf-8"))
    require(metrics == collect(), "Metricile codului nu mai corespund surselor.")
    pages = build_pages(summary, metrics)
    require(AUTHORS == ("Nadolu Alex", "Dalya Tobescu"), "Autori neconformi.")
    require(len(pages) == 12 and sum(page.seconds for page in pages) == 570,
            "Numar / durata slide-uri invalide.")
    deck_path = ROOT / "presentation/SASPS_M1_Crosswords.pptx"
    with zipfile.ZipFile(deck_path) as archive:
        require(archive.testzip() is None, "Arhiva PPTX corupta.")
        for name in archive.namelist():
            if name.endswith((".xml", ".rels")):
                data = archive.read(name)
                ET.fromstring(data)
                require(not any(account in data.lower()
                                for account in (b"nadolualex", b"rnadolu_adobe")),
                        "Cont GitHub prezent in PPTX.")
    deck = Presentation(deck_path)
    require(len(deck.slides) == 12, "PPTX nu are 12 slide-uri.")
    manifest = json.loads((ROOT / "presentation/manifest.json").read_text(encoding="utf-8"))
    require(manifest["total_seconds"] == 570 and manifest["qa_seconds"] == 120,
            "Manifest temporal invalid.")
    require(manifest["authors"] == list(AUTHORS) and manifest["contributors_count"] == 2,
            "Contribuitori manifest neconformi.")
    require(deck.core_properties.author == "; ".join(AUTHORS), "Autori metadata PPTX incorecti.")
    for index in (0, 10):
        visible = "\n".join(shape.text for shape in deck.slides[index].shapes if shape.has_text_frame)
        notes = deck.slides[index].notes_slide.notes_text_frame.text
        require(all(author in visible and author in notes for author in AUTHORS),
                "Autorii lipsesc din titlu/contributii sau note.")
    all_text = []
    for index, slide in enumerate(deck.slides):
        notes = slide.notes_slide.notes_text_frame.text
        require(pages[index].notes in notes and f"{pages[index].seconds} secunde" in notes,
                "Note lipsa sau neactualizate.")
        for shape in slide.shapes:
            require(shape.left >= 0 and shape.top >= 0, "Forma cu coordonate negative.")
            require(shape.left + shape.width <= deck.slide_width + 2
                    and shape.top + shape.height <= deck.slide_height + 2,
                    "Forma depaseste slide-ul.")
            if shape.has_text_frame:
                all_text.append(shape.text)
    diagram = deck.slides[4]
    arrows = [shape for shape in diagram.shapes
              if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE
              and shape.auto_shape_type == MSO_SHAPE.RIGHT_ARROW]
    require(len(arrows) >= 4, "Diagrama arhitecturala nu are sageti vizibile.")
    require("StrategyDispatcher" in "\n".join(all_text), "Diagrama nu are nodul Strategy.")
    for variant in samples:
        value = f"{summary['metrics'][variant]['median_ns_per_call'] / 1000:.3f} µs/apel"
        require(value in "\n".join(all_text), "Timpii PPTX nu corespund datelor.")
    pdf_path = ROOT / "presentation/SASPS_M1_Crosswords_slides.pdf"
    reader = PdfReader(pdf_path, strict=True)
    require(len(reader.pages) == 12, "PDF preview nu are 12 pagini.")
    require(all(page.extract_text().strip() for page in reader.pages), "Pagina PDF fara text.")
    pdf_text = "\n".join(page.extract_text() for page in reader.pages)
    require("DOR" in pdf_text, "Demo-ul nu apare in PDF.")
    require(reader.metadata.author == "; ".join(AUTHORS), "Autori metadata PDF incorecti.")
    for index in (0, 10):
        require(all(author in reader.pages[index].extract_text() for author in AUTHORS),
                "Autorii lipsesc din titlu/contributii PDF.")
    academic_text = pdf_text + json.dumps(manifest, ensure_ascii=False) + deck.core_properties.author
    require(not any(account in academic_text.lower() for account in ("nadolualex", "rnadolu_adobe")),
            "Cont GitHub prezent in materialele prezentarii.")
    report = {
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "tests_passed": test_count,
        "demos": "both solved; all output except variant header identical",
        "benchmark": "all raw rows, paired summaries and complete RNG/state checksum verified",
        "pptx": "12 slides; valid ZIP/XML; notes, 570s timing, diagram arrows and shape bounds checked",
        "pdf": "12 readable pages; generated from same layout, not PowerPoint rendering",
        "authors": list(AUTHORS),
        "author_checks": "both names visible on title/contributors and notes; PPTX/PDF/manifest metadata verified; no account names in presentation",
        "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (deck_path, pdf_path, RESULTS / "raw.csv", RESULTS / "summary.json")
        },
        "publication": "not verified by this script; verify remote main and M1 separately",
    }
    (RESULTS / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK: {test_count} tests, 2 demos, raw results, PPTX/PDF (12 slides; 570 secunde).")


if __name__ == "__main__":
    main()
