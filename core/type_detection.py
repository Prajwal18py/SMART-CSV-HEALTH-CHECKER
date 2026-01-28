"""
Column Type Detection
Automatically identify Date, ID, Numeric, and Categorical columns
"""
import pandas as pd
import re


def detect_column_types(df):
    """
    Identify and categorize columns by their data type
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        Tuple of (types_dict, modified_df)
        - types_dict: Dictionary with keys 'numeric', 'categorical', 'datetime', 'ids'
        - modified_df: DataFrame with datetime columns converted
    """
    types = {
        'numeric': [],
        'categorical': [],
        'datetime': [],
        'ids': []
    }
    
    for col in df.columns:
        # Check if already datetime type
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            types['datetime'].append(col)
            continue
        
        # Try parsing dates from strings
        try:
            if df[col].dtype == 'object':
                non_null = df[col].dropna()
                
                if len(non_null) > 0:
                    samples = non_null.head(min(10, len(non_null)))
                    
                    # Count how many samples match date patterns
                    date_pattern_count = sum(
                        1 for s in samples
                        if isinstance(s, str) and (
                            re.match(r'\d{4}-\d{2}-\d{2}', s) or  # YYYY-MM-DD
                            re.match(r'\d{2}/\d{2}/\d{4}', s)     # MM/DD/YYYY
                        )
                    )
                    
                    # If 80%+ match date patterns, convert to datetime
                    if date_pattern_count >= len(samples) * 0.8:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        types['datetime'].append(col)
                        continue
        except Exception:
            pass
        
        # Detect IDs and numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            n_unique = df[col].nunique()
            n_rows = len(df)
            
            # If >90% unique values and >50 rows, likely an ID column
            if n_rows > 50 and n_unique > 0.9 * n_rows:
                types['ids'].append(col)
            else:
                types['numeric'].append(col)
        else:
            # Everything else is categorical
            types['categorical'].append(col)
    
    return types, df