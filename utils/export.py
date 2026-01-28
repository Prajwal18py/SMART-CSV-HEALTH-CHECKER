"""
Export utilities for multiple file formats
"""
import pandas as pd
import io
from typing import Optional
import json

from utils.logger import get_logger

logger = get_logger()


def export_to_excel(df: pd.DataFrame, sheet_name: str = 'Data') -> bytes:
    """
    Export DataFrame to Excel format
    
    Args:
        df: DataFrame to export
        sheet_name: Name of the Excel sheet
    
    Returns:
        Bytes of Excel file
    """
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    buffer.seek(0)
    return buffer.getvalue()


def export_to_parquet(df: pd.DataFrame) -> bytes:
    """
    Export DataFrame to Parquet format
    
    Args:
        df: DataFrame to export
    
    Returns:
        Bytes of Parquet file
    """
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine='pyarrow')
    buffer.seek(0)
    return buffer.getvalue()


def export_to_json(df: pd.DataFrame, orient: str = 'records') -> str:
    """
    Export DataFrame to JSON format
    
    Args:
        df: DataFrame to export
        orient: JSON orientation ('records', 'columns', 'index', 'split', 'table')
    
    Returns:
        JSON string
    """
    return df.to_json(orient=orient, date_format='iso', indent=2)


def export_to_sql_inserts(df: pd.DataFrame, table_name: str = 'data_table') -> str:
    """
    Generate SQL INSERT statements from DataFrame
    
    Args:
        df: DataFrame to export
        table_name: Name of the SQL table
    
    Returns:
        String with SQL INSERT statements
    """
    sql_statements = []
    
    # Generate CREATE TABLE statement
    column_defs = []
    for col in df.columns:
        dtype = df[col].dtype
        
        if pd.api.types.is_integer_dtype(dtype):
            sql_type = 'INTEGER'
        elif pd.api.types.is_float_dtype(dtype):
            sql_type = 'REAL'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            sql_type = 'TIMESTAMP'
        elif pd.api.types.is_bool_dtype(dtype):
            sql_type = 'BOOLEAN'
        else:
            sql_type = 'TEXT'
        
        # Clean column name for SQL
        clean_col = col.replace(' ', '_').replace('-', '_')
        column_defs.append(f'    {clean_col} {sql_type}')
    
    create_stmt = f"CREATE TABLE {table_name} (\n" + ',\n'.join(column_defs) + "\n);"
    sql_statements.append(create_stmt)
    sql_statements.append('')
    
    # Generate INSERT statements
    for idx, row in df.iterrows():
        values = []
        for val in row.values:
            if pd.isna(val):
                values.append('NULL')
            elif isinstance(val, str):
                # Escape single quotes
                escaped = val.replace("'", "''")
                values.append(f"'{escaped}'")
            elif isinstance(val, (int, float)):
                values.append(str(val))
            elif isinstance(val, pd.Timestamp):
                values.append(f"'{val.isoformat()}'")
            else:
                values.append(f"'{str(val)}'")
        
        columns = ', '.join([c.replace(' ', '_').replace('-', '_') for c in df.columns])
        values_str = ', '.join(values)
        insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});"
        sql_statements.append(insert_stmt)
    
    return '\n'.join(sql_statements)


