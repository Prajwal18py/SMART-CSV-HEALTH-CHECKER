"""
PDF Report Generation
Generate comprehensive PDF reports with dark professional theme
"""
from io import BytesIO
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Try importing reportlab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        PageBreak, HRFlowable, KeepTogether
    )
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════
# DARK THEME PALETTE (matching EDA/Model Builder)
# ══════════════════════════════════════════════════════════════════════
C_BG       = colors.HexColor("#0f172a")
C_CARD     = colors.HexColor("#1e293b")
C_CARD2    = colors.HexColor("#1a2840")
C_INDIGO   = colors.HexColor("#6366f1")
C_IND_L    = colors.HexColor("#a5b4fc")
C_GREEN    = colors.HexColor("#6ee7b7")
C_YELLOW   = colors.HexColor("#fbbf24")
C_RED      = colors.HexColor("#f87171")
C_TEXT     = colors.HexColor("#e2e8f0")
C_MUTED    = colors.HexColor("#94a3b8")
C_BORDER   = colors.HexColor("#334155")


def clean_text_for_pdf(text):
    """Remove non-ASCII characters for PDF compatibility"""
    return re.sub(r'[^\x00-\x7F]+', '', str(text)).strip()


def generate_pdf(df, results):
    """
    Generate comprehensive dark-themed PDF report
    
    Args:
        df: DataFrame
        results: Analysis results dictionary
    
    Returns:
        BytesIO buffer containing PDF
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title="Data Health Report",
        author="DataForge Studio"
    )
    
    W = A4[0] - 36*mm  # usable width
    
    # ══════════════════════════════════════════════════════════════════
    # STYLE DEFINITIONS
    # ══════════════════════════════════════════════════════════════════
    def S(name, **kw):
        return ParagraphStyle(name, **kw)
    
    sTitle = S("T", fontSize=26, textColor=colors.white,
               fontName="Helvetica-Bold", alignment=TA_CENTER)
    sSub   = S("Su", fontSize=10, textColor=C_IND_L,
               fontName="Helvetica", alignment=TA_CENTER)
    sH1    = S("H1", fontSize=13, textColor=C_IND_L,
               fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=5)
    sH2    = S("H2", fontSize=10, textColor=C_TEXT,
               fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
    sBody  = S("Bo", fontSize=9, textColor=C_MUTED,
               fontName="Helvetica", spaceAfter=2, leading=13)
    
    def divider():
        return HRFlowable(width="100%", thickness=1,
                          color=C_INDIGO, spaceAfter=8, spaceBefore=2)
    
    # ══════════════════════════════════════════════════════════════════
    # BUILD STORY
    # ══════════════════════════════════════════════════════════════════
    story = []
    
    # ──────────────────────────────────────────────────────────────────
    # COVER PAGE
    # ──────────────────────────────────────────────────────────────────
    cover = Table([[Paragraph("Data Health Report", sTitle)]], colWidths=[W])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 22),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
        ("BOX",           (0, 0), (-1, -1), 2, C_INDIGO),
    ]))
    story.append(cover)
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Generated: {now}  •  DataForge Studio", sSub))
    story.append(Spacer(1, 20))
    
    # ──────────────────────────────────────────────────────────────────
    # HEALTH SCORE BADGE
    # ──────────────────────────────────────────────────────────────────
    score = results['health_score']
    
    # Determine grade and color
    if score >= 90:
        grade, grade_desc, score_color = 'A+', 'Excellent', C_GREEN
    elif score >= 80:
        grade, grade_desc, score_color = 'A', 'Very Good', C_GREEN
    elif score >= 70:
        grade, grade_desc, score_color = 'B', 'Good', C_IND_L
    elif score >= 60:
        grade, grade_desc, score_color = 'C', 'Fair', C_YELLOW
    elif score >= 50:
        grade, grade_desc, score_color = 'D', 'Poor', C_RED
    else:
        grade, grade_desc, score_color = 'F', 'Critical', C_RED
    
    score_para = Paragraph(
        f'<b><font size="36" color="{score_color.hexval()}">{score}/100</font></b><br/>'
        f'<font size="14" color="{score_color.hexval()}">Grade {grade}</font><br/>'
        f'<font size="9" color="{C_MUTED.hexval()}">{grade_desc}</font>',
        S("sc", fontName="Helvetica-Bold", alignment=TA_CENTER, leading=36)
    )
    
    score_box = Table([[score_para]], colWidths=[W])
    score_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_CARD),
        ("BOX",           (0, 0), (-1, -1), 2, score_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(score_box)
    story.append(Spacer(1, 16))
    
    # ──────────────────────────────────────────────────────────────────
    # DATASET OVERVIEW
    # ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("1. Dataset Overview", sH1))
    story.append(divider())
    
    overview_pairs = [
        ("Rows",    f"{len(df):,}"),
        ("Columns", f"{len(df.columns):,}"),
        ("Memory",  f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"),
        ("Numeric", f"{len(df.select_dtypes(include=[np.number]).columns)}"),
        ("Categorical", f"{len(df.select_dtypes(include=['object', 'category']).columns)}"),
    ]
    
    ov_rows = [
        [
            Paragraph(f"<b>{k}</b>", S("ok", fontSize=8, textColor=C_MUTED,
                                        fontName="Helvetica-Bold")),
            Paragraph(v, S("ov", fontSize=8, textColor=C_TEXT, fontName="Courier")),
        ]
        for k, v in overview_pairs
    ]
    
    ov_tbl = Table(ov_rows, colWidths=[W * 0.35, W * 0.65])
    ov_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, C_CARD2]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
    ]))
    story.append(ov_tbl)
    story.append(Spacer(1, 12))
    
    # ──────────────────────────────────────────────────────────────────
    # ISSUES DETECTED
    # ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("2. Issues Detected", sH1))
    story.append(divider())
    
    if not results['issues']:
        no_issues_para = Paragraph(
            '<font color="#6ee7b7">✅ No critical issues detected. Data quality is excellent.</font>',
            S("ni", fontSize=9, textColor=C_GREEN, fontName="Helvetica")
        )
        story.append(no_issues_para)
    else:
        # Group issues by severity
        critical_issues = [i for i in results['issues'] if i['severity'] == 'High']
        warning_issues  = [i for i in results['issues'] if i['severity'] == 'Medium']
        info_issues     = [i for i in results['issues'] if i['severity'] == 'Low']
        
        # Critical issues
        if critical_issues:
            story.append(Paragraph("Critical Issues", sH2))
            for issue in critical_issues[:10]:  # top 10
                icon = "🚨" if "AI" not in issue['type'] else "🤖"
                issue_text = f"{icon} <b>{clean_text_for_pdf(issue['type'])}</b>: {clean_text_for_pdf(issue['message'])}"
                issue_data = [[Paragraph(issue_text, S("iss", fontSize=8, textColor=C_TEXT, fontName="Helvetica"))]]
                issue_tbl = Table(issue_data, colWidths=[W])
                issue_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#2d1515")),
                    ("BOX",           (0, 0), (-1, -1), 1, C_RED),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("TOPPADDING",    (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.append(issue_tbl)
                story.append(Spacer(1, 4))
        
        # Warning issues (show first 5)
        if warning_issues:
            story.append(Paragraph("Warnings", sH2))
            for issue in warning_issues[:5]:
                icon = "⚠️"
                issue_text = f"{icon} <b>{clean_text_for_pdf(issue['type'])}</b>: {clean_text_for_pdf(issue['message'])}"
                issue_data = [[Paragraph(issue_text, S("iss", fontSize=8, textColor=C_TEXT, fontName="Helvetica"))]]
                issue_tbl = Table(issue_data, colWidths=[W])
                issue_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#2d2515")),
                    ("BOX",           (0, 0), (-1, -1), 1, C_YELLOW),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("TOPPADDING",    (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.append(issue_tbl)
                story.append(Spacer(1, 4))
    
    story.append(Spacer(1, 12))
    
    # ──────────────────────────────────────────────────────────────────
    # RECOMMENDATIONS
    # ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("3. Recommendations", sH1))
    story.append(divider())
    
    if not results['recommendations']:
        rec_para = Paragraph(
            '<font color="#6ee7b7">✨ No additional actions needed. Keep up the good work!</font>',
            S("rec", fontSize=9, textColor=C_GREEN, fontName="Helvetica")
        )
        story.append(rec_para)
    else:
        for idx, rec in enumerate(results['recommendations'][:10], 1):
            rec_text = f"<b>{idx}.</b> {clean_text_for_pdf(rec)}"
            rec_data = [[Paragraph(rec_text, S("rec", fontSize=8, textColor=C_TEXT, fontName="Helvetica"))]]
            rec_tbl = Table(rec_data, colWidths=[W])
            rec_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C_CARD),
                ("BOX",           (0, 0), (-1, -1), 0.5, C_INDIGO),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(rec_tbl)
            story.append(Spacer(1, 4))
    
    story.append(Spacer(1, 12))
    
    # ──────────────────────────────────────────────────────────────────
    # COLUMN SUMMARY (Top issues per column)
    # ──────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4. Column Quality Summary", sH1))
    story.append(divider())
    
    col_data = [
        [
            Paragraph("<b>Column</b>", S("ch", fontSize=8, textColor=colors.white,
                                          fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>Type</b>", S("ch", fontSize=8, textColor=colors.white,
                                        fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>Missing %</b>", S("ch", fontSize=8, textColor=colors.white,
                                             fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>Unique</b>", S("ch", fontSize=8, textColor=colors.white,
                                          fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>Status</b>", S("ch", fontSize=8, textColor=colors.white,
                                          fontName="Helvetica-Bold", alignment=TA_CENTER)),
        ]
    ]
    
    for col in df.columns[:30]:  # first 30 columns
        dtype = str(df[col].dtype)
        missing_pct = df[col].isna().mean() * 100
        unique = df[col].nunique()
        
        # Determine status color
        if missing_pct > 20:
            status = '<font color="#f87171">⚠️ High Missing</font>'
        elif missing_pct > 5:
            status = '<font color="#fbbf24">⚠️ Some Missing</font>'
        elif unique == 1:
            status = '<font color="#94a3b8">Constant</font>'
        else:
            status = '<font color="#6ee7b7">✓ OK</font>'
        
        col_data.append([
            Paragraph(clean_text_for_pdf(col)[:25], S("cc", fontSize=7, textColor=C_IND_L, fontName="Courier")),
            Paragraph(dtype[:15], S("cc", fontSize=7, textColor=C_MUTED, fontName="Courier", alignment=TA_CENTER)),
            Paragraph(f"{missing_pct:.1f}%", S("cc", fontSize=7, textColor=C_TEXT, fontName="Courier", alignment=TA_CENTER)),
            Paragraph(f"{unique:,}", S("cc", fontSize=7, textColor=C_TEXT, fontName="Courier", alignment=TA_CENTER)),
            Paragraph(status, S("cc", fontSize=7, alignment=TA_CENTER)),
        ])
    
    col_tbl = Table(col_data, colWidths=[W*0.30, W*0.15, W*0.15, W*0.15, W*0.25])
    col_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_INDIGO),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_CARD, C_CARD2]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.25, C_BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(col_tbl)
    
    if len(df.columns) > 30:
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            f'<i>Showing first 30 of {len(df.columns)} columns. '
            f'Full analysis available in the interactive dashboard.</i>',
            S("note", fontSize=7, textColor=C_MUTED, fontName="Helvetica-Oblique")
        ))
    
    # ──────────────────────────────────────────────────────────────────
    # FOOTER
    # ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_INDIGO))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated by DataForge Studio  •  {now}",
        S("ft", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_executive_scorecard(df, results):
    """
    Create executive one-page summary with dark theme
    
    Args:
        df: DataFrame
        results: Analysis results
    
    Returns:
        BytesIO buffer or None if reportlab unavailable
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title="Executive Scorecard",
        author="DataForge Studio"
    )
    
    W = A4[0] - 36*mm
    
    # ══════════════════════════════════════════════════════════════════
    # STYLES
    # ══════════════════════════════════════════════════════════════════
    def S(name, **kw):
        return ParagraphStyle(name, **kw)
    
    sTitle = S("T", fontSize=22, textColor=colors.white,
               fontName="Helvetica-Bold", alignment=TA_CENTER)
    sSub   = S("Su", fontSize=9, textColor=C_IND_L,
               fontName="Helvetica", alignment=TA_CENTER)
    sBody  = S("Bo", fontSize=9, textColor=C_TEXT, fontName="Helvetica")
    
    story = []
    
    # ──────────────────────────────────────────────────────────────────
    # TITLE
    # ──────────────────────────────────────────────────────────────────
    title_tbl = Table([[Paragraph("Executive Scorecard", sTitle)]], colWidths=[W])
    title_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("BOX",           (0, 0), (-1, -1), 2, C_INDIGO),
    ]))
    story.append(title_tbl)
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"{now}  •  DataForge Studio", sSub))
    story.append(Spacer(1, 16))
    
    # ──────────────────────────────────────────────────────────────────
    # SCORE BADGE + KEY METRICS
    # ──────────────────────────────────────────────────────────────────
    score = results['health_score']
    
    if score >= 90:
        grade, score_color = 'A+', C_GREEN
    elif score >= 80:
        grade, score_color = 'A', C_GREEN
    elif score >= 70:
        grade, score_color = 'B', C_IND_L
    elif score >= 60:
        grade, score_color = 'C', C_YELLOW
    else:
        grade, score_color = 'F', C_RED
    
    score_para = Paragraph(
        f'<b><font size="32" color="{score_color.hexval()}">{score}/100</font></b><br/>'
        f'<font size="12" color="{score_color.hexval()}">Grade {grade}</font>',
        S("sc", fontName="Helvetica-Bold", alignment=TA_CENTER, leading=32)
    )
    score_box = Table([[score_para]], colWidths=[W * 0.25])
    score_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_CARD),
        ("BOX",           (0, 0), (-1, -1), 2, score_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    
    # Key metrics table
    critical_count = len([i for i in results['issues'] if i['severity'] == 'High'])
    warning_count = len([i for i in results['issues'] if i['severity'] == 'Medium'])
    
    metrics_pairs = [
        ("Dataset Size",     f"{len(df):,} rows × {len(df.columns)} columns"),
        ("Critical Issues",  f"{critical_count}"),
        ("Warnings",         f"{warning_count}"),
        ("Recommendations",  f"{len(results['recommendations'])}"),
    ]
    
    metrics_rows = [
        [
            Paragraph(f"<b>{k}</b>", S("mk", fontSize=8, textColor=C_MUTED, fontName="Helvetica-Bold")),
            Paragraph(v, S("mv", fontSize=8, textColor=C_TEXT, fontName="Courier")),
        ]
        for k, v in metrics_pairs
    ]
    
    metrics_tbl = Table(metrics_rows, colWidths=[W * 0.30, W * 0.45])
    metrics_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, C_CARD2]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
    ]))
    
    # Combine score + metrics side by side
    header_row = Table([[score_box, Spacer(6, 1), metrics_tbl]],
                       colWidths=[W * 0.25, 6, W * 0.75 - 6])
    header_row.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(header_row)
    story.append(Spacer(1, 16))
    
    # ──────────────────────────────────────────────────────────────────
    # TOP ISSUES
    # ──────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        '<font color="#a5b4fc"><b>Top Issues Requiring Attention</b></font>',
        S("h", fontSize=11, textColor=C_IND_L, fontName="Helvetica-Bold")
    ))
    story.append(Spacer(1, 6))
    
    top_issues = [i for i in results['issues'] if i['severity'] == 'High'][:5]
    if not top_issues:
        story.append(Paragraph(
            '<font color="#6ee7b7">✅ No critical issues detected.</font>',
            S("ni", fontSize=9, textColor=C_GREEN)
        ))
    else:
        for issue in top_issues:
            issue_text = f"🚨 <b>{clean_text_for_pdf(issue['type'])}</b>: {clean_text_for_pdf(issue['message'][:80])}..."
            issue_data = [[Paragraph(issue_text, S("iss", fontSize=8, textColor=C_TEXT, fontName="Helvetica"))]]
            issue_tbl = Table(issue_data, colWidths=[W])
            issue_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#2d1515")),
                ("BOX",           (0, 0), (-1, -1), 1, C_RED),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(issue_tbl)
            story.append(Spacer(1, 4))
    
    story.append(Spacer(1, 12))
    
    # ──────────────────────────────────────────────────────────────────
    # RECOMMENDATIONS (Top 3)
    # ──────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        '<font color="#a5b4fc"><b>Recommended Actions</b></font>',
        S("h", fontSize=11, textColor=C_IND_L, fontName="Helvetica-Bold")
    ))
    story.append(Spacer(1, 6))
    
    for idx, rec in enumerate(results['recommendations'][:3], 1):
        rec_text = f"<b>{idx}.</b> {clean_text_for_pdf(rec)}"
        rec_data = [[Paragraph(rec_text, S("rec", fontSize=8, textColor=C_TEXT, fontName="Helvetica"))]]
        rec_tbl = Table(rec_data, colWidths=[W])
        rec_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_CARD),
            ("BOX",           (0, 0), (-1, -1), 0.5, C_INDIGO),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(rec_tbl)
        story.append(Spacer(1, 4))
    
    # ──────────────────────────────────────────────────────────────────
    # FOOTER
    # ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_INDIGO))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated by DataForge Studio  •  {now}",
        S("ft", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer