"""Generate the M1 PPTX and slide-only PDF from one explicit layout."""

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import reportlab

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "presentation"
W, H = 13.333333, 7.5
BG, PANEL, WHITE, MUTED = "101A2C", "1B2B43", "F5F7FC", "B8C7DD"
TEAL, GOLD, BLUE = "5BD8BB", "F1BE68", "88B4FF"


def fonts() -> str:
    mac = Path("/System/Library/Fonts/Supplemental")
    linux = Path("/usr/share/fonts/truetype/dejavu")
    bundled = Path(reportlab.__file__).parent / "fonts"
    choices = (
        (mac / "Arial.ttf", mac / "Arial Bold.ttf", "Arial"),
        (linux / "DejaVuSans.ttf", linux / "DejaVuSans-Bold.ttf", "DejaVu Sans"),
        (bundled / "Vera.ttf", bundled / "VeraBd.ttf", "Bitstream Vera Sans"),
    )
    for normal, bold, family in choices:
        if normal.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("Deck", str(normal)))
            pdfmetrics.registerFont(TTFont("DeckBold", str(bold)))
            return family
    raise RuntimeError("Nu exista font TTF pentru export PDF.")


FONT = fonts()


class Page:
    def __init__(self, title: str, seconds: int, notes: str):
        self.title, self.seconds, self.notes = title, seconds, notes
        self.items: list[dict] = []

    def box(self, x, y, w, h, fill=PANEL, line=None):
        self.items.append(dict(kind="box", x=x, y=y, w=w, h=h, fill=fill, line=line))

    def text(self, x, y, w, h, text, size=20, color=WHITE, bold=False):
        font = "DeckBold" if bold else "Deck"
        for character in text:
            if not character.isspace() and ord(character) not in pdfmetrics.getFont(font).face.charToGlyph:
                raise ValueError(f"Fontul nu acopera caracterul: {character!r}")
        lines = []
        for paragraph in text.split("\n"):
            current = ""
            for word in paragraph.split():
                candidate = f"{current} {word}".strip()
                if pdfmetrics.stringWidth(candidate, font, size) > (w * 72 - 8):
                    if not current:
                        raise ValueError(f"Cuvant prea lat: {word}")
                    lines.append(current)
                    current = word
                else:
                    current = candidate
            lines.append(current)
        if len(lines) * size * 1.2 > h * 72 - 4:
            raise ValueError(f"Text prea inalt pe slide '{self.title}': {text[:80]}")
        self.items.append(dict(kind="text", x=x, y=y, w=w, h=h, lines=lines,
                               size=size, color=color, bold=bold))

    def arrow(self, x, y, w, h=0.24, color=TEAL):
        self.items.append(dict(kind="arrow", x=x, y=y, w=w, h=h, fill=color))

    def heading(self, index: int):
        self.text(.55, .25, 12, .35, "SASPS  /  MILESTONE 1", 12, TEAL, True)
        self.text(.55, .78, 12.2, .7, self.title, 30, WHITE, True)
        self.text(.55, 7.13, 10.9, .25, "Crosswords  •  Prototip comparativ  •  15.11.2026", 10, MUTED)
        self.text(12, 7.13, .75, .25, f"{index:02d} / 12", 10, MUTED)

    def card(self, x, y, w, h, title, body, accent=TEAL, size=20):
        self.box(x, y, w, h)
        self.box(x, y, .06, h, accent)
        self.text(x + .25, y + .2, w - .5, .65, title, 22, accent, True)
        self.text(x + .25, y + 1, w - .5, h - 1.15, body, size)

    def grid(self, x, y, size, rows):
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.box(x + c * size, y + r * size, size - .03, size - .03,
                         "334055" if value == "#" else "E8F4F0")
                if value != "#":
                    self.text(x + c * size + .1, y + r * size + .09,
                              size - .16, size - .12, value, 23, BG, True)