def generate_validation_rules(df: pd.DataFrame) -> str:
    """
    Generate data validation rules based on DataFrame analysis
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        String with validation rules
    """
    rules = []
    rules.append("# Data Validation Rules")
    rules.append("# Generated from dataset analysis\n")
    
    for col in df.columns:
        col_rules = [f"## {col}"]
        dtype = df[col].dtype
        
        # Data type
        if pd.api.types.is_integer_dtype(dtype):
            col_rules.append(f"- Type: INTEGER")
        elif pd.api.types.is_float_dtype(dtype):
            col_rules.append(f"- Type: FLOAT")
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_rules.append(f"- Type: DATETIME")
        else:
            col_rules.append(f"- Type: STRING")
        
        # Nullable
        has_nulls = df[col].isna().any()
        col_rules.append(f"- Nullable: {has_nulls}")
        
        # Numeric constraints
        if pd.api.types.is_numeric_dtype(dtype):
            min_val = df[col].min()
            max_val = df[col].max()
            col_rules.append(f"- Range: [{min_val}, {max_val}]")
        
        # Categorical/Enum
        elif df[col].dtype == 'object':
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) <= 20:
                vals_str = ', '.join([f"'{v}'" for v in unique_vals[:10]])
                if len(unique_vals) > 10:
                    vals_str += f", ... ({len(unique_vals)} total)"
                col_rules.append(f"- Allowed Values: [{vals_str}]")
            else:
                col_rules.append(f"- Unique Values: {len(unique_vals)}")
        
        # Uniqueness
        is_unique = df[col].nunique() == len(df[col].dropna())
        if is_unique:
            col_rules.append(f"- Constraint: UNIQUE")
        
        rules.extend(col_rules)
        rules.append("")
    
    return '\n'.join(rules)


def export_html_report(df: pd.DataFrame, results: dict, 
                       title: str = "Data Quality Report") -> str:
    """
    Generate comprehensive HTML report
    
    Args:
        df: DataFrame analyzed
        results: Analysis results
        title: Report title
    
    Returns:
        HTML string
    """
    from features.statistics import get_health_grade
    
    score = results['health_score']
    grade = get_health_grade(score)
    
    # Determine color
    if score >= 80:
        color = '#10b981'
    elif score >= 60:
        color = '#f59e0b'
    else:
        color = '#ef4444'
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        body {{ background: #0f172a; color: #e2e8f0; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 2rem; }}
        .score {{ font-size: 4rem; font-weight: bold; color: {color}; }}
        .grade {{ font-size: 2rem; color: {color}; }}
        .section {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; }}
        .section h2 {{ color: #a5b4fc; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; }}
        .issue-high {{ color: #ef4444; }}
        .issue-medium {{ color: #f59e0b; }}
        .issue-low {{ color: #22c55e; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
        .metric-card {{ background: #334155; padding: 1rem; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 1.5rem; font-weight: bold; color: #6366f1; }}
        .metric-label {{ color: #94a3b8; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 {title}</h1>
            <div class="score">{score}/100</div>
            <div class="grade">Grade: {grade}</div>
        </div>
        
        <div class="section">
            <h2>📊 Dataset Overview</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-value">{len(df):,}</div>
                    <div class="metric-label">Rows</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(df.columns)}</div>
                    <div class="metric-label">Columns</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{df.isna().sum().sum():,}</div>
                    <div class="metric-label">Missing Values</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{df.duplicated().sum()}</div>
                    <div class="metric-label">Duplicates</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🚨 Issues Detected ({len(results['issues'])})</h2>
            <table>
                <tr><th>Type</th><th>Severity</th><th>Description</th></tr>
    """
    
    for issue in results['issues']:
        severity_class = f"issue-{issue['severity'].lower()}"
        html += f"""
                <tr>
                    <td>{issue['type']}</td>
                    <td class="{severity_class}">{issue['severity']}</td>
                    <td>{issue['message']}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            <ul>
    """
    
    for rec in results['recommendations']:
        html += f"<li>{rec}</li>\n"
    
    html += """
            </ul>
        </div>
        
        <div class="section">
            <h2>📋 Column Summary</h2>
            <table>
                <tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th></tr>
    """
    
    for col in df.columns:
        missing_pct = df[col].isna().mean() * 100
        unique_count = df[col].nunique()
        html += f"""
                <tr>
                    <td>{col}</td>
                    <td>{df[col].dtype}</td>
                    <td>{missing_pct:.1f}%</td>
                    <td>{unique_count:,}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <footer style="text-align: center; margin-top: 2rem; color: #64748b;">
            Generated by Smart CSV Health Checker AI
        </footer>
    </div>
</body>
</html>
    """
    
    return html