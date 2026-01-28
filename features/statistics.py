"""
Statistical Helper Functions
Health grading, anomaly severity, and analysis helpers
"""


def get_health_grade(score):
    """Convert health score to letter grade"""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def get_anomaly_severity(score):
    """Color code anomaly severity based on score"""
    if score < -0.5:
        return "🔴 Severe"
    elif score < -0.3:
        return "🟡 Medium"
    else:
        return "🟢 Low"


def explain_anomaly(row, df, feature_importance):
    """
    Explain why a specific row is anomalous
    
    Args:
        row: The anomalous row (pandas Series)
        df: The full DataFrame
        feature_importance: DataFrame with Feature and Importance columns
    
    Returns:
        List of explanation dictionaries
    """
    explanations = []
    if feature_importance is None:
        return []
    
    for idx, feat in feature_importance.iterrows():
        col = feat['Feature']
        row_val = row[col]
        
        # Compare to typical values
        mean = df[col].mean()
        std = df[col].std()
        
        if std == 0:
            continue
        
        z_score = abs((row_val - mean) / std)
        
        if z_score > 2:  # More than 2 std devs away
            explanations.append({
                'column': col,
                'value': row_val,
                'typical_range': f"{mean - 2*std:.1f} to {mean + 2*std:.1f}",
                'severity': 'High' if z_score > 3 else 'Medium',
                'z_score': z_score,
                'deviation': z_score
            })
    
    return explanations