"""
Main AI Analysis Engine
Performs comprehensive data quality analysis with AI anomaly detection
"""
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# Enable experimental IterativeImputer (MICE)
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer

from config.constants import (
    CORR_THRESHOLD, OUTLIER_IQR_MULTIPLIER, HIGH_SKEW_THRESHOLD,
    MEDIUM_SKEW_THRESHOLD, DEFAULT_AI_CONTAMINATION, MIN_ROWS_FOR_AI,
    MIN_NUMERIC_COLS_FOR_AI, HIGH_MISSING_THRESHOLD, MEDIUM_MISSING_THRESHOLD,
    LOW_MISSING_THRESHOLD, QUALITY_WEIGHTS, DISPLAY_ROW_LIMIT
)
from utils.logger import get_logger

logger = get_logger()


def deduct_health_score(results, amount):
    """Safely deduct from health score (never goes below 0)"""
    results['health_score'] = max(0, results['health_score'] - amount)
    return results['health_score']


def deduct_quality_dimension(results, dimension, amount):
    """Safely deduct from a quality dimension score"""
    if dimension in results['quality_dimensions']:
        results['quality_dimensions'][dimension] = max(
            0, results['quality_dimensions'][dimension] - amount
        )


def analyze_csv_with_ai(df, types, contamination=DEFAULT_AI_CONTAMINATION, imputation_method='drop'):
    """
    Advanced analysis with AI-powered anomaly detection
    
    Args:
        df: DataFrame to analyze
        types: Dictionary of column types from detect_column_types()
        contamination: Proportion of outliers in dataset (for AI)
        imputation_method: How to handle missing values ('drop', 'mean', 'mice')
    
    Returns:
        Dictionary containing health score, quality dimensions, issues, 
        recommendations, stats, visualizations, model
    """
    logger.log_analysis_start(len(df), len(df.columns))
    
    results = {
        'health_score': 100,
        'quality_dimensions': {
            'completeness': 100,
            'consistency': 100,
            'accuracy': 100,
            'validity': 100,
            'uniqueness': 100
        },
        'issues': [],
        'recommendations': [],
        'stats': {
            'missing_info': pd.DataFrame(),
            'skew_info': pd.DataFrame(),
            'outlier_info': pd.DataFrame(),
            'high_corr': pd.DataFrame(),
            'pca': None,
            'ai_anomalies': None,
            'feature_importance': None
        },
        'visualizations': {},
        'model': None
    }
    
    total_rows = len(df)
    
    if total_rows == 0:
        results['health_score'] = 0
        results['issues'].append({
            'type': 'Empty Dataset',
            'severity': 'High',
            'message': 'Dataset contains no rows'
        })
        return results
    
    # =====================================================================
    # 1. MISSING VALUES ANALYSIS (Completeness)
    # =====================================================================
    try:
        missing_info = []
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                pct = (missing_count / total_rows) * 100
                missing_info.append({
                    'Column': col, 
                    'Missing': missing_count,
                    'Percentage': pct
                })
                
                deduct_quality_dimension(results, 'completeness', min(10, pct/10))
                
                if pct > HIGH_MISSING_THRESHOLD * 100:
                    sev = 'High'
                    deduct_health_score(results, min(10, pct/10))
                elif pct > MEDIUM_MISSING_THRESHOLD * 100:
                    sev = 'Medium'
                    deduct_health_score(results, min(5, pct/20))
                else:
                    sev = 'Low'
                    deduct_health_score(results, min(2, pct/50))
                
                results['issues'].append({
                    'type': 'Missing Data',
                    'severity': sev,
                    'message': f"'{col}': {pct:.1f}% missing ({missing_count:,} values)"
                })
                
                if pct > HIGH_MISSING_THRESHOLD * 100:
                    results['recommendations'].append(f"❌ Consider dropping '{col}' (>{HIGH_MISSING_THRESHOLD*100:.0f}% missing)")
                elif pct > LOW_MISSING_THRESHOLD * 100:
                    results['recommendations'].append(f"🔧 Impute missing values in '{col}' using MICE")
        
        if missing_info:
            results['stats']['missing_info'] = pd.DataFrame(missing_info)
            
    except Exception as e:
        logger.log_error_with_context(e, "Missing values analysis")
    
    # =====================================================================
    # 2. DUPLICATES ANALYSIS (Uniqueness)
    # =====================================================================
    try:
        dups = df.duplicated().sum()
        if dups > 0:
            pct = (dups / total_rows) * 100
            
            deduct_quality_dimension(results, 'uniqueness', min(30, pct * 2))
            deduct_health_score(results, min(15, pct))
            
            results['issues'].append({
                'type': 'Duplicates',
                'severity': 'Medium' if pct < 10 else 'High',
                'message': f"{dups:,} duplicate rows ({pct:.1f}%)"
            })
            results['recommendations'].append(f"🗑️ Remove {dups:,} duplicate rows")
            
    except Exception as e:
        logger.log_error_with_context(e, "Duplicates analysis")
    
    # =====================================================================
    # 3. OUTLIERS ANALYSIS (Accuracy) - IQR Method
    # =====================================================================
    outlier_info = []
    iqr_outlier_indices = set()
    
    for col in types['numeric']:
        try:
            col_data = df[col].dropna()
            if len(col_data) < 4:
                continue
                
            Q1, Q3 = col_data.quantile(0.25), col_data.quantile(0.75)
            IQR = Q3 - Q1
            
            if IQR == 0:
                continue
            
            outlier_mask = (
                (df[col] < (Q1 - OUTLIER_IQR_MULTIPLIER * IQR)) |
                (df[col] > (Q3 + OUTLIER_IQR_MULTIPLIER * IQR))
            )
            outliers = outlier_mask.sum()
            
            if outliers > 0:
                pct = (outliers / total_rows) * 100
                outlier_info.append({
                    'Column': col,
                    'Outliers': outliers,
                    'Percentage': pct,
                    'Lower_Bound': Q1 - OUTLIER_IQR_MULTIPLIER * IQR,
                    'Upper_Bound': Q3 + OUTLIER_IQR_MULTIPLIER * IQR
                })
                iqr_outlier_indices.update(df[outlier_mask].index.tolist())
                
                if pct > 5:
                    deduct_quality_dimension(results, 'accuracy', min(10, pct))
                    deduct_health_score(results, min(5, pct/5))
                    results['issues'].append({
                        'type': 'Statistical Outliers',
                        'severity': 'Medium',
                        'message': f"'{col}' has {outliers:,} outliers ({pct:.1f}%)"
                    })
        except Exception as e:
            logger.log_error_with_context(e, f"Outlier analysis for {col}")
            continue
    
    if outlier_info:
        results['stats']['outlier_info'] = pd.DataFrame(outlier_info)
    
    # =====================================================================
    # 4. SKEWNESS ANALYSIS (Validity)
    # =====================================================================
    skew_info = []
    for col in types['numeric']:
        try:
            col_data = df[col].dropna()
            if len(col_data) < 3:
                continue
                
            skew = col_data.skew()
            if abs(skew) > MEDIUM_SKEW_THRESHOLD:
                skew_info.append({
                    'Column': col, 
                    'Skewness': round(skew, 3),
                    'Interpretation': 'Right-skewed' if skew > 0 else 'Left-skewed'
                })
                
                if abs(skew) > HIGH_SKEW_THRESHOLD:
                    deduct_quality_dimension(results, 'validity', 5)
                    deduct_health_score(results, 2)
                    results['issues'].append({
                        'type': 'High Skewness',
                        'severity': 'Low',
                        'message': f"'{col}' is highly skewed ({skew:.2f}) - consider log transform"
                    })
        except Exception as e:
            logger.log_error_with_context(e, f"Skewness analysis for {col}")
            continue
    
    if skew_info:
        results['stats']['skew_info'] = pd.DataFrame(skew_info)
    
    # =====================================================================
    # 5. CORRELATION ANALYSIS (Consistency)
    # =====================================================================
    if len(types['numeric']) > 1:
        try:
            valid_numeric = [c for c in types['numeric'] if df[c].notna().sum() > 10]
            
            if len(valid_numeric) > 1:
                corr_matrix = df[valid_numeric].corr()
                results['visualizations']['correlation'] = corr_matrix
                high_corr = []
                
                upper_triangle = np.triu_indices_from(corr_matrix, k=1)
                for i, j in zip(*upper_triangle):
                    corr_val = corr_matrix.iloc[i, j]
                    if pd.notna(corr_val) and abs(corr_val) > CORR_THRESHOLD:
                        c1, c2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        high_corr.append({
                            'Feature 1': c1, 
                            'Feature 2': c2, 
                            'Correlation': round(corr_val, 3)
                        })
                        deduct_quality_dimension(results, 'consistency', 5)
                        deduct_health_score(results, 2)
                        results['issues'].append({
                            'type': 'High Correlation',
                            'severity': 'Medium',
                            'message': f"'{c1}' & '{c2}' highly correlated ({corr_val:.2f}) - consider removing one"
                        })
                
                if high_corr:
                    results['stats']['high_corr'] = pd.DataFrame(high_corr)
                    
        except Exception as e:
            logger.log_error_with_context(e, "Correlation analysis")
    
    # =====================================================================
    # 6. AI ANOMALY DETECTION (Isolation Forest)
    # =====================================================================
    if len(types['numeric']) >= MIN_NUMERIC_COLS_FOR_AI and len(df) >= MIN_ROWS_FOR_AI:
        try:
            df_numeric = df[types['numeric']].copy()
            
            # Handle missing values based on method
            if imputation_method == 'drop':
                df_ai = df_numeric.dropna()
                indices_mapping = df_ai.index.tolist()
            elif imputation_method == 'mean':
                df_ai = df_numeric.fillna(df_numeric.mean())
                indices_mapping = df_ai.index.tolist()
            elif imputation_method == 'mice':
                try:
                    mice_imputer = IterativeImputer(
                        max_iter=10,
                        random_state=42,
                        initial_strategy='mean'
                    )
                    imputed_data = mice_imputer.fit_transform(df_numeric)
                    df_ai = pd.DataFrame(imputed_data, columns=df_numeric.columns, index=df_numeric.index)
                    indices_mapping = df_ai.index.tolist()
                except Exception as mice_error:
                    logger.log_error_with_context(mice_error, "MICE imputation failed, falling back to mean")
                    df_ai = df_numeric.fillna(df_numeric.mean())
                    indices_mapping = df_ai.index.tolist()
            else:
                df_ai = df_numeric.dropna()
                indices_mapping = df_ai.index.tolist()
            
            if len(df_ai) >= MIN_ROWS_FOR_AI:
                iso_forest = IsolationForest(
                    contamination=contamination,
                    random_state=42,
                    n_estimators=100,
                    n_jobs=-1
                )
                
                predictions = iso_forest.fit_predict(df_ai)
                anomaly_scores = iso_forest.score_samples(df_ai)
                
                results['model'] = iso_forest
                
                anomaly_mask = predictions == -1
                anomaly_indices = np.array(indices_mapping)[anomaly_mask]
                num_anomalies = len(anomaly_indices)
                
                if num_anomalies > 0:
                    results['stats']['ai_anomalies'] = {
                        'indices': anomaly_indices.tolist(),
                        'scores': anomaly_scores[anomaly_mask].tolist(),
                        'all_scores': anomaly_scores.tolist(),
                        'predictions': predictions.tolist()
                    }
                    
                    both_methods = set(anomaly_indices) & iqr_outlier_indices
                    deduct_quality_dimension(results, 'accuracy', min(15, num_anomalies / len(df) * 100))
                    deduct_health_score(results, min(10, num_anomalies / len(df) * 100))
                    
                    results['issues'].append({
                        'type': 'AI Anomaly Detection',
                        'severity': 'High',
                        'message': f"🤖 AI detected {num_anomalies:,} anomalies ({len(both_methods)} also statistical outliers)"
                    })
                    
                    # Feature importance
                    try:
                        importances = np.zeros(len(types['numeric']))
                        for tree in iso_forest.estimators_:
                            importances += tree.feature_importances_
                        importances /= len(iso_forest.estimators_)
                        
                        feature_imp = pd.DataFrame({
                            'Feature': types['numeric'],
                            'Importance': importances
                        }).sort_values('Importance', ascending=False)
                        results['stats']['feature_importance'] = feature_imp
                    except Exception as fi_error:
                        logger.log_error_with_context(fi_error, "Feature importance calculation")
                
                # PCA Analysis
                try:
                    scaler = StandardScaler()
                    scaled_data = scaler.fit_transform(df_ai)
                    
                    n_components = min(10, len(types['numeric']), len(df_ai))
                    pca = PCA(n_components=n_components)
                    pca_components = pca.fit_transform(scaled_data)
                    
                    results['stats']['pca'] = {
                        'explained': pca.explained_variance_ratio_,
                        'cumulative': np.cumsum(pca.explained_variance_ratio_),
                        'components': pca_components,
                        'anomaly_labels': predictions,
                        'variance_explained_2d': sum(pca.explained_variance_ratio_[:2]) if len(pca.explained_variance_ratio_) >= 2 else 0,
                        'loadings': pca.components_
                    }
                except Exception as pca_error:
                    logger.log_error_with_context(pca_error, "PCA analysis")
        
        except Exception as e:
            logger.log_error_with_context(e, "AI anomaly detection")
    
    # =====================================================================
    # 7. CALCULATE FINAL SCORES
    # =====================================================================
    
    weighted_score = sum(
        results['quality_dimensions'][dim] * QUALITY_WEIGHTS[dim]
        for dim in QUALITY_WEIGHTS.keys()
        if dim in results['quality_dimensions']
    )
    
    results['health_score'] = max(0, min(100, round(
        0.6 * weighted_score + 0.4 * results['health_score'], 1
    )))
    
    for dim in results['quality_dimensions']:
        results['quality_dimensions'][dim] = round(results['quality_dimensions'][dim], 1)
    
    logger.log_analysis_complete(results['health_score'], 0)
    
    return results