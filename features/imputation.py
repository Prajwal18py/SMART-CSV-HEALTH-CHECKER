"""
AI Smart Imputation using MICE
Use Multiple Imputation by Chained Equations for missing value prediction
"""
import pandas as pd
import numpy as np

# Enable experimental IterativeImputer (MICE)
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer

from utils.logger import get_logger

logger = get_logger()


def mice_imputation(df, max_iter=10, random_state=42, verbose=False):
    """
    Perform MICE (Multiple Imputation by Chained Equations) imputation
    """
    df_imputed = df.copy()
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    original_dtypes = df.dtypes.to_dict()
    cols_with_missing = [c for c in df.columns if df[c].isna().any()]
    
    if verbose:
        logger.info(f"MICE Imputation: {len(cols_with_missing)} columns with missing values")
    
    if numeric_cols:
        numeric_missing = [c for c in numeric_cols if c in cols_with_missing]
        
        if numeric_missing:
            numeric_data = df[numeric_cols].copy()
            
            try:
                mice_imputer = IterativeImputer(
                    max_iter=max_iter,
                    random_state=random_state,
                    initial_strategy='mean',
                    imputation_order='ascending',
                    verbose=0
                )
                
                imputed_numeric = mice_imputer.fit_transform(numeric_data)
                df_imputed[numeric_cols] = imputed_numeric
                
                if verbose:
                    logger.info(f"MICE completed for {len(numeric_missing)} numeric columns")
                    
            except Exception as e:
                logger.log_error_with_context(e, "MICE imputation for numeric columns")
                for col in numeric_missing:
                    df_imputed[col].fillna(df_imputed[col].mean(), inplace=True)
    
    for col in categorical_cols:
        if df_imputed[col].isna().any():
            mode_val = df_imputed[col].mode()
            if not mode_val.empty:
                df_imputed[col].fillna(mode_val[0], inplace=True)
    
    for col, dtype in original_dtypes.items():
        try:
            if col in numeric_cols:
                if dtype in ['int64', 'int32', 'int16', 'int8']:
                    df_imputed[col] = df_imputed[col].round().astype(dtype)
                elif dtype == 'Int64':
                    df_imputed[col] = df_imputed[col].round().astype('Int64')
        except Exception:
            pass
    
    return df_imputed


def ai_smart_imputation(df, col):
    """
    Use MICE to predict missing values for a specific column
    """
    try:
        if df[col].isna().sum() == 0:
            return df
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if pd.api.types.is_numeric_dtype(df[col]):
            if col in numeric_cols and len(numeric_cols) > 1:
                df_numeric = df[numeric_cols].copy()
                
                mice_imputer = IterativeImputer(
                    max_iter=10,
                    random_state=42,
                    initial_strategy='mean'
                )
                
                imputed_data = mice_imputer.fit_transform(df_numeric)
                
                col_idx = numeric_cols.index(col)
                df[col] = imputed_data[:, col_idx]
                
                try:
                    original_non_null = df[col].dropna()
                    if len(original_non_null) > 0:
                        if (original_non_null == original_non_null.astype(int)).all():
                            df[col] = df[col].round().astype('Int64')
                except Exception:
                    pass
            else:
                df[col].fillna(df[col].mean(), inplace=True)
        else:
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col].fillna(mode_val[0], inplace=True)
    
    except Exception as e:
        logger.log_error_with_context(e, f"MICE imputation for column {col}")
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col].fillna(mode_val[0], inplace=True)
    
    return df


def advanced_mice_imputation(df, n_imputations=5, max_iter=10, random_state=42):
    """
    Perform multiple MICE imputations and return pooled results
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols or not df[numeric_cols].isna().any().any():
        return df.copy(), {}
    
    imputed_datasets = []
    
    for i in range(n_imputations):
        df_copy = df.copy()
        
        try:
            mice_imputer = IterativeImputer(
                max_iter=max_iter,
                random_state=random_state + i,
                sample_posterior=True
            )
            
            imputed_numeric = mice_imputer.fit_transform(df_copy[numeric_cols])
            df_copy[numeric_cols] = imputed_numeric
            imputed_datasets.append(df_copy)
        except Exception as e:
            logger.log_error_with_context(e, f"MICE imputation iteration {i+1}")
            continue
    
    if not imputed_datasets:
        logger.warning("All MICE iterations failed, returning original with mean imputation")
        df_fallback = df.copy()
        for col in numeric_cols:
            df_fallback[col].fillna(df_fallback[col].mean(), inplace=True)
        return df_fallback, {}
    
    df_pooled = df.copy()
    uncertainty = {}
    
    for col in numeric_cols:
        all_values = np.array([d[col].values for d in imputed_datasets])
        
        pooled_values = np.mean(all_values, axis=0)
        df_pooled[col] = pooled_values
        
        within_var = np.mean(np.var(all_values, axis=0))
        between_var = np.var(np.mean(all_values, axis=1))
        total_var = within_var + (1 + 1/n_imputations) * between_var
        
        uncertainty[col] = {
            'within_variance': within_var,
            'between_variance': between_var,
            'total_variance': total_var,
            'std_error': np.sqrt(total_var)
        }
    
    for col in df.columns:
        if col not in numeric_cols and df[col].isna().any():
            mode_val = df[col].mode()
            if not mode_val.empty:
                df_pooled[col].fillna(mode_val[0], inplace=True)
    
    return df_pooled, uncertainty