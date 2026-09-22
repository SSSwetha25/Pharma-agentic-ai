from datetime import datetime
from html import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _text(value, fallback="Unavailable"):
    if value is None or value == "":
        return fallback
    return str(value)


def _paragraph(value, style):
    return Paragraph(escape(_text(value)), style)


def _score_dimension(dimension):
    if not isinstance(dimension, dict):
        return "Unknown"
    score = dimension.get("score")
    maximum = dimension.get("maximum")
    if score is None:
        return "Unknown"
    return f"{score} / {maximum}"


def _footer(canvas, doc):
    canvas.saveState()
    width, _ = A4

    canvas.setStrokeColor(colors.HexColor("#E2E8F0"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, 14 * mm, width - doc.rightMargin, 14 * mm)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#98A2B3"))
    canvas.drawString(
        doc.leftMargin,
        9 * mm,
        "PharmIntel · Research and decision-support prototype",
    )
    canvas.drawRightString(
        width - doc.rightMargin,
        9 * mm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


def _make_table(data, widths, header=True, font_size=8.2):
    cell_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=font_size,
        leading=10.5,
        textColor=colors.HexColor("#334155"),
    )
    header_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=font_size,
        leading=10.5,
        textColor=colors.white,
    )

    converted = []
    for row_index, row in enumerate(data):
        style = header_style if header and row_index == 0 else cell_style
        converted.append(
            [Paragraph(escape(_text(value, "—")), style) for value in row]
        )

    table = Table(converted, colWidths=widths, repeatRows=1 if header else 0)
    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#17324D"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D7DEE7"),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F8FAFC")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _normalize_trials(trials):
    if isinstance(trials, pd.DataFrame):
        if trials.empty:
            return []
        return trials.to_dict("records")

    if not isinstance(trials, list):
        return []

    return [trial for trial in trials if isinstance(trial, dict)]