def build_pages(summary: dict, metrics: dict) -> list[Page]:
    pages = []
    p = Page("Crosswords: Strategy vs condiționale", 25,
             "Introduceți tema confirmată și delimitarea: acesta este M1, nu M3. "
             "Același joc și aceiași algoritmi, două mecanisme de dispatch. "
             "Nu anticipăm un câștig de performanță. Numele academic și echipa trebuie confirmate.")
    p.text(.65, 1.95, 8.5, 1.75, "Același joc.\nTrei politici.\nDouă mecanisme de selecție.", 32, WHITE, True)
    p.text(.65, 4.25, 7.2, 1.25, "Investigăm structura și extensibilitatea, fără a schimba regulile sau a penaliza baseline-ul.", 23, MUTED)
    p.box(.65, 6.05, 7.9, .55, PANEL)
    p.text(.85, 6.15, 7.5, .35, "M1: prototip + pilot exploratoriu  |  9:30 + 2 min Q&A", 16, TEAL, True)
    p.grid(9.2, 2.1, .61, ("CAL##", "O####", "DOR##", "U####", "LAC##"))
    p.text(9.2, 5.45, 3.5, .8, "Cont: nadolualex\nNume / echipă: de completat", 16, MUTED)
    pages.append(p)

    p = Page("Problema, obiectivele și aplicația", 40,
             "Jucătorul completează definiții și poate solicita indicii. "
             "Intersecțiile au o singură stare. Obiectivul este separarea variației, "
             "nu schimbarea jocului. Grila mică este deliberată pentru un demo verificabil.")
    p.card(.6, 1.75, 6.65, 4.65, "Un joc mic, complet demonstrabil",
           "Grilă 5×5, 11 celule, 4 definiții originale.\n"
           "Răspunsuri, ștergere și verificarea câștigului.\n"
           "Indicii: prima literă, literă aleatoare, cuvânt.\n"
           "Litere dezvăluite protejate; erori explicite.", size=21)
    p.text(7.75, 1.9, 4.8, .6, "Ce comparăm?", 24, TEAL, True)
    p.text(7.75, 2.75, 4.8, 2.1,
           "Selecția / delegarea politicii.\nNu comparăm două jocuri diferite.\nNu schimbăm algoritmii de indicii.", 23)
    p.text(7.75, 5.25, 4.8, 1.3, "Criteriu esențial: comportament identic la aceleași comenzi și seed-uri.", 21, GOLD)
    pages.append(p)

    p = Page("Variante investigate: motivație și cost", 40,
             "Strategy încapsulează algoritmi interschimbabili printr-o interfață. "
             "Clientul alege cheia, dispatcherul selectează obiectul, motorul delegă. "
             "Pentru trei cazuri, condiționalele sunt rezonabile. Clasele Strategy "
             "apelează aceiași helperi, ca să izolăm dispatch-ul.")
    p.card(.6, 1.75, 5.95, 4.75, "Condiționale — baseline",
           "if / elif în ConditionalDispatcher.\n"
           "Aceiași helperi de politică.\n"
           "Avantaj: compact, ușor de urmărit.\n"
           "Extensie: adăugare de ramură.\n"
           "Nu introducem costuri artificiale.", GOLD, 21)
    p.card(6.8, 1.75, 5.95, 4.75, "Strategy — varianta cu pattern",
           "HintStrategy + trei clase concrete.\n"
           "Registru de obiecte fără stare.\n"
           "Avantaj anticipat: responsabilități separate.\n"
           "Extensie: clasă + înregistrare.\n"
           "Cost: mai mult cod și indirectionare.", TEAL, 21)
    pages.append(p)

    p = Page("Ipoteze și criterii experimentale", 45,
             "E0 este invariantul obligatoriu, verificat pe corpus, nu demonstrat formal. "
             "H1 rămâne de testat printr-o extensie controlată în M2. H2 nu afirmă "
             "viteză mai mare; raportăm timpi descriptivi. Memoria și construcția sunt viitoare.")
    for y, label, body, color in (
        (1.75, "E0 / ECHIVALENȚĂ", "Evenimente, stare, erori și RNG identice. Testat pe corpusul M1.", TEAL),
        (2.95, "H1 / EXTENSIE", "Fișiere / linii modificate și regresii la o politică nouă. Planificat M2.", BLUE),
        (4.15, "H2 / TIMP", "Mediană, Q1–Q3, raport median în perechi. Pilot fără inferență statistică.", GOLD),
        (5.35, "H3 / COST INIȚIAL", "Construcție și memorie, separat de apelul de indiciu. Planificat M2.", BLUE),
    ):
        p.box(.6, y, 12.1, 1.03)
        p.text(.85, y + .18, 3.15, .65, label, 18, color, True)
        p.text(4.05, y + .14, 8.3, .75, body, 20)
    pages.append(p)

    p = Page("Arhitectură: variație locală, motor comun", 60,
             "Urmăriți săgețile. Game validează, construiește contextul și aplică actualizarea. "
             "Doar alegerea helperului diferă: ramuri directe versus obiect HintStrategy. "
             "RNG-ul aparține fiecărui Game. Grila, starea și interfața CLI nu sunt duplicate.")
    p.box(.65, 2.8, 1.45, 1.25)
    p.text(.78, 3.05, 1.18, .8, "CLI\ncomun", 20, WHITE, True)
    p.arrow(2.13, 3.3, .45)
    p.box(2.62, 2.55, 2.3, 1.75)
    p.text(2.8, 2.75, 1.95, 1.35, "Game\nvalidare\ncontext, RNG", 19, TEAL, True)
    p.arrow(4.98, 3.3, .5)
    p.box(5.55, 1.9, 3.5, 1.4)
    p.text(5.75, 2.08, 3.1, 1.0, "ConditionalDispatcher\nif / elif → helper", 19, GOLD, True)
    p.box(5.55, 3.65, 3.5, 1.65)
    p.text(5.75, 3.83, 3.1, 1.35, "StrategyDispatcher\nregistru → HintStrategy\n3 obiecte concrete", 19, TEAL, True)
    p.arrow(9.1, 2.5, .45, color=GOLD)
    p.arrow(9.1, 4.3, .45)
    p.box(9.62, 2.1, 3.05, 2.95)
    p.text(9.83, 2.35, 2.62, 2.45, "Helperi comuni\nfirst_cells\nrandom_cells\nword_cells\n→ celule selectate", 19, WHITE, True)
    p.box(.65, 5.7, 12.05, .9)
    p.text(.9, 5.85, 11.55, .65,
           "Game: aceleași celule → protejare, contor, HintResult. Aceleași date / reguli / UI.", 20, MUTED)
    pages.append(p)

    p = Page("Demo: aceeași grilă, aceleași rezultate", 100,
             "Aveți terminalele deschise. Rulați python3 -m crosswords --variant conditional "
             "--seed 42 --demo, apoi aceeași comandă cu strategy. Arătați C prima literă, "
             "R ales aleator pe 2A și completarea CODUL. Răspunsurile finale rezolvă grila. "
             "Antetul diferă, evenimentele nu. Dacă demo-ul live nu este disponibil, "
             "folosiți fallback-ul static vizibil și spuneți explicit că este static.")
    p.box(.6, 1.75, 7.9, 4.95)
    p.text(.85, 1.98, 7.4, .55, "Demo fără input, seed 42", 23, TEAL, True)
    p.text(.85, 2.75, 7.4, 1.0,
           "python3 -m crosswords\n--variant conditional --seed 42 --demo", 20, WHITE)
    p.text(.85, 4, 7.4, 1.45,
           "hint 1A first → C\nhint 2A random → R\nhint 1D word → completează CODUL", 21)
    p.text(.85, 5.8, 7.4, .7, "Repetăm cu --variant strategy.\nFinal: CAL / DOR / LAC, 3 indicii.", 18, GOLD)
    p.grid(9.05, 2.05, .62, ("CAL##", "O####", "DOR##", "U####", "LAC##"))
    p.text(9.05, 5.5, 3.75, 1.05, "Fallback static al demo-ului.\nGrila finală: 11 / 11 celule corecte.", 18, MUTED)
    pages.append(p)

    p = Page("Protocol comparabil și reproductibil", 60,
             "Corectitudinea este verificată înainte de măsurare pentru toate cele 256 jocuri "
             "și prin checksum după fiecare lot. Încălzirile nu intră în date. În fiecare pereche "
             "ordinea este aleasă reproductibil. Măsurăm întregul apel, nu numai dispatch-ul. "
             "Crearea obiectelor este exclusă; un posibil cost al Strategy rămâne de măsurat separat.")
    for x, title, body in (
        (.6, "1. VERIFICARE", "Evenimente + stare + RNG\n256 jocuri identice"),
        (4.75, "2. ÎNCĂLZIRE", "3 loturi / variantă\nExcluse din rezultate"),
        (8.9, "3. MĂSURARE", "30 perechi A/B\nOrdine cu seed fix"),
    ):
        p.card(x, 1.85, 3.8, 2.3, title, body, size=19)
    p.arrow(4.42, 2.75, .25)
    p.arrow(8.57, 2.75, .25)
    p.text(.8, 4.55, 11.9, .6, "256 jocuri × 8 apeluri = 2.048 apeluri / lot; 61.440 / variantă.", 22, TEAL, True)
    p.text(.8, 5.45, 11.9, 1.1,
           "perf_counter_ns • seed 2026 • GC oprit doar în cronometrare\n"
           "În afara timerului: construcție, I/O, verificări, checksum.", 21, MUTED)
    pages.append(p)

    c = summary["metrics"]["conditional"]
    s = summary["metrics"]["strategy"]
    p = Page("Pilot M1: rezultate reale, exploratorii", 45,
             "Citiți medianele și dispersia descriptivă. Raportul este mediana rapoartelor "
             "în perechi, nu raportul medianelor. Peste 1 înseamnă mai lent pentru Strategy "
             "în acest workload. Nu raportăm semnificație. O diferență mică sau negativă "
             "nu invalidează proiectul. Sursa este CSV-ul real, nu cifre inventate.")
    maximum = max(c["median_ns_per_call"], s["median_ns_per_call"]) * 1.25
    for y, label, values, color in (
        (2.0, "Condiționale", c, GOLD), (3.45, "Strategy", s, TEAL),
    ):
        p.text(.75, y, 3.4, .5, label, 23, color, True)
        p.box(4.25, y, 5.2 * values["median_ns_per_call"] / maximum, .5, color)
        p.text(9.8, y, 2.8, .5, f"{values['median_ns_per_call'] / 1000:.3f} µs/apel", 22, color, True)
        p.text(4.25, y + .67, 7.9, .5,
               f"Q1–Q3: {values['q1_ns_per_call'] / 1000:.3f}–{values['q3_ns_per_call'] / 1000:.3f} µs/apel", 19, MUTED)
    p.text(.75, 5.0, 11.9, .55,
           f"Raport median pereche Strategy / condiționale: {summary['median_paired_strategy_over_conditional']:.3f}", 23, WHITE, True)
    p.text(.75, 5.95, 11.9, .85,
           "Un host / proces / workload. Fără inferență statistică.\n"
           "Python 3.13.2 • macOS arm64 • results/m1/raw.csv + summary.json", 18, MUTED)
    pages.append(p)

    p = Page("Structura codului: un trade-off, nu un verdict", 40,
             "Metricile sunt descriptive: linii ne-goale/ne-comentariu și clase incluzând Protocol. "
             "If se numără doar în select al dispatcherului, nu în tot programul. "
             "Strategy are mai multe clase și cod. Extensibilitatea nu este dovedită de numărul "
             "de ramuri: experimentul de extensie este planificat M2.")
    p.box(.65, 1.8, 12.05, 3.65)
    headers = [("Metrică descriptivă", .9, 6.2), ("if/elif", 7.4, 2), ("Strategy", 10.1, 2.2)]
    for text, x, width in headers:
        p.text(x, 2.02, width, .5, text, 22, TEAL, True)
    rows = (
        ("Linii ne-goale / ne-comentariu", "nonblank_noncomment_lines"),
        ("Clase, incluzând Protocol", "class_definitions_including_protocol"),
        ("Noduri If în dispatcher.select", "dispatcher_select_if_nodes"),
    )
    for y, (label, key) in zip((2.9, 3.7, 4.5), rows):
        p.text(.9, y, 6.2, .55, label, 21)
        p.text(7.4, y, 2, .55, str(metrics["conditional"][key]), 24, GOLD, True)
        p.text(10.1, y, 2.2, .55, str(metrics["strategy"][key]), 24, TEAL, True)
    p.text(.8, 5.85, 11.8, .95,
           "Compactitate acum vs separarea responsabilităților la extensie.\n"
           "Nu confundăm mutarea ramurilor cu mentenabilitatea globală.", 22, MUTED)
    pages.append(p)

    p = Page("Stadiu implementare și limite M1", 45,
             "Sunt realizate ambele variante, testele, demo-ul, scripturile și pilotul. "
             "Testele includ 100 seed-uri, comenzi mixte și erori. Codul și datele sunt locale "
             "cu tag M1; repository-ul personal privat a fost creat și release-ul se verifică la final. Nu afirmăm articol final sau "
             "contribuții umane neconfirmate. Studenții trebuie să valideze asistența AI.")
    p.card(.6, 1.75, 5.95, 4.85, "Realizat și verificabil",
           "Motor comun + două variante.\n"
           "18 teste; echivalență inclusiv RNG.\n"
           "Demo complet, fără input.\n"
           "CSV brut + metadate + reproducere.\n"
           "Git local și tag M1 la release.", TEAL, 21)
    p.card(6.8, 1.75, 5.95, 4.85, "Nu este încă realizat",
           "Extensie controlată / memorie.\n"
           "Replicări multi-process robuste.\n"
           "Concluzii statistice / articol M3.\n"
           "Echipă și roluri umane confirmate.\n"
           "Articolul final rămâne pentru M3.", GOLD, 21)
    pages.append(p)

    p = Page("Echipă, progres real și plan până la M2", 45,
             "Nu inventăm membri sau sprinturi. Contul este nadolualex, numele academic rămâne "
             "de completat. Responsabilitățile pot fi ale aceluiași student. Pregătirea curentă "
             "este asistată AI. Sprinturile viitoare depind de calendarul cursului; M2 s12, M3 s14.")
    p.box(.6, 1.75, 4.6, 4.95)
    p.text(.85, 2.0, 4.1, .6, "De confirmat", 23, GOLD, True)
    p.text(.85, 2.9, 4.1, 2.55,
           "Nume academic / membri.\n"
           "Roluri: motor + teste,\nexperimente, prezentare.\n"
           "Nu sunt persoane distincte presupuse.", 21)
    p.text(.85, 5.7, 4.1, .8, "Pregătire asistată AI;\nvalidare academică obligatorie.", 18, MUTED)
    for y, title, body in (
        (1.75, "ACUM / M1", "Prototip, teste, pilot, PPTX. Nu inventăm sprinturi trecute."),
        (3.05, "SPRINTURI VIITOARE", "Corpus extins → extensie controlată → replicări / memorie."),
        (4.35, "M2 / SĂPTĂMÂNA 12", "Raport comparativ și date reproductibile; tag M2 atunci."),
        (5.65, "M3 / SĂPTĂMÂNA 14", "PPTX final + articol științific PDF; tag M3 atunci."),
    ):
        p.box(5.5, y, 7.2, 1.05)
        p.text(5.72, y + .1, 6.75, .35, title, 15, TEAL, True)
        p.text(5.72, y + .46, 6.75, .55, body, 16)
    pages.append(p)

    p = Page("Ce rămâne de demonstrat?", 25,
             "Încheiați cu întrebarea de extensibilitate, nu cu un verdict de viteză. "
             "Referințele sunt publice; suportul de curs nu este reprodus. "
             "Menționați asistența AI și responsabilitatea studentului de a înțelege și valida. "
             "Opriți prezentarea la 9:30 și rezervați două minute pentru întrebări.")
    p.text(.8, 1.9, 11.7, 1.25,
           "Când merită separarea prin Strategy\ncostul suplimentar de structură?", 30, TEAL, True)
    p.text(.8, 3.5, 11.7, .85,
           "M1 dovedește un prototip comparabil pe corpusul testat.\nM2 va testa extensia; M3 va sintetiza dovezile și limitele.", 22)
    p.text(.8, 4.75, 11.7, 1.35,
           "Referințe publice: Refactoring.Guru — Strategy; pyperf — Run benchmarks.\n"
           "URL-uri și metodologie completă: docs/METHODOLOGY.md.\n"
           "AI declarat; echipa și contribuțiile umane trebuie confirmate.", 18, MUTED)
    p.text(.8, 6.3, 11.7, .4, "9:30 prezentare  /  2:00 întrebări", 19, GOLD, True)
    pages.append(p)
    for index, page in enumerate(pages, 1):
        page.heading(index)
    return pages


