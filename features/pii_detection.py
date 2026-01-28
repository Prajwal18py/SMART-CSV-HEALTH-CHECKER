"""
PII (Personally Identifiable Information) Detection
Detect and flag sensitive data columns
"""
import pandas as pd
import numpy as np
import re
import hashlib
from typing import Dict, List


# PII Patterns
PII_PATTERNS = {
    'email': {
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'description': 'Email Address',
        'risk': 'High',
        'recommendation': 'Hash or remove email addresses'
    },
    'phone_us': {
        'pattern': r'^(\+1)?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$',
        'description': 'US Phone Number',
        'risk': 'High',
        'recommendation': 'Mask or remove phone numbers'
    },
    'ssn': {
        'pattern': r'^\d{3}-?\d{2}-?\d{4}$',
        'description': 'Social Security Number',
        'risk': 'Critical',
        'recommendation': 'Remove SSN immediately - highly sensitive'
    },
    'credit_card': {
        'pattern': r'^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})$',
        'description': 'Credit Card Number',
        'risk': 'Critical',
        'recommendation': 'Remove credit card numbers immediately'
    },
    'ip_address': {
        'pattern': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        'description': 'IP Address',
        'risk': 'Medium',
        'recommendation': 'Consider anonymizing IP addresses'
    },
    'zip_code': {
        'pattern': r'^\d{5}(-\d{4})?$',
        'description': 'US ZIP Code',
        'risk': 'Low',
        'recommendation': 'Consider using broader geographic regions'
    }
}

# Column name patterns that suggest PII
PII_COLUMN_PATTERNS = {
    'name': {
        'patterns': ['name', 'first_name', 'last_name', 'full_name', 'firstname', 'lastname', 'fname', 'lname'],
        'description': 'Person Name',
        'risk': 'High',
        'recommendation': 'Consider pseudonymization or removal'
    },
    'address': {
        'patterns': ['address', 'street', 'city', 'state', 'country', 'location', 'addr'],
        'description': 'Physical Address',
        'risk': 'Medium',
        'recommendation': 'Consider using broader geographic regions'
    },
    'email': {
        'patterns': ['email', 'e-mail', 'mail', 'email_address'],
        'description': 'Email Address',
        'risk': 'High',
        'recommendation': 'Hash or remove email addresses'
    },
    'phone': {
        'patterns': ['phone', 'mobile', 'cell', 'telephone', 'tel', 'contact'],
        'description': 'Phone Number',
        'risk': 'High',
        'recommendation': 'Mask or remove phone numbers'
    },
    'ssn': {
        'patterns': ['ssn', 'social_security', 'socialsecurity', 'ss_number'],
        'description': 'Social Security Number',
        'risk': 'Critical',
        'recommendation': 'Remove SSN immediately'
    },
    'dob': {
        'patterns': ['dob', 'birth', 'birthday', 'date_of_birth', 'birthdate'],
        'description': 'Date of Birth',
        'risk': 'Medium',
        'recommendation': 'Consider using age ranges'
    },
    'salary': {
        'patterns': ['salary', 'income', 'wage', 'compensation', 'pay'],
        'description': 'Financial Information',
        'risk': 'High',
        'recommendation': 'Consider using salary bands'
    }
}


def detect_pii(df: pd.DataFrame) -> Dict:
    """
    Detect PII in a DataFrame
    
    Args:
        df: DataFrame to scan for PII
    
    Returns:
        Dictionary with PII detection results
    """
    results = {
        'total_columns': len(df.columns),
        'pii_columns': [],
        'risk_summary': {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0},
        'overall_risk': 'Low',
        'recommendations': []
    }
    
    for col in df.columns:
        col_pii = detect_column_pii(df, col)
        
        if col_pii['is_pii']:
            results['pii_columns'].append(col_pii)
            results['risk_summary'][col_pii['risk']] += 1
    
    # Determine overall risk
    if results['risk_summary']['Critical'] > 0:
        results['overall_risk'] = 'Critical'
    elif results['risk_summary']['High'] > 0:
        results['overall_risk'] = 'High'
    elif results['risk_summary']['Medium'] > 0:
        results['overall_risk'] = 'Medium'
    elif results['risk_summary']['Low'] > 0:
        results['overall_risk'] = 'Low'
    else:
        results['overall_risk'] = 'None Detected'
    
    # Generate recommendations
    results['recommendations'] = generate_recommendations(results)
    
    return results


