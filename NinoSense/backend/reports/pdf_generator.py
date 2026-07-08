import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def generate_report_pdf(output_path, current_status, forecast_list):
    """
    Generates a professional, government-style PDF report summarizing the current climate state
    and listing the 6-month ahead El Niño / La Niña predictions.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'GovTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'), # Slate 900
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'GovSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#d97706'), # Gold / Amber 600
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e3a8a'), # Deep Blue
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'GovBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'), # Slate 700
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'GovBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []
    
    # 1. Government Banner Header
    story.append(Paragraph("NINOSENSE CLIMATE INTELLIGENCE SYSTEM", title_style))
    story.append(Paragraph("OFFICIAL METEOROLOGICAL BULLETIN & ENSO FORECAST", subtitle_style))
    
    # Add a visual separator line
    sep_data = [['']]
    sep_table = Table(sep_data, colWidths=[504], rowHeights=[2])
    sep_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e3a8a')),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(sep_table)
    story.append(Spacer(1, 15))
    
    # 2. Document Info (Date, Issuer)
    current_date = datetime.now().strftime("%B %d, %Y")
    info_text = f"<b>Report Issued:</b> {current_date}<br/><b>Issuing Agency:</b> Department of Climate Dynamics, NinoSense Advisory Board"
    story.append(Paragraph(info_text, body_style))
    story.append(Spacer(1, 10))
    
    # 3. Executive Summary Section
    story.append(Paragraph("1. Executive Summary", section_heading))
    
    val = current_status['value']
    phase = current_status['phase']
    intensity = current_status['intensity']
    period = current_status['period_txt']
    
    summary_text = (
        f"This official bulletin presents the current status and predictive outlook of the "
        f"El Niño-Southern Oscillation (ENSO) cycle. Based on oceanographic data collected up to the "
        f"latest reporting period (<b>{period}</b>), sea surface temperature anomalies in the central Pacific Ocean "
        f"exhibit an Oceanic Niño Index (ONI) of <b>{val}°C</b>, placing the current climate cycle under a "
        f"<b>{intensity if intensity != 'N/A' else ''} {phase}</b> phase."
    )
    story.append(Paragraph(summary_text, body_style))
    
    # Impacts Summary
    story.append(Paragraph("Key observed regional highlights include:", body_style))
    if phase == "El Niño":
        story.append(Paragraph("• <b>Atmospheric Circulation:</b> Reduced easterly trade winds and displacement of tropical rainfall eastward.", bullet_style))
        story.append(Paragraph("• <b>Impact Outlook:</b> Higher risk of drought conditions in Australia/Indonesia and heavy precipitation in South America/Southern United States.", bullet_style))
    elif phase == "La Niña":
        story.append(Paragraph("• <b>Atmospheric Circulation:</b> Enhanced easterly trade winds resulting in cooler sea surface temperatures in the equatorial Pacific.", bullet_style))
        story.append(Paragraph("• <b>Impact Outlook:</b> Increased precipitation across Southeast Asia/Australia, and cooler, wetter winters in the Northern US/Canada.", bullet_style))
    else:
        story.append(Paragraph("• <b>Atmospheric Circulation:</b> Standard Walker circulation patterns are functioning under historical baselines.", bullet_style))
        story.append(Paragraph("• <b>Impact Outlook:</b> Near-normal seasonal weather ranges are expected globally over the next quarter.", bullet_style))
        
    story.append(Spacer(1, 10))
    
    # 4. Current Observations Table
    story.append(Paragraph("2. Current Observations Details", section_heading))
    obs_data = [
        [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Observed Value</b>", body_style), Paragraph("<b>Climatic Meaning</b>", body_style)],
        ["Reporting Period", period, "Latest recorded season"],
        ["Oceanic Niño Index (ONI)", f"{val}°C", "3-month running mean SST anomaly in Niño 3.4"],
        ["Active Phase Status", phase, "Current ENSO cycle condition"],
        ["Severity Classification", intensity, "Magnitude of SST anomaly deviations"],
    ]
    
    obs_table = Table(obs_data, colWidths=[150, 120, 234])
    obs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(obs_table)
    story.append(Spacer(1, 15))
    
    # 5. ML Predictive Outlook Section
    story.append(Paragraph("3. 6-Month Machine Learning Forecasting Outlook", section_heading))
    story.append(Paragraph("The predictions below are generated using a Random Forest Regressor trained on historical ONI data since 1950. The model accounts for seasonal oscillations, rolling mean anomalies, and historical lag parameters.", body_style))
    
    forecast_data = [
        ["Month Out", "Period", "Predicted ONI", "Expected Phase", "Confidence Interval"]
    ]
    
    for item in forecast_list:
        forecast_data.append([
            f"+{item['step']} Month(s)",
            item['period_txt'],
            f"{item['value']}°C",
            f"{item['intensity'] if item['intensity'] != 'N/A' else ''} {item['phase']}",
            f"{item['value_lower']}°C to {item['value_upper']}°C"
        ])
        
    forecast_table = Table(forecast_data, colWidths=[80, 100, 100, 114, 110])
    forecast_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(forecast_table)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Disclaimer: This report represents simulated forecasts based on computational models. It should be used for research and planning purposes. Government operations should coordinate directly with the national meteorological agency.</i>", ParagraphStyle('Dis', parent=styles['Italic'], fontSize=8, leading=10, textColor=colors.HexColor('#64748b'))))
    
    # Build the document
    doc.build(story)
