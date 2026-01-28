"""
Configuration constants for Smart CSV Health Checker
"""

# =================================================================
# ANALYSIS THRESHOLDS
# =================================================================
CORR_THRESHOLD = 0.9
OUTLIER_IQR_MULTIPLIER = 1.5
MAX_FILE_SIZE_MB = 200
HIGH_SKEW_THRESHOLD = 2.0
MEDIUM_SKEW_THRESHOLD = 1.0
DEFAULT_AI_CONTAMINATION = 0.05
MIN_ROWS_FOR_AI = 10
MIN_NUMERIC_COLS_FOR_AI = 2

# Missing Value Thresholds
HIGH_MISSING_THRESHOLD = 0.5       # 50% - suggest dropping column
MEDIUM_MISSING_THRESHOLD = 0.3     # 30% - high severity issue
LOW_MISSING_THRESHOLD = 0.1        # 10% - medium severity issue

# Column Detection
ID_COLUMN_UNIQUENESS = 0.9         # 90% unique = likely ID column
MIN_ROWS_FOR_ID_DETECTION = 50

# Display Limits
DISPLAY_ROW_LIMIT = 20
MAX_CATEGORIES_DISPLAY = 10
MAX_COLUMNS_PROFILE = 50

# Sampling
LARGE_DATASET_THRESHOLD = 100000
SAMPLE_FRACTION = 0.1

# Cache TTL (seconds)
CACHE_TTL = 3600

# =================================================================
# UI COLORS (for metric cards)
# =================================================================
COLORS = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#06b6d4'
}

# =================================================================
# GRADE THRESHOLDS
# =================================================================
GRADE_THRESHOLDS = {
    'A+': 90,
    'A': 80,
    'B': 70,
    'C': 60,
    'D': 50,
    'F': 0
}

# =================================================================
# QUALITY DIMENSION WEIGHTS
# =================================================================
QUALITY_WEIGHTS = {
    'completeness': 0.25,    # Missing values
    'consistency': 0.20,     # Duplicates, format issues
    'accuracy': 0.25,        # Outliers, impossible values
    'validity': 0.15,        # Data type mismatches
    'uniqueness': 0.15       # Duplicate detection
}

# =================================================================
# FEATURE FLAGS
# =================================================================
REPORTLAB_AVAILABLE = True  # Set based on import success
ENABLE_CACHING = True
ENABLE_SAMPLING_PROMPT = True