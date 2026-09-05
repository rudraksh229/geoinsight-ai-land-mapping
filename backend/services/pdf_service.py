import os
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# PDF REPORT GENERATION
# ============================================================

def _safe_filename(value):
    """
    Convert a value into a filesystem-safe filename.
    """

    value = str(value or "unknown")

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value,
    )

    value = value.strip(
        "_"
    )

    return value or "unknown"


def _safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return default

        number = float(value)

        if number != number:
            return default

        if number in (
            float("inf"),
            float("-inf"),
        ):
            return default

        return number

    except (
        TypeError,
        ValueError,
    ):
        return default


def _safe_text(value, default="N/A"):
    """
    Safely convert a value to text.
    """

    if value is None:
        return default

    text = str(value).strip()

    return text or default


def generate_pdf(data: dict):
    """
    Generate a GeoInsight AI land-analysis PDF report.

    Expected data fields:

        village
        district
        state
        date
        latitude
        longitude
        total_area
        vegetation
        water
        builtup
        barren
        ndvi
        ndwi
        ndbi
        prediction
        confidence
        recommendation
    """

    if not isinstance(data, dict):
        raise ValueError(
            "PDF data must be provided as a dictionary."
        )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    output_directory = os.path.join(
        os.getcwd(),
        "generated_reports",
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Safe filename
    # --------------------------------------------------------

    village = _safe_filename(
        data.get(
            "village",
            "unknown",
        )
    )

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = os.path.join(
        output_directory,
        f"report_{village}_{timestamp}.pdf",
    )

    # --------------------------------------------------------
    # Document configuration
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
        title="GeoInsight AI Land Analysis Report",
        author="GeoInsight AI",
    )

    # --------------------------------------------------------
    # Styles
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "GeoInsightTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "GeoInsightSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "GeoInsightSection",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
    )

    normal_style = ParagraphStyle(
        "GeoInsightNormal",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
    )

    # --------------------------------------------------------
    # Extract values safely
    # --------------------------------------------------------

    village_name = _safe_text(
        data.get("village")
    )

    district = _safe_text(
        data.get("district")
    )

    state = _safe_text(
        data.get("state")
    )

    date_value = _safe_text(
        data.get("date")
    )

    latitude = _safe_float(
        data.get("latitude")
    )

    longitude = _safe_float(
        data.get("longitude")
    )

    total_area = _safe_float(
        data.get("total_area")
    )

    vegetation = _safe_float(
        data.get("vegetation")
    )

    water = _safe_float(
        data.get("water")
    )

    builtup = _safe_float(
        data.get("builtup")
    )

    barren = _safe_float(
        data.get("barren")
    )

    ndvi = _safe_float(
        data.get("ndvi")
    )

    ndwi = _safe_float(
        data.get("ndwi")
    )

    ndbi = _safe_float(
        data.get("ndbi")
    )

    prediction = _safe_text(
        data.get("prediction")
    )

    confidence = _safe_float(
        data.get("confidence")
    )

    recommendation = _safe_text(
        data.get("recommendation")
    )

    # --------------------------------------------------------
    # Build document
    # --------------------------------------------------------

    elements = []

    elements.append(
        Paragraph(
            "<b>GeoInsight AI Land Analysis Report</b>",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            "AI-based Land Mapping & Analysis System",
            subtitle_style,
        )
    )

    # --------------------------------------------------------
    # Location Information
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Location Information</b>",
            section_style,
        )
    )

    location_data = [
        ["Field", "Value"],

        [
            "Village",
            village_name,
        ],

        [
            "District",
            district,
        ],

        [
            "State",
            state,
        ],

        [
            "Date",
            date_value,
        ],

        [
            "Latitude",
            f"{latitude:.6f}",
        ],

        [
            "Longitude",
            f"{longitude:.6f}",
        ],
    ]

    location_table = Table(
        location_data,
        colWidths=[
            2.2 * inch,
            3.5 * inch,
        ],
        repeatRows=1,
    )

    location_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkgreen,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elements.append(
        location_table
    )

    elements.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # Land-Cover Information
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Land-Cover Analysis</b>",
            section_style,
        )
    )

    land_cover_data = [
        ["Land Type", "Area (ha)"],

        [
            "Total Area",
            f"{total_area:.2f}",
        ],

        [
            "Vegetation",
            f"{vegetation:.2f}",
        ],

        [
            "Water",
            f"{water:.2f}",
        ],

        [
            "Built-up",
            f"{builtup:.2f}",
        ],

        [
            "Barren",
            f"{barren:.2f}",
        ],
    ]

    land_cover_table = Table(
        land_cover_data,
        colWidths=[
            2.8 * inch,
            2.9 * inch,
        ],
        repeatRows=1,
    )

    land_cover_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkgreen,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "RIGHT",
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elements.append(
        land_cover_table
    )

    elements.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # Spectral Indices
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Satellite Spectral Indices</b>",
            section_style,
        )
    )

    indices_data = [
        ["Index", "Value"],

        [
            "NDVI",
            f"{ndvi:.4f}",
        ],

        [
            "NDWI",
            f"{ndwi:.4f}",
        ],

        [
            "NDBI",
            f"{ndbi:.4f}",
        ],
    ]

    indices_table = Table(
        indices_data,
        colWidths=[
            2.8 * inch,
            2.9 * inch,
        ],
        repeatRows=1,
    )

    indices_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkgreen,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "RIGHT",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elements.append(
        indices_table
    )

    elements.append(
        Spacer(
            1,
            12,
        )
    )

    # --------------------------------------------------------
    # AI Analysis
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "<b>AI Analysis</b>",
            section_style,
        )
    )

    ai_data = [
        ["Field", "Value"],

        [
            "AI Prediction",
            prediction,
        ],

        [
            "AI Confidence",
            f"{confidence:.2f}%",
        ],

        [
            "Recommendation",
            Paragraph(
                recommendation,
                normal_style,
            ),
        ],
    ]

    ai_table = Table(
        ai_data,
        colWidths=[
            2.2 * inch,
            3.5 * inch,
        ],
        repeatRows=1,
    )

    ai_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkgreen,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    elements.append(
        ai_table
    )

    elements.append(
        Spacer(
            1,
            20,
        )
    )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "<b>Generated by GeoInsight AI</b><br/>"
            "AI-based Land Mapping & Analysis System<br/>"
            "VIT Bhopal University",
            normal_style,
        )
    )

    # --------------------------------------------------------
    # Generate PDF
    # --------------------------------------------------------

    try:
        document.build(
            elements
        )

    except Exception as exc:
        raise RuntimeError(
            "Failed to generate PDF report. "
            f"Reason: {exc}"
        ) from exc

    return filename
