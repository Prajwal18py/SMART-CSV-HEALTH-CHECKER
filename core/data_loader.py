"""
Data Loading and Validation
Handle CSV file upload, validation, and test dataset generation
"""
import streamlit as st
import pandas as pd
import numpy as np

from config.constants import MAX_FILE_SIZE_MB, LARGE_DATASET_THRESHOLD, SAMPLE_FRACTION
from utils.logger import get_logger
from utils.memory import sample_large_dataset

logger = get_logger()


def handle_file_upload(uploaded_file, enable_sampling=True):
    """
    Validate and load CSV file with optional sampling
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        enable_sampling: Whether to offer sampling for large files
    
    Returns:
        DataFrame or None if validation fails
    """
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    logger.log_file_upload(uploaded_file.name, file_size_mb)
    
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File too large ({file_size_mb:.1f} MB). Maximum: {MAX_FILE_SIZE_MB} MB")
        return None
    elif file_size_mb > 50:
        st.warning(
            f"⚠️ Large file detected ({file_size_mb:.1f} MB). "
            f"Analysis may take 30-60 seconds."
        )
    
    # Load CSV
    try:
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.warning(f"⚠️ Large file ({file_size_mb:.1f} MB). Analyzing first 10k rows.")
            df = pd.read_csv(uploaded_file, nrows=10000)
        else:
            df = pd.read_csv(uploaded_file)
        
        # Validation
        if df.empty:
            st.error("❌ The uploaded file is empty!")
            return None
        
        if len(df.columns) == 0:
            st.error("❌ No columns found in the file!")
            return None
        
        # Sampling for very large datasets
        if enable_sampling and len(df) > LARGE_DATASET_THRESHOLD:
            use_sample = st.checkbox(
                f"📊 Dataset has {len(df):,} rows. Use {SAMPLE_FRACTION*100:.0f}% sample for faster analysis?",
                value=True,
                key="use_sampling"
            )
            if use_sample:
                df, was_sampled = sample_large_dataset(df, LARGE_DATASET_THRESHOLD, SAMPLE_FRACTION)
                if was_sampled:
                    st.info(f"📉 Using sample of {len(df):,} rows for analysis")
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error reading CSV: {str(e)}")
        logger.log_error_with_context(e, "CSV file reading")
        return None


