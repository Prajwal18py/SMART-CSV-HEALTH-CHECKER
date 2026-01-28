"""
PDF Report Generation
Generate comprehensive PDF reports and executive scorecards
"""
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import re

from features.statistics import get_health_grade

# Try importing reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def clean_text_for_pdf(text):
    """Remove non-ASCII characters for PDF compatibility"""
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()


def generate_pdf(df, results):
    """
    Generate comprehensive PDF report with matplotlib
    
    Args:
        df: DataFrame
        results: Analysis results dictionary
    
    Returns:
        BytesIO buffer containing PDF
    """
    buffer = BytesIO()
    plt.style.use('default')
    
    try:
        with PdfPages(buffer) as pdf:
            # PAGE 1: SUMMARY
            fig = plt.figure(figsize=(8.5, 11))
            
            # Title
            plt.text(0.5, 0.95, 'AI Data Health Report', 
                    ha='center', fontsize=24, fontweight='bold')
            
            # Health Score
            score = results['health_score']
            if score >= 90:
                color = '#00c851'
            elif score >= 80:
                color = '#7cb342'
            elif score >= 70:
                color = '#ffc107'
            elif score >= 60:
                color = '#ff9800'
            else:
                color = '#ff4444'
            
            grade = get_health_grade(score)
            grade_desc = {
                'A+': '(Excellent)', 'A': '(Very Good)', 'B': '(Good)',
                'C': '(Fair)', 'D': '(Poor)', 'F': '(Critical)'
            }
            
            # Display score
            plt.text(0.5, 0.80, f"{score}/100", 
                    ha='center', fontsize=45, fontweight='bold', color=color)
            plt.text(0.5, 0.70, f"{grade} {grade_desc.get(grade, '')}", 
                    ha='center', fontsize=24, color=color)
            
            # Issues list
            y = 0.55
            for issue in results['issues'][:12]:
                plt.text(0.1, y, 
                        f"[{issue['severity'][0]}] {clean_text_for_pdf(issue['message'])}", 
                        fontsize=9)
                y -= 0.03
            
            # Footer
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            plt.text(0.5, 0.05, f"Generated: {current_time}", 
                    ha='center', fontsize=8, color='gray')
            plt.text(0.95, 0.02, f"Page 1", 
                    ha='right', fontsize=8, color='gray')
            
            plt.axis('off')
            pdf.savefig(fig)
            plt.close()
            
            # PAGE 2: CORRELATION HEATMAP (if available)
            if 'correlation' in results['visualizations']:
                fig2, ax = plt.subplots(figsize=(8.5, 11))
                corr = results['visualizations']['correlation']
                
                # Plot heatmap
                im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
                ax.set_title('Feature Correlation Matrix', fontsize=16, pad=20)
                
                # Labels
                ax.set_xticks(range(len(corr.columns)))
                ax.set_yticks(range(len(corr.columns)))
                ax.set_xticklabels(corr.columns, rotation=45, ha='right', fontsize=8)
                ax.set_yticklabels(corr.columns, fontsize=8)
                
                plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                
                # Footer
                plt.text(0.5, 0.05, f"Generated: {current_time}", 
                        ha='center', fontsize=8, color='gray', 
                        transform=fig2.transFigure)
                plt.text(0.95, 0.02, f"Page 2", 
                        ha='right', fontsize=8, color='gray', 
                        transform=fig2.transFigure)
                
                plt.tight_layout(rect=[0, 0.06, 1, 0.95])
                pdf.savefig(fig2)
                plt.close()
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
    
    buffer.seek(0)
    return buffer


def generate_executive_scorecard(df, results):
    """
    Create executive one-page summary using reportlab
    
    Args:
        df: DataFrame
        results: Analysis results
    
    Returns:
        BytesIO buffer or None if reportlab unavailable
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>Data Quality Scorecard</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Executive Summary
    summary = f"""
    <b>Overall Grade:</b> {get_health_grade(results['health_score'])} ({results['health_score']}/100)<br/>
    <b>Dataset Size:</b> {len(df):,} rows x {len(df.columns)} columns<br/>
    <b>Critical Issues:</b> {len([i for i in results['issues'] if i['severity'] == 'High'])}<br/>
    <b>AI Anomalies:</b> {len(results['stats']['ai_anomalies']['indices']) if results['stats']['ai_anomalies'] else 0}
    """
    elements.append(Paragraph(summary, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Issue Summary Table
    issue_data = [['Issue Type', 'Count', 'Action Needed']]
    issue_counts = {}
    
    for issue in results['issues']:
        issue_type = issue['type']
        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
    
    for issue_type, count in issue_counts.items():
        issue_data.append([issue_type, str(count), 'Review & Clean'])
    
    table = Table(issue_data)
    
    # Table styling
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]
    
    # Alternating row colors
    for i in range(1, len(issue_data)):
        bg_color = colors.HexColor('#f3f4f6') if i % 2 == 1 else colors.white
        table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
    
    table.setStyle(TableStyle(table_style))
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer