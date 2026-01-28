"""
Caching utilities for Smart CSV Health Checker
"""
import streamlit as st
import pandas as pd
import hashlib
from typing import Any, Optional, Callable
from functools import wraps

from config.constants import CACHE_TTL, ENABLE_CACHING


def compute_dataframe_hash(df: pd.DataFrame) -> str:
    """
    Compute a hash of a DataFrame for cache key purposes
    
    Args:
        df: DataFrame to hash
    
    Returns:
        String hash of the DataFrame
    """
    # Use shape + column names + sample of data for hash
    hash_components = [
        str(df.shape),
        str(list(df.columns)),
        str(df.dtypes.tolist()),
    ]
    
    # Add sample data hash for small datasets
    if len(df) <= 1000:
        hash_components.append(str(df.values.tobytes()))
    else:
        # For large datasets, sample
        sample = df.sample(n=min(1000, len(df)), random_state=42)
        hash_components.append(str(sample.values.tobytes()))
    
    combined = '|'.join(hash_components)
    return hashlib.md5(combined.encode()).hexdigest()


def get_cached_analysis(df_hash: str) -> Optional[dict]:
    """
    Retrieve cached analysis results
    
    Args:
        df_hash: Hash of the DataFrame
    
    Returns:
        Cached results or None
    """
    if not ENABLE_CACHING:
        return None
    
    cache_key = f"analysis_{df_hash}"
    
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    return None


def set_cached_analysis(df_hash: str, results: dict):
    """
    Cache analysis results
    
    Args:
        df_hash: Hash of the DataFrame
        results: Analysis results to cache
    """
    if not ENABLE_CACHING:
        return
    
    cache_key = f"analysis_{df_hash}"
    st.session_state[cache_key] = results


def cached_analysis(func: Callable) -> Callable:
    """
    Decorator for caching analysis functions
    
    Usage:
        @cached_analysis
        def analyze_csv_with_ai(df, types, contamination, imputation_method):
            ...
    """
    @wraps(func)
    def wrapper(df: pd.DataFrame, *args, **kwargs):
        if not ENABLE_CACHING:
            return func(df, *args, **kwargs)
        
        # Compute hash
        df_hash = compute_dataframe_hash(df)
        
        # Create cache key with all parameters
        param_hash = hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()[:8]
        full_hash = f"{df_hash}_{param_hash}"
        
        # Check cache
        cached = get_cached_analysis(full_hash)
        if cached is not None:
            return cached
        
        # Compute and cache
        result = func(df, *args, **kwargs)
        set_cached_analysis(full_hash, result)
        
        return result
    
    return wrapper


def clear_analysis_cache():
    """Clear all cached analysis results"""
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith('analysis_')]
    for key in keys_to_delete:
        del st.session_state[key]


def clear_session_state_for_new_file(uploaded_file):
    """
    Clear session state when a new file is uploaded
    
    Args:
        uploaded_file: The newly uploaded file
    """
    if uploaded_file is None:
        return
    
    current_file = uploaded_file.name
    previous_file = st.session_state.get('previous_file')
    
    if previous_file != current_file:
        # Clear previous analysis state
        keys_to_clear = [
            'wizard_step',
            'wizard_actions', 
            'pipeline_steps',
            'cleaning_ops',
            'validation_rules',
            'pca_computed',
            'synthetic_generated'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Clear analysis cache
        clear_analysis_cache()
        
        # Update previous file tracker
        st.session_state.previous_file = current_file