def generate_test_dataset():
    """
    Generate a comprehensive test dataset with various anomalies for testing.
    This creates realistic data with intentional issues for the health checker to detect.
    
    Returns:
        DataFrame with anomalies, missing values, duplicates, and PII-like data
    """
    np.random.seed(42)
    n_rows = 300
    
    # =================================================================
    # 1. BASE NORMAL DATA
    # =================================================================
    
    # Generate realistic employee data
    ages = np.random.normal(35, 8, n_rows).clip(22, 65).astype(int)
    salaries = np.random.lognormal(10.8, 0.4, n_rows).astype(int)
    experience = np.random.gamma(5, 2, n_rows).clip(0, 40).astype(int)
    employee_ids = list(range(1000, 1000 + n_rows))
    departments = np.random.choice(['Engineering', 'Sales', 'HR', 'Marketing', 'Finance'], n_rows)
    join_dates = pd.date_range('2018-01-01', periods=n_rows, freq='2D')
    
    # Create base DataFrame
    df = pd.DataFrame({
        'Employee_ID': employee_ids,
        'Age': ages.astype(float),
        'Salary': salaries.astype(float),
        'Experience_Years': experience.astype(float),
        'Department': departments,
        'Join_Date': join_dates,
        'Email': [f"employee{i}@company.com" for i in range(n_rows)],
        'Phone': [f"555-{np.random.randint(100,999)}-{np.random.randint(1000,9999)}" for _ in range(n_rows)],
        'Performance_Score': np.random.normal(75, 15, n_rows).clip(0, 100).round(1)
    })
    
    # =================================================================
    # 2. INJECT MISSING VALUES (10-15% in key columns)
    # =================================================================
    
    missing_age_idx = np.random.choice(n_rows, size=int(n_rows * 0.10), replace=False)
    df.loc[missing_age_idx, 'Age'] = np.nan
    
    missing_salary_idx = np.random.choice(n_rows, size=int(n_rows * 0.05), replace=False)
    df.loc[missing_salary_idx, 'Salary'] = np.nan
    
    missing_exp_idx = np.random.choice(n_rows, size=int(n_rows * 0.08), replace=False)
    df.loc[missing_exp_idx, 'Experience_Years'] = np.nan
    
    # =================================================================
    # 3. INJECT STATISTICAL OUTLIERS (Extreme values)
    # =================================================================
    
    outlier_rows = []
    
    # Extreme high salary (billionaire)
    outlier_rows.append({
        'Employee_ID': 9999, 'Age': 45.0, 'Salary': 10000000.0,
        'Experience_Years': 10.0, 'Department': 'Finance',
        'Join_Date': pd.Timestamp('2021-01-01'), 'Email': 'ceo@company.com',
        'Phone': '555-000-0001', 'Performance_Score': 95.0
    })
    
    # Negative age (impossible)
    outlier_rows.append({
        'Employee_ID': 9998, 'Age': -10.0, 'Salary': 50000.0,
        'Experience_Years': 2.0, 'Department': 'Marketing',
        'Join_Date': pd.Timestamp('2022-03-10'), 'Email': 'ghost@company.com',
        'Phone': '555-000-0002', 'Performance_Score': 70.0
    })
    
    # Extreme experience (80 years - impossible)
    outlier_rows.append({
        'Employee_ID': 9997, 'Age': 60.0, 'Salary': 90000.0,
        'Experience_Years': 80.0, 'Department': 'Engineering',
        'Join_Date': pd.Timestamp('2023-01-01'), 'Email': 'veteran@company.com',
        'Phone': '555-000-0003', 'Performance_Score': 85.0
    })
    
    # Extremely low salary
    outlier_rows.append({
        'Employee_ID': 9996, 'Age': 30.0, 'Salary': 100.0,
        'Experience_Years': 5.0, 'Department': 'HR',
        'Join_Date': pd.Timestamp('2020-06-15'), 'Email': 'intern@company.com',
        'Phone': '555-000-0004', 'Performance_Score': 60.0
    })
    
    # =================================================================
    # 4. INJECT LOGICAL ANOMALIES (AI should detect these)
    # =================================================================
    
    # Baby Senior: Age 20 with 15 years experience (impossible)
    outlier_rows.append({
        'Employee_ID': 9001, 'Age': 20.0, 'Salary': 80000.0,
        'Experience_Years': 15.0, 'Department': 'Engineering',
        'Join_Date': pd.Timestamp('2020-01-01'), 'Email': 'prodigy@company.com',
        'Phone': '555-111-1111', 'Performance_Score': 90.0
    })
    
    # Underpaid Executive: 30 years exp but $500 salary
    outlier_rows.append({
        'Employee_ID': 9002, 'Age': 55.0, 'Salary': 500.0,
        'Experience_Years': 30.0, 'Department': 'Sales',
        'Join_Date': pd.Timestamp('2019-06-15'), 'Email': 'veteran_exec@company.com',
        'Phone': '555-222-2222', 'Performance_Score': 88.0
    })
    
    # Future joiner (join date in 2050)
    outlier_rows.append({
        'Employee_ID': 9003, 'Age': 30.0, 'Salary': 70000.0,
        'Experience_Years': 5.0, 'Department': 'HR',
        'Join_Date': pd.Timestamp('2050-01-01'), 'Email': 'future@company.com',
        'Phone': '555-333-3333', 'Performance_Score': 75.0
    })
    
    # High performer with 0 experience and high salary
    outlier_rows.append({
        'Employee_ID': 9004, 'Age': 22.0, 'Salary': 150000.0,
        'Experience_Years': 0.0, 'Department': 'Engineering',
        'Join_Date': pd.Timestamp('2024-01-01'), 'Email': 'nepotism@company.com',
        'Phone': '555-444-4444', 'Performance_Score': 99.0
    })
    
    # =================================================================
    # 5. INJECT CATEGORICAL ANOMALIES (Typos, inconsistencies)
    # =================================================================
    
    outlier_rows.append({
        'Employee_ID': 9101, 'Age': 28.0, 'Salary': 60000.0,
        'Experience_Years': 4.0, 'Department': 'Enginering',  # Typo
        'Join_Date': pd.Timestamp('2021-05-01'), 'Email': 'typo1@company.com',
        'Phone': '555-555-5551', 'Performance_Score': 72.0
    })
    
    outlier_rows.append({
        'Employee_ID': 9102, 'Age': 32.0, 'Salary': 65000.0,
        'Experience_Years': 6.0, 'Department': 'SALES',  # Caps
        'Join_Date': pd.Timestamp('2021-06-01'), 'Email': 'caps@company.com',
        'Phone': '555-555-5552', 'Performance_Score': 78.0
    })
    
    outlier_rows.append({
        'Employee_ID': 9103, 'Age': 29.0, 'Salary': 62000.0,
        'Experience_Years': 5.0, 'Department': 'HR ',  # Trailing space
        'Join_Date': pd.Timestamp('2021-07-01'), 'Email': 'space@company.com',
        'Phone': '555-555-5553', 'Performance_Score': 70.0
    })
    
    # =================================================================
    # 6. ADD PII-LIKE DATA FOR DETECTION
    # =================================================================
    
    outlier_rows.append({
        'Employee_ID': 9200, 'Age': 40.0, 'Salary': 75000.0,
        'Experience_Years': 12.0, 'Department': 'Finance',
        'Join_Date': pd.Timestamp('2020-01-15'), 'Email': 'ssn_test@company.com',
        'Phone': '123-45-6789',  # SSN format
        'Performance_Score': 80.0
    })
    
    # =================================================================
    # 7. COMBINE ALL DATA
    # =================================================================
    
    outliers_df = pd.DataFrame(outlier_rows)
    df = pd.concat([df, outliers_df], ignore_index=True)
    
    # =================================================================
    # 8. INJECT DUPLICATE ROWS
    # =================================================================
    
    duplicates = df.iloc[:5].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # =================================================================
    # 9. SHUFFLE THE DATA
    # =================================================================
    
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # =================================================================
    # 10. ADD HIGHLY CORRELATED COLUMNS
    # =================================================================
    
    df['Annual_Bonus'] = df['Salary'] * 0.15 + np.random.normal(0, 500, len(df))
    df['Annual_Bonus'] = df['Annual_Bonus'].clip(0, None)
    
    df['Years_to_Retirement'] = (65 - df['Age']).clip(0, 43) + np.random.normal(0, 1, len(df))
    
    logger.info(f"Generated test dataset: {len(df)} rows, {len(df.columns)} columns")
    df['Join_Date'] = pd.to_datetime(df['Join_Date'])
    return df