def generate_pdf_report(results, user_query: str) -> str:
    """
    Generate a professional, evidence-aware PDF briefing from the
    multi-agent result structure.

    The report preserves the distinction between source-reported facts,
    derived projections, and unavailable evidence. It does not fabricate
    missing domain evidence.
    """
    file_path = "agentic_pharma_report.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=20 * mm,
        title="Pharma Intelligence Report",
        author="PharmIntel",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        textColor=colors.HexColor("#172033"),
        spaceAfter=5,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=12,
        textColor=colors.HexColor("#667085"),
        spaceAfter=13,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#17324D"),
        spaceBefore=13,
        spaceAfter=7,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13.2,
        textColor=colors.HexColor("#334155"),
        spaceAfter=7,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.7,
        leading=10.5,
        textColor=colors.HexColor("#667085"),
        spaceAfter=4,
    )

    score_style = ParagraphStyle(
        "Score",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=25,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17324D"),
    )

    score_label_style = ParagraphStyle(
        "ScoreLabel",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#667085"),
    )

    callout_style = ParagraphStyle(
        "Callout",
        parent=body_style,
        fontSize=9.2,
        leading=14,
        textColor=colors.HexColor("#344054"),
        spaceAfter=0,
    )

    story = []

    clinical = results.get("clinical", {}) or {}
    patent = results.get("patent", {}) or {}
    market = results.get("market", {}) or {}
    opportunity = results.get("opportunity_score", {}) or {}

    market_data = market.get("market_data", {}) or {}
    source_reported = market_data.get("source_reported", {}) or {}
    derived_projection = market_data.get("derived_projection", []) or []
    strategic_signals = market_data.get("strategic_signals", {}) or {}

    # ------------------------------------------------------------
    # Header
    # ------------------------------------------------------------
    story.append(Paragraph("Pharma Intelligence Report", title_style))
    story.append(
        Paragraph(
            "Generated by Agentic Decision Support System"
            f"  ·  {datetime.now().strftime('%B %d, %Y · %H:%M')}",
            subtitle_style,
        )
    )

    query_table = Table(
        [
            [
                Paragraph(
                    f"<b>Target Research Query</b><br/>{escape(user_query)}",
                    body_style,
                )
            ]
        ],
        colWidths=[174 * mm],
    )
    query_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#DCE3EA"),
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(query_table)
    story.append(Spacer(1, 8))

    # ------------------------------------------------------------
    # Executive recommendation
    # ------------------------------------------------------------
    story.append(Paragraph("Executive Recommendation", section_style))

    conclusion = results.get(
        "conclusion",
        "No combined conclusion was generated.",
    )

    conclusion_table = Table(
        [[Paragraph(escape(_text(conclusion)), callout_style)]],
        colWidths=[174 * mm],
    )
    conclusion_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6FAFF")),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#BFD3E8"),
                ),
                (
                    "LINEBEFORE",
                    (0, 0),
                    (0, -1),
                    3,
                    colors.HexColor("#17324D"),
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(conclusion_table)

    # ------------------------------------------------------------
    # Opportunity assessment
    # ------------------------------------------------------------
    story.append(Paragraph("Opportunity Assessment", section_style))

    overall_score = opportunity.get("overall_score")
    rating = opportunity.get("rating", "Unavailable")
    confidence = opportunity.get(
        "evidence_confidence",
        {},
    ).get(
        "level",
        opportunity.get("confidence", "Unavailable"),
    )
    dimensions = opportunity.get("dimension_scores", {}) or {}

    score_display = (
        f"{overall_score} / 100"
        if overall_score is not None
        else "Unavailable"
    )

    score_grid = Table(
        [
            [
                Paragraph(score_display, score_style),
                Paragraph(escape(_text(rating)), score_style),
                Paragraph(escape(_text(confidence)), score_style),
            ],
            [
                Paragraph("Opportunity score", score_label_style),
                Paragraph("Assessment", score_label_style),
                Paragraph("Evidence confidence", score_label_style),
            ],
        ],
        colWidths=[58 * mm, 58 * mm, 58 * mm],
    )
    score_grid.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.HexColor("#DCE3EA"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#E7ECF1"),
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 9),
            ]
        )
    )
    story.append(score_grid)
    story.append(Spacer(1, 7))

    dimension_data = [
        ["Dimension", "Score", "Interpretation / status"],
        [
            "Market potential",
            _score_dimension(dimensions.get("market")),
            "Source-backed market size and reported growth",
        ],
        [
            "Clinical activity",
            _score_dimension(dimensions.get("clinical")),
            "Validated clinical development activity",
        ],
        [
            "Competition",
            _score_dimension(dimensions.get("competition")),
            _text(
                dimensions.get("competition", {}).get("level")
                if isinstance(dimensions.get("competition"), dict)
                else None,
                "Unknown",
            ),
        ],
        [
            "IP evidence",
            _score_dimension(dimensions.get("ip")),
            "Unknown / unavailable" if dimensions.get("ip", {}).get("score") is None
            else "Evidence-backed IP assessment",
        ],
    ]
    story.append(
        _make_table(
            dimension_data,
            [48 * mm, 30 * mm, 96 * mm],
            font_size=8.2,
        )
    )

    score_method = opportunity.get("methodology", {}).get(
        "missing_evidence_policy"
    )
    if score_method:
        story.append(Spacer(1, 5))
        story.append(
            Paragraph(
                f"<b>Scoring policy:</b> {escape(str(score_method))}",
                small_style,
            )
        )

    # ------------------------------------------------------------
    # Clinical evidence
    # ------------------------------------------------------------
    story.append(Paragraph("Clinical Evidence", section_style))

    trials = _normalize_trials(clinical.get("trials", []))
    trials_count = len(trials) or clinical.get("trial_count", 0)

    # Avoid displaying a contradictory fallback such as "No clinical
    # summary available" when actual trial records are present.
    clinical_summary = clinical.get("summary")
    if trials_count:
        if not clinical_summary or str(clinical_summary).strip().lower() in {
            "no clinical summary available.",
            "no clinical summary available",
        }:
            clinical_summary = (
                f"{trials_count} validated matching clinical trial(s) were "
                "identified by the Clinical Agent."
            )
    elif not clinical_summary:
        clinical_summary = "No clinical trial records are available for this analysis."

    story.append(Paragraph(escape(_text(clinical_summary)), body_style))

    if trials:
        rows = [
            [
                "NCT ID",
                "Trial",
                "Status",
                "Phase",
                "Enrollment",
                "Sponsor",
                "Start",
            ]
        ]

        for trial in trials:
            phase = trial.get("phase", "Not reported")
            if isinstance(phase, list):
                phase = ", ".join(map(str, phase)) or "Not reported"

            rows.append(
                [
                    trial.get("nct_id", "—"),
                    trial.get("title", "—"),
                    trial.get("status", "—"),
                    phase,
                    trial.get("enrollment", "—"),
                    trial.get("sponsor", "—"),
                    trial.get("start_date", "—"),
                ]
            )

        clinical_table = _make_table(
            rows,
            [
                20 * mm,
                60 * mm,
                23 * mm,
                20 * mm,
                20 * mm,
                30 * mm,
                25 * mm,
            ],
            font_size=6.8,
        )
        story.append(clinical_table)

        story.append(
            Paragraph(
                "Source: ClinicalTrials.gov. Individual NCT identifiers in the "
                "dashboard link to the corresponding registry records.",
                small_style,
            )
        )
    else:
        story.append(
            Paragraph(
                "No clinical trial records are available for this analysis.",
                small_style,
            )
        )

    # ------------------------------------------------------------
    # Market intelligence
    # ------------------------------------------------------------
    story.append(Paragraph("Market Intelligence", section_style))

    market_summary = market.get(
        "summary",
        "No market summary is available.",
    )
    if market_summary:
        story.append(Paragraph(escape(_text(market_summary)), body_style))

    if market_data:
        source_size = source_reported.get(
            "market_size",
            market_data.get("estimated_size", "Unavailable"),
        )
        source_year = source_reported.get(
            "year",
            market_data.get("estimated_size_year", "Not reported"),
        )
        reported_growth = source_reported.get(
            "growth",
            market_data.get("cagr", "Unavailable"),
        )
        forecast_size = source_reported.get(
            "forecast_market_size",
            market_data.get("forecast_market_size", "Unavailable"),
        )
        forecast_year = source_reported.get(
            "forecast_year",
            market_data.get("forecast_year", "Not reported"),
        )
        competition = market_data.get(
            "competition_level",
            "Unavailable",
        )

        market_grid = [
            ["Metric", "Value", "Evidence type"],
            ["Market size", source_size, f"Source-reported ({source_year})"],
            ["Growth", reported_growth, "Source-reported"],
            [
                "Forecast",
                f"{forecast_size} by {forecast_year}",
                "Source-reported",
            ],
            ["Competition", competition, "Agent assessment"],
        ]

        story.append(
            _make_table(
                market_grid,
                [45 * mm, 55 * mm, 74 * mm],
                font_size=8,
            )
        )

        if derived_projection:
            story.append(Spacer(1, 7))
            story.append(
                Paragraph("Derived Market Trajectory", section_style)
            )

            projection_rows = [["Year", "Market Size ($B)", "Type"]]
            for item in derived_projection:
                projection_rows.append(
                    [
                        item.get("Year", "—"),
                        item.get("Market Size ($B)", "—"),
                        "Source baseline"
                        if item.get("Year") == source_reported.get("year")
                        else "Derived",
                    ]
                )

            story.append(
                _make_table(
                    projection_rows,
                    [35 * mm, 55 * mm, 84 * mm],
                    font_size=8,
                )
            )

            method = market_data.get("projection_method")
            if method:
                story.append(
                    Paragraph(
                        f"<b>Projection method:</b> {escape(str(method))}",
                        small_style,
                    )
                )

            story.append(
                Paragraph(
                    "The source-reported market figures and derived "
                    "intermediate projections are intentionally kept separate.",
                    small_style,
                )
            )

        drivers = market_data.get("key_drivers", []) or []
        if drivers:
            story.append(Paragraph("Commercial Drivers", section_style))
            for driver in drivers:
                story.append(
                    Paragraph(
                        f"• {escape(str(driver))}",
                        body_style,
                    )
                )

        opportunity_signal = strategic_signals.get("opportunity")
        competitive_signal = strategic_signals.get("competitive_intensity")
        if opportunity_signal or competitive_signal:
            story.append(Paragraph("Strategic Market Signals", section_style))
            if opportunity_signal:
                if isinstance(opportunity_signal, dict):
                    level = opportunity_signal.get("level", "Unavailable")
                    rationale = opportunity_signal.get("rationale")
                    text = f"<b>Opportunity — {escape(_text(level))}</b>"
                    if rationale:
                        text += f"<br/>{escape(_text(rationale))}"
                else:
                    text = f"<b>Opportunity — {escape(_text(opportunity_signal))}</b>"
                story.append(Paragraph(text, body_style))

            if competitive_signal:
                if isinstance(competitive_signal, dict):
                    level = competitive_signal.get("level", "Unavailable")
                    assessment = competitive_signal.get("assessment")
                    text = f"<b>Competitive intensity — {escape(_text(level))}</b>"
                    if assessment:
                        text += f"<br/>{escape(_text(assessment))}"
                else:
                    text = (
                        f"<b>Competitive intensity — "
                        f"{escape(_text(competitive_signal))}</b>"
                    )
                story.append(Paragraph(text, body_style))

    # ------------------------------------------------------------
    # IP evidence
    # ------------------------------------------------------------
    story.append(Paragraph("IP Evidence Status", section_style))

    patent_status = (
        "Available"
        if patent.get("patents") is not None
        and isinstance(patent.get("patents"), pd.DataFrame)
        and not patent.get("patents").empty
        else "Unknown / unavailable"
    )

    patent_summary = patent.get(
        "summary",
        "",
    )

    story.append(
        Paragraph(
            f"<b>Status:</b> {escape(patent_status)}",
            body_style,
        )
    )

    # If IP evidence is unavailable, use wording that describes the
    # retrieval limitation rather than implying that a substantive patent
    # search found no relevant patents.
    if patent_status == "Unknown / unavailable":
        patent_summary = (
            "Patent/IP evidence was unavailable from the currently "
            "implemented retrieval source. Therefore, no conclusion about "
            "patent coverage, freedom to operate, or absence of relevant "
            "patents can be made."
        )

    if patent_summary:
        story.append(
            Paragraph(
                escape(_text(patent_summary)),
                body_style,
            )
        )

    story.append(
        Paragraph(
            "No patent records being available from the currently "
            "implemented evidence source must not be interpreted as proof "
            "that no relevant patents exist. A definitive freedom-to-operate "
            "opinion requires claim-level legal analysis, jurisdiction review, "
            "patent-family review and prosecution-status assessment.",
            small_style,
        )
    )

    # ------------------------------------------------------------
    # Evidence limitations
    # ------------------------------------------------------------
    story.append(Paragraph("Evidence Limitations & Methodology", section_style))

    limitations = []

    for domain_key, label in [
        ("clinical", "Clinical"),
        ("market", "Market"),
        ("patent", "IP"),
    ]:
        domain = results.get(domain_key, {}) or {}
        domain_limitations = domain.get("limitations", []) or []
        for limitation in domain_limitations:
            limitations.append(f"{label}: {limitation}")

    if not limitations:
        limitations.append(
            "Unavailable evidence is not replaced with simulated or "
            "fabricated records."
        )

    for limitation in limitations:
        story.append(
            Paragraph(
                f"• {escape(str(limitation))}",
                body_style,
            )
        )

    story.append(
        Paragraph(
            "Opportunity score is a normalized decision-support signal, "
            "not a financial, medical or legal recommendation. Evidence "
            "confidence is reported separately from the opportunity score.",
            body_style,
        )
    )

    # ------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------
    story.append(Paragraph("Evidence Sources", section_style))

    sources = []

    clinical_source = clinical.get("source")
    if clinical_source:
        sources.append(("Clinical", clinical_source))

    market_source = market.get("source")
    if market_source:
        if isinstance(market_source, dict):
            sources.append(
                (
                    "Market",
                    market_source.get("name", "Market source"),
                )
            )
        else:
            sources.append(("Market", market_source))

    secondary_source = market.get("secondary_source")
    if secondary_source:
        if isinstance(secondary_source, dict):
            sources.append(
                (
                    "Secondary context",
                    secondary_source.get("name", "Secondary source"),
                )
            )
        else:
            sources.append(("Secondary context", secondary_source))

    if patent.get("source"):
        sources.append(("IP", patent.get("source")))

    if sources:
        source_rows = [["Domain", "Source"]]
        source_rows.extend(
            [[domain, source] for domain, source in sources]
        )
        story.append(
            _make_table(
                source_rows,
                [45 * mm, 129 * mm],
                font_size=8,
            )
        )
    else:
        story.append(
            Paragraph("No source metadata was returned.", body_style)
        )

    # ------------------------------------------------------------
    # Disclaimer
    # ------------------------------------------------------------
    story.append(Spacer(1, 7))
    disclaimer = Table(
        [
            [
                Paragraph(
                    "<b>Disclaimer</b><br/>"
                    "PharmIntel is a research and decision-support prototype. "
                    "It does not provide medical advice, legal advice, "
                    "definitive Freedom-to-Operate opinions, or investment "
                    "guarantees.",
                    small_style,
                )
            ]
        ],
        colWidths=[174 * mm],
    )
    disclaimer.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#DCE3EA"),
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(disclaimer)

    doc.build(
        story,
        onFirstPage=_footer,
        onLaterPages=_footer,
    )

    return file_path