def export(pages: list[Page]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    presentation = Presentation()
    presentation.slide_width, presentation.slide_height = Inches(W), Inches(H)
    presentation.core_properties.title = "SASPS M1 — Crosswords: Strategy pattern vs conditionale"
    presentation.core_properties.author = "Pregatire asistata GitHub Copilot; echipa de confirmat"
    presentation.core_properties.subject = "Milestone 1; prototip si pilot exploratoriu"
    pdf = canvas.Canvas(str(OUT / "SASPS_M1_Crosswords_slides.pdf"), pagesize=(W * 72, H * 72))
    pdf.setTitle("SASPS M1 — slide-uri, nu articol stiintific")
    pdf.setAuthor("Pregatire asistata AI; echipa de confirmat")
    for index, page in enumerate(pages, 1):
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor.from_string(BG)
        pdf.setFillColorRGB(*(int(BG[i:i+2], 16) / 255 for i in (0, 2, 4)))
        pdf.rect(0, 0, W * 72, H * 72, fill=1, stroke=0)
        for item in page.items:
            x, y, w, h = (item[key] for key in ("x", "y", "w", "h"))
            if min(x, y, w, h) < 0 or x + w > W + .001 or y + h > H + .001:
                raise ValueError(f"Forma in afara slide-ului {index}: {item}")
            if item["kind"] == "text":
                shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
                frame = shape.text_frame
                frame.margin_left = frame.margin_right = Pt(2)
                frame.margin_top = frame.margin_bottom = Pt(0)
                frame.word_wrap = False
                pdf.setFont("DeckBold" if item["bold"] else "Deck", item["size"])
                color = item["color"]
                pdf.setFillColorRGB(*(int(color[i:i+2], 16) / 255 for i in (0, 2, 4)))
                for line_index, line in enumerate(item["lines"]):
                    paragraph = frame.paragraphs[0] if line_index == 0 else frame.add_paragraph()
                    paragraph.text = line
                    paragraph.font.name = FONT
                    paragraph.font.size = Pt(item["size"])
                    paragraph.font.bold = item["bold"]
                    paragraph.font.color.rgb = RGBColor.from_string(color)
                    paragraph.space_before = paragraph.space_after = Pt(0)
                    paragraph.line_spacing = Pt(item["size"] * 1.2)
                    pdf.drawString(x * 72 + 2, (H - y) * 72 - item["size"] * (1 + 1.2 * line_index), line)
            else:
                shape_type = MSO_SHAPE.RIGHT_ARROW if item["kind"] == "arrow" else MSO_SHAPE.RECTANGLE
                shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
                shape.fill.solid()
                color = item["fill"]
                shape.fill.fore_color.rgb = RGBColor.from_string(color)
                shape.line.fill.background()
                pdf.setFillColorRGB(*(int(color[i:i+2], 16) / 255 for i in (0, 2, 4)))
                if item["kind"] == "arrow":
                    path = pdf.beginPath()
                    px, py = x * 72, (H - y - h) * 72
                    pw, ph = w * 72, h * 72
                    for n, (dx, dy) in enumerate(((0, .25), (.6, .25), (.6, 0),
                                                  (1, .5), (.6, 1), (.6, .75), (0, .75))):
                        if n == 0:
                            path.moveTo(px + dx * pw, py + dy * ph)
                        else:
                            path.lineTo(px + dx * pw, py + dy * ph)
                    path.close()
                    pdf.drawPath(path, fill=1, stroke=0)
                else:
                    pdf.rect(x * 72, (H - y - h) * 72, w * 72, h * 72, fill=1, stroke=0)
        slide.notes_slide.notes_text_frame.text = (
            f"SLIDE {index} — DUREE: {page.seconds} secunde\n\n{page.notes}"
        )
        pdf.showPage()
    presentation.save(OUT / "SASPS_M1_Crosswords.pptx")
    pdf.save()
    manifest = {
        "slides": [{"number": i, "title": p.title, "seconds": p.seconds,
                    "speaker_notes": p.notes} for i, p in enumerate(pages, 1)],
        "total_seconds": sum(p.seconds for p in pages),
        "qa_seconds": 120,
        "font": FONT,
        "pdf_kind": "slide preview from same layout; not final scientific article",
        "results_source": "results/m1/summary.json",
        "code_metrics_source": "results/m1/code_metrics.json",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    summary = json.loads((ROOT / "results/m1/summary.json").read_text(encoding="utf-8"))
    metrics = json.loads((ROOT / "results/m1/code_metrics.json").read_text(encoding="utf-8"))
    pages = build_pages(summary, metrics)
    if len(pages) != 12 or sum(page.seconds for page in pages) != 570:
        raise ValueError("Numar / durata slide-uri neconforme.")
    export(pages)
    print(OUT / "SASPS_M1_Crosswords.pptx")


if __name__ == "__main__":
    main()
