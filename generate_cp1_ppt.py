import csv
import json
from datetime import datetime
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent


def set_run_style(run, size=16, bold=False, color=(31, 41, 55)) -> None:
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)


def add_line(text_frame, text: str, size=16, bold=False, color=(31, 41, 55), first=False, space_after=4):
    paragraph = text_frame.paragraphs[0] if first else text_frame.add_paragraph()
    paragraph.text = text
    paragraph.space_after = Pt(space_after)
    for run in paragraph.runs:
        set_run_style(run, size=size, bold=bold, color=color)


def read_csv_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file)]


def read_report(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_metrics():
    ems_rows = read_csv_rows(ROOT / "data" / "raw" / "ems_events.csv")
    joined_rows = read_csv_rows(ROOT / "data" / "processed" / "joined_event_daily.csv")
    report = read_report(ROOT / "outputs" / "quality_report.json")

    n_events = int(report.get("final_rows", {}).get("ems_events_clean", 0))
    joined_event_ids = {row["event_id"] for row in joined_rows if row.get("event_id")}
    m_events = len(joined_event_ids)
    p_coverage = round((100.0 * m_events / n_events), 1) if n_events else 0.0

    start_dates = [datetime.strptime(row["start_date"], "%Y-%m-%d") for row in ems_rows if row.get("start_date")]
    end_dates = [datetime.strptime(row["end_date"], "%Y-%m-%d") for row in ems_rows if row.get("end_date")]
    period_min = min(start_dates).strftime("%Y-%m-%d") if start_dates else "-"
    period_max = max(end_dates).strftime("%Y-%m-%d") if end_dates else "-"

    return {
        "N": n_events,
        "M": m_events,
        "P": p_coverage,
        "PERIOD": f"{period_min} - {period_max}",
    }


def add_slide_1(prs: Presentation, metrics: dict) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title = slide.shapes.add_textbox(Inches(0.55), Inches(0.35), Inches(12.1), Inches(0.5)).text_frame
    add_line(
        title,
        "MEDE · CP1 · ALINIERE ȘI SURSE · SĂPTĂMÂNA 4",
        size=15,
        bold=True,
        color=(30, 39, 97),
        first=True,
        space_after=0,
    )

    subtitle = slide.shapes.add_textbox(Inches(0.55), Inches(0.85), Inches(12.1), Inches(0.5)).text_frame
    add_line(
        subtitle,
        "Alexandru Neagu · U8 · Cauzele inundațiilor europene",
        size=20,
        bold=True,
        color=(17, 24, 39),
        first=True,
        space_after=0,
    )

    body = slide.shapes.add_textbox(Inches(0.55), Inches(1.45), Inches(12.15), Inches(5.6)).text_frame
    body.word_wrap = True
    body.clear()
    add_line(body, "Întrebarea mea", size=16, bold=True, first=True, space_after=2)
    add_line(body, "Q8.1 — Inundațiile din Europa se grupează după cauză (ploaie intensă / fluvial / topire)?", size=14)
    add_line(body, "", size=10, space_after=0)
    add_line(body, "Unitatea și sursele", size=16, bold=True, space_after=2)
    add_line(
        body,
        "Evenimentul de inundație (1 rând = 1 activare EMS Flood din Europa) → Copernicus EMS + ERA5-Land "
        "(precipitații 1/3/7/30 zile, topire, umiditatea solului); pas de timp: ferestre de 1–30 zile înainte de eveniment.",
        size=14,
    )
    add_line(body, "Cheia comună: codul EMSR + data evenimentului + celula ERA5-Land din centroid.", size=14)
    add_line(body, "", size=10, space_after=0)
    add_line(body, "Cui îi folosește răspunsul", size=16, bold=True, space_after=2)
    add_line(
        body,
        "Hidrologului / planificatorului de risc: ce înseamnă „clusterul 3” — de ex. evenimente cu sol saturat și topire, "
        "unde avertizarea se bazează pe zăpadă, nu pe ploaie.",
        size=14,
    )
    add_line(body, "", size=10, space_after=0)
    add_line(body, "Unde am ajuns", size=16, bold=True, space_after=2)
    add_line(body, "Etapa curentă: aliniere (surse → un tabel, 1 rând = 1 eveniment)", size=14)
    add_line(
        body,
        f"Făcut de la CP0: pipeline-ul rulează pe ambele surse; X are {metrics['M']} × 8; "
        f"acoperire {metrics['P']}% din {metrics['N']} evenimente europene; data card pe 2 surse; SOA cu 10 articole.",
        size=14,
    )
    add_line(body, "Ce am schimbat față de plan: nimic.", size=14)
    add_line(body, "Următorul pas: CP2 — matricea X documentată și prima proiecție PCA.", size=14)

    footer = slide.shapes.add_textbox(Inches(0.55), Inches(7.02), Inches(12.2), Inches(0.25)).text_frame
    add_line(footer, "Slide 1 din 3 · Fișier Moodle: CP1_U8.pdf · Prezentare: 3 minute", size=11, color=(75, 85, 99), first=True, space_after=0)


def add_slide_2(prs: Presentation, metrics: dict) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title = slide.shapes.add_textbox(Inches(0.55), Inches(0.35), Inches(12.1), Inches(0.5)).text_frame
    add_line(
        title,
        "DOVADA ETAPEI · DATA CARD PE SCURT + STATE OF THE ART (10 ARTICOLE)",
        size=15,
        bold=True,
        color=(30, 39, 97),
        first=True,
        space_after=0,
    )

    subtitle = slide.shapes.add_textbox(Inches(0.55), Inches(0.85), Inches(12.1), Inches(0.5)).text_frame
    add_line(
        subtitle,
        f"Din {metrics['N']} inundații EMS din Europa, {metrics['M']} ({metrics['P']}%) supraviețuiesc alinierii cu ERA5-Land",
        size=15,
        bold=True,
        color=(17, 24, 39),
        first=True,
        space_after=0,
    )

    body = slide.shapes.add_textbox(Inches(0.55), Inches(1.35), Inches(12.2), Inches(5.7)).text_frame
    body.word_wrap = True
    body.clear()
    add_line(body, "S1 · Copernicus EMS, activări Rapid Mapping", size=14, bold=True, first=True, space_after=1)
    add_line(
        body,
        f"Flood (EMSR), Europa · {metrics['PERIOD']} · 1 rând = 1 eveniment (AOI vectorial) · lon/lat, UTC · "
        "goluri: 0 fără dată/geometrie · licență: conform termenilor oficiali Copernicus EMS.",
        size=12,
    )
    add_line(body, "", size=10, space_after=0)
    add_line(body, "S2 · ERA5-Land hourly (C3S / CDS)", size=14, bold=True, space_after=1)
    add_line(
        body,
        "tp, snowmelt, swvl1 · 0,1° (~9 km), 00:00 UTC → total zilnic · mm, m³/m³ · goluri: 0 evenimente incomplete · "
        "licență Copernicus.",
        size=12,
    )
    add_line(body, "", size=10, space_after=0)
    add_line(body, "Articol | Date / surse | Metodă | Metrică | Rezultat publicat (nu propriu)", size=12, bold=True, space_after=1)
    lines = [
        "1. Stein et al. (2020) | 113 635 ev., 4 155 bazine | arbore de decizie, 5 procese | robustețe + evaluare | exces de ploaie dominant; variabil în bazin",
        "2. Blöschl et al. (2017) | 4 262 stații, 38 țări EU | momentul maximului; Theil–Sen | trend zile/deceniu | −13 … +9 zile/deceniu",
        "3. Hall & Blöschl (2018) | 4 105 stații EU | clustere pe sezonalitate | — | 6 regiuni cu sezoane distincte",
        "4. Berghuijs et al. (2016) | 420 bazine SUA | mecanisme dominante | — | sol umed, topire > ploaie singură",
        "5. Stein et al. (2021) | 671 bazine SUA | random forest + ALE | R² bazine nemăsurate | R² 0,45–0,9; clima domină",
        "6. Kemter et al. (2020) | 3 872 stații EU | clasif. pe meteo antecedent | Spearman | ρ>0 la 95% din stații",
        "7. Bertola et al. (2021) | 2 370 stații EU | Gumbel regional, bayesian | elasticități | NV: ploaie; E: topire; S: ambele",
        "8. Tarasova et al. (2019) | review clasificări cauzale | sinteză critică | — | fără definiție unificată",
        "9. Bonafilia et al. (2020) | S1, 4 831 chipuri, 11 ev. | FCNN vs. prag | 4 variante de etichete | FCNN pe etichete S2 cel mai bun",
        "10. Muñoz-Sabater et al. (2021) | ERA5-Land, 9 km | reanaliză orară | vs. in-situ | zăpadă: performanță mixtă",
    ]
    for line in lines:
        add_line(body, line, size=11, space_after=0)

    footer = slide.shapes.add_textbox(Inches(0.55), Inches(7.02), Inches(12.2), Inches(0.25)).text_frame
    add_line(
        footer,
        "Slide 2 din 3 · Rezultate publicate, nu proprii; seturi diferite nu se compară numeric · "
        "ALE = efecte locale acumulate; FCNN = rețea convoluțională; detalii în SOA_U8",
        size=10,
        color=(75, 85, 99),
        first=True,
        space_after=0,
    )


def add_slide_3(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title = slide.shapes.add_textbox(Inches(0.55), Inches(0.35), Inches(12.1), Inches(0.5)).text_frame
    add_line(
        title,
        "BLOCAJE ȘI URMĂTOARELE DOUĂ SĂPTĂMÂNI · CP2: 4 NOIEMBRIE 2026, 00:00",
        size=15,
        bold=True,
        color=(30, 39, 97),
        first=True,
        space_after=0,
    )

    body = slide.shapes.add_textbox(Inches(0.55), Inches(0.95), Inches(12.2), Inches(6.0)).text_frame
    body.word_wrap = True
    body.clear()
    add_line(body, "Blocaje și planul până la CP2", size=16, bold=True, first=True, space_after=1)
    add_line(body, "Blocaje / riscuri", size=14, bold=True, space_after=1)
    add_line(
        body,
        "1. EMS nu e un eșantion aleator (doar utilizatori autorizați cer activări) → raportez acoperirea pe țări și nu "
        "generalizez la „toate inundațiile Europei”.",
        size=13,
    )
    add_line(
        body,
        "2. Fără etichetă de cauză în EMS → subtipul și textul rapoartelor servesc doar la interpretare → am nevoie de acordul titularului.",
        size=13,
    )
    add_line(
        body,
        "3. ERA5-Land are ~9 km, iar AOI-urile pot fi mai mici → centroid vs. media pe AOI; testez la CP2.",
        size=13,
    )
    add_line(
        body,
        "4. Evenimente scoase din X: 0 (motive: fără dată / geometrie / meteo incompletă) → am păstrat regula strictă de validare.",
        size=13,
    )
    add_line(body, "", size=10, space_after=0)
    add_line(body, "Planul pe 2 săptămâni", size=14, bold=True, space_after=1)
    add_line(
        body,
        "Săpt. 5: matricea X documentată (n × d, cu proveniența fiecărei trăsături); analiză univariată și bivariată; "
        "decid fereastra (end-offset 0 vs. 1) și punctul vs. media pe AOI.",
        size=13,
    )
    add_line(
        body,
        "Săpt. 6: prima proiecție PCA (scree, loadings) pe X scalat, ca baseline; README reproductibil.",
        size=13,
    )
    add_line(
        body,
        "La CP2 arăt: matricea X + scree/loadings. Secțiunea de articol: Methods — trăsături.",
        size=13,
    )
    add_line(
        body,
        "Comparația pregătită: S1 singur vs. S1 + teren + meteo (CP3–CP4).",
        size=13,
    )
    add_line(body, "Repo: [https://github.com/utilizator/MEDE-U8-flood-causes]", size=13)

    footer = slide.shapes.add_textbox(Inches(0.55), Inches(7.02), Inches(12.2), Inches(0.25)).text_frame
    add_line(
        footer,
        "Slide 3 din 3 · Întrebare pentru profesor: se acceptă subtipul EMS ca etichetă slabă, folosită doar la interpretare?",
        size=10,
        color=(75, 85, 99),
        first=True,
        space_after=0,
    )


def build_presentation(output_path: Path) -> None:
    metrics = build_metrics()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    add_slide_1(prs, metrics)
    add_slide_2(prs, metrics)
    add_slide_3(prs)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))


if __name__ == "__main__":
    build_presentation(ROOT / "CP1_U8.pptx")