def detect_column_pii(df: pd.DataFrame, col: str) -> Dict:
    """Detect PII in a specific column"""
    
    result = {
        'column': col,
        'is_pii': False,
        'pii_type': None,
        'description': None,
        'risk': 'Low',
        'confidence': 0,
        'detection_method': None,
        'recommendation': None
    }
    
    # Check column name patterns
    col_lower = col.lower().replace(' ', '_').replace('-', '_')
    
    for pii_type, config in PII_COLUMN_PATTERNS.items():
        for pattern in config['patterns']:
            if pattern in col_lower:
                result['is_pii'] = True
                result['pii_type'] = pii_type
                result['description'] = config['description']
                result['risk'] = config['risk']
                result['confidence'] = 0.7
                result['detection_method'] = 'Column Name Pattern'
                result['recommendation'] = config['recommendation']
                break
        if result['is_pii']:
            break
    
    # Check data patterns (only for string columns)
    if df[col].dtype == 'object':
        data_pii = detect_data_patterns(df[col])
        
        if data_pii['is_pii']:
            if data_pii['confidence'] > result.get('confidence', 0):
                result.update(data_pii)
            elif result['is_pii']:
                result['confidence'] = min(0.95, result['confidence'] + 0.2)
                result['detection_method'] = 'Column Name + Data Pattern'
    
    return result


def detect_data_patterns(series: pd.Series) -> Dict:
    """Detect PII patterns in data values"""
    
    result = {
        'is_pii': False,
        'pii_type': None,
        'description': None,
        'risk': 'Low',
        'confidence': 0,
        'detection_method': 'Data Pattern',
        'recommendation': None
    }
    
    non_null = series.dropna().astype(str)
    
    if len(non_null) == 0:
        return result
    
    sample = non_null.head(1000)
    
    for pii_type, config in PII_PATTERNS.items():
        pattern = config['pattern']
        
        try:
            matches = sample.str.match(pattern, na=False)
            match_rate = matches.sum() / len(sample)
            
            if match_rate > 0.5:
                result['is_pii'] = True
                result['pii_type'] = pii_type
                result['description'] = config['description']
                result['risk'] = config['risk']
                result['confidence'] = min(0.95, match_rate)
                result['recommendation'] = config['recommendation']
                break
        except:
            continue
    
    return result


def generate_recommendations(results: Dict) -> List[str]:
    """Generate actionable recommendations"""
    
    recommendations = []
    
    if results['risk_summary']['Critical'] > 0:
        recommendations.append("🚨 CRITICAL: Found highly sensitive data (SSN, Credit Cards). Remove or encrypt immediately!")
    
    if results['risk_summary']['High'] > 0:
        recommendations.append("⚠️ HIGH RISK: Personal identifiers found. Consider pseudonymization or hashing.")
    
    if results['risk_summary']['Medium'] > 0:
        recommendations.append("📊 MEDIUM RISK: Quasi-identifiers found. Consider generalization.")
    
    if results['overall_risk'] == 'None Detected':
        recommendations.append("✅ No obvious PII detected. Always review data manually before sharing.")
    
    return recommendations


def mask_pii_column(df: pd.DataFrame, col: str, method: str = 'hash') -> pd.Series:
    """
    Mask PII in a column
    
    Args:
        df: DataFrame
        col: Column name
        method: 'hash', 'mask', 'redact', 'generalize'
    
    Returns:
        Masked Series
    """
    series = df[col].copy()
    
    if method == 'hash':
        def hash_value(x):
            if pd.isna(x):
                return x
            return hashlib.sha256(str(x).encode()).hexdigest()[:12]
        return series.apply(hash_value)
    
    elif method == 'mask':
        def mask_value(x):
            if pd.isna(x):
                return x
            s = str(x)
            if len(s) <= 4:
                return '*' * len(s)
            return s[:2] + '*' * (len(s) - 4) + s[-2:]
        return series.apply(mask_value)
    
    elif method == 'redact':
        return series.apply(lambda x: '[REDACTED]' if pd.notna(x) else x)
    
    elif method == 'generalize':
        if pd.api.types.is_numeric_dtype(series):
            try:
                bins = pd.qcut(series, q=5, duplicates='drop')
                return bins.astype(str)
            except:
                return series.apply(lambda x: '[GENERALIZED]' if pd.notna(x) else x)
        else:
            return series.apply(lambda x: '[GENERALIZED]' if pd.notna(x) else x)
    
    return series