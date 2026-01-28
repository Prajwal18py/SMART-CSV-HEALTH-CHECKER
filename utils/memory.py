"""
Memory optimization utilities for Smart CSV Health Checker
"""
import pandas as pd
import numpy as np
from typing import Tuple

from utils.logger import get_logger

logger = get_logger()


def optimize_dtypes(df: pd.DataFrame, verbose: bool = False) -> Tuple[pd.DataFrame, dict]:
    """
    Optimize DataFrame dtypes to reduce memory usage
    
    Args:
        df: DataFrame to optimize
        verbose: Whether to log optimization details
    
    Returns:
        Tuple of (optimized DataFrame, optimization report)
    """
    df_optimized = df.copy()
    report = {
        'original_memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'optimized_memory_mb': 0,
        'savings_percent': 0,
        'changes': []
    }
    
    for col in df_optimized.columns:
        col_type = df_optimized[col].dtype
        
        try:
            # Optimize integers
            if col_type in ['int64', 'int32']:
                col_min = df_optimized[col].min()
                col_max = df_optimized[col].max()
                
                if col_min >= 0:
                    if col_max <= 255:
                        df_optimized[col] = df_optimized[col].astype('uint8')
                        report['changes'].append(f"{col}: int64 -> uint8")
                    elif col_max <= 65535:
                        df_optimized[col] = df_optimized[col].astype('uint16')
                        report['changes'].append(f"{col}: int64 -> uint16")
                    elif col_max <= 4294967295:
                        df_optimized[col] = df_optimized[col].astype('uint32')
                        report['changes'].append(f"{col}: int64 -> uint32")
                else:
                    if col_min >= -128 and col_max <= 127:
                        df_optimized[col] = df_optimized[col].astype('int8')
                        report['changes'].append(f"{col}: int64 -> int8")
                    elif col_min >= -32768 and col_max <= 32767:
                        df_optimized[col] = df_optimized[col].astype('int16')
                        report['changes'].append(f"{col}: int64 -> int16")
                    elif col_min >= -2147483648 and col_max <= 2147483647:
                        df_optimized[col] = df_optimized[col].astype('int32')
                        report['changes'].append(f"{col}: int64 -> int32")
            
            # Optimize floats
            elif col_type == 'float64':
                col_data = df_optimized[col].dropna()
                if len(col_data) > 0 and (col_data == col_data.astype(int)).all():
                    df_optimized[col] = df_optimized[col].astype('Int64')
                    report['changes'].append(f"{col}: float64 -> Int64 (nullable)")
                else:
                    df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
                    if df_optimized[col].dtype != col_type:
                        report['changes'].append(f"{col}: float64 -> {df_optimized[col].dtype}")
            
            # Optimize objects to category if low cardinality
            elif col_type == 'object':
                num_unique = df_optimized[col].nunique()
                num_total = len(df_optimized[col])
                
                if num_total > 0 and num_unique / num_total < 0.5:
                    df_optimized[col] = df_optimized[col].astype('category')
                    report['changes'].append(f"{col}: object -> category ({num_unique} unique)")
        
        except Exception:
            continue
    
    report['optimized_memory_mb'] = df_optimized.memory_usage(deep=True).sum() / 1024**2
    
    if report['original_memory_mb'] > 0:
        report['savings_percent'] = (
            (report['original_memory_mb'] - report['optimized_memory_mb']) / 
            report['original_memory_mb'] * 100
        )
    
    if verbose:
        logger.info(
            f"Memory optimization: {report['original_memory_mb']:.2f} MB -> "
            f"{report['optimized_memory_mb']:.2f} MB ({report['savings_percent']:.1f}% savings)"
        )
    
    return df_optimized, report


def get_memory_usage(df: pd.DataFrame) -> dict:
    """
    Get detailed memory usage of a DataFrame
    """
    memory_usage = df.memory_usage(deep=True)
    
    return {
        'total_mb': memory_usage.sum() / 1024**2,
        'per_column': {
            col: memory_usage[col] / 1024**2 
            for col in df.columns
        },
        'index_mb': memory_usage['Index'] / 1024**2 if 'Index' in memory_usage else 0
    }


def sample_large_dataset(df: pd.DataFrame, threshold: int = 100000, 
                          fraction: float = 0.1, random_state: int = 42) -> Tuple[pd.DataFrame, bool]:
    """
    Sample a large dataset if it exceeds threshold
    """
    if len(df) > threshold:
        sampled_df = df.sample(frac=fraction, random_state=random_state)
        logger.info(f"Sampled dataset: {len(df):,} -> {len(sampled_df):,} rows ({fraction*100:.0f}%)")
        return sampled_df, True
    
    return df, False

def prepare_df_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for Streamlit display by fixing type issues
    """
    df_display = df.copy()
    
    for col in df_display.columns:
        # Convert datetime columns to string for display
        if pd.api.types.is_datetime64_any_dtype(df_display[col]):
            df_display[col] = df_display[col].astype(str)
        # Handle mixed object types
        elif df_display[col].dtype == 'object':
            try:
                # Try to convert to datetime if it looks like dates
                df_display[col] = pd.to_datetime(df_display[col]).astype(str)
            except:
                df_display[col] = df_display[col].astype(str)
    
    return df_display