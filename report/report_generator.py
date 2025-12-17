from datetime import datetime
from textwrap import wrap

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def _draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: int,
    y: int,
    max_width: int,
    line_height: int,
) -> int:
    """
    Draw text with simple word-wrapping and return the new y position.
    """
    if not text:
        return y

    # Rough approximation: characters per line based on width
    # (Helvetica 10 ~ 6 points per character on average)
    max_chars_per_line = max(int(max_width / 6), 20)
    lines = []
    for paragraph in str(text).split("\n"):
        if not paragraph.strip():
            lines.append("")  # blank line
        else:
            lines.extend(wrap(paragraph, max_chars_per_line))

    for line in lines:
        if y < 50:  # start a new page if we're too close to the bottom
            c.showPage()
            c.setFont("Helvetica", 10)
            y = A4[1] - 50
        c.drawString(x, y, line)
        y -= line_height

    return y


def generate_pdf_report(results, user_query: str) -> str:
    """
    Generate a simple PDF report summarising the agents' outputs.

    Returns the path to the generated PDF file.
    """
    file_path = "agentic_pharma_report.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Agentic AI – Pharma Innovation Report")
    y -= 30

    # Metadata
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"User Query: {user_query}")
    y -= 15
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    content_width = int(width - 100)  # left margin 50, right margin 50

    # Clinical Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Clinical Trials Summary")
    y -= 20
    c.setFont("Helvetica", 10)
    clinical_text = results.get("clinical", {}).get(
        "summary", "No clinical summary available."
    )
    y = _draw_wrapped_text(c, clinical_text, 50, y, content_width, line_height=14)
    y -= 10

    # Patent Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Patent Landscape Summary")
    y -= 20
    c.setFont("Helvetica", 10)
    patent_text = results.get("patent", {}).get(
        "summary", "No patent summary available."
    )
    y = _draw_wrapped_text(c, patent_text, 50, y, content_width, line_height=14)
    y -= 10

    # Market Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Market Overview")
    y -= 20
    c.setFont("Helvetica", 10)
    market_summary = results.get("market", {}).get(
        "summary", "No market summary available."
    )
    y = _draw_wrapped_text(c, market_summary, 50, y, content_width, line_height=14)

    # Finalise PDF
    c.showPage()
    c.save()

    return file_path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from textwrap import wrap


def _draw_wrapped_text(c: canvas.Canvas, text: str, x: int, y: int, max_width: int, line_height: int) -> int:
    """
    Draws text with simple word-wrapping and returns the new y position.
    """
    if not text:
        return y

    # Rough approximation: characters per line based on width
    # (Helvetica 10 ~ 6 points per character on average)
    max_chars_per_line = max(int(max_width / 6), 20)
    lines = []
    for paragraph in str(text).split("\n"):
        if not paragraph.strip():
            lines.append("")  # blank line
        else:
            lines.extend(wrap(paragraph, max_chars_per_line))

    for line in lines:
        if y < 50:  # start a new page if we're too close to the bottom
            c.showPage()
            c.setFont("Helvetica", 10)
            y = A4[1] - 50
        c.drawString(x, y, line)
        y -= line_height

    return y


def generate_pdf_report(results, user_query):
    file_path = "agentic_pharma_report.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Agentic AI – Pharma Innovation Report")
    y -= 30

    # Metadata
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"User Query: {user_query}")
    y -= 15
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    content_width = int(width - 100)  # left margin 50, right margin 50

    # Clinical Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Clinical Trials Summary")
    y -= 20
    c.setFont("Helvetica", 10)
    clinical_text = results.get("clinical", {}).get("summary", "No clinical summary available.")
    y = _draw_wrapped_text(c, clinical_text, 50, y, content_width, line_height=14)
    y -= 10

    # Patent Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Patent Landscape Summary")
    y -= 20
    c.setFont("Helvetica", 10)
    patent_text = results.get("patent", {}).get("summary", "No patent summary available.")
    y = _draw_wrapped_text(c, patent_text, 50, y, content_width, line_height=14)
    y -= 10

    # Market Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Market Overview")
    y -= 20
    c.setFont("Helvetica", 10)
    market_summary = results.get("market", {}).get("summary", "No market summary available.")
    y = _draw_wrapped_text(c, market_summary, 50, y, content_width, line_height=14)

    # Finalize PDF
    c.showPage()
    c.save()

    return file_path

