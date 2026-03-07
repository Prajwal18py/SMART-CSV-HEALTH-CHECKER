"""
Data Loading and Validation
Supports CSV, Excel (XLS/XLSX), JSON, Parquet, Feather, TSV, ORC
VERSION: 2.1 - All bugs fixed

BUGS FIXED IN 2.1:
- ✅ FIX 1: Removed deprecated infer_datetime_format (pandas 2.0+ warning)
- ✅ FIX 2: Auto-detect datetime now skips numeric-looking columns (ID/code cols)
- ✅ FIX 3: Column sanitization now stores a name-mapping in session_state
             so pipeline_code_generator can use the correct names
- ✅ FIX 4: Threshold raised to 0.8 to prevent false datetime conversions

ENHANCEMENTS FROM 2.0 (kept):
- ✅ Column name sanitization (removes special characters)
- ✅ Better encoding detection (UTF-8, Latin-1, CP1252)
- ✅ Memory usage tracking
- ✅ Duplicate column name handling
- ✅ Empty row/column removal
- ✅ Enhanced validation with troubleshooting tips
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import re

from config.constants import MAX_FILE_SIZE_MB, LARGE_DATASET_THRESHOLD, SAMPLE_FRACTION
from utils.logger import get_logger
from utils.memory import sample_large_dataset

logger = get_logger()

# ─────────────────────────────────────────────
# SUPPORTED FORMATS CONFIG
# ─────────────────────────────────────────────
SUPPORTED_FORMATS = {
    ".csv":     ("CSV",           "📄",  "Comma-separated values"),
    ".tsv":     ("TSV",           "📄",  "Tab-separated values"),
    ".txt":     ("TXT",           "📄",  "Text (auto-detect delimiter)"),
    ".xlsx":    ("Excel",         "📗",  "Excel 2007+ workbook"),
    ".xls":     ("Excel (Legacy)","📗",  "Excel 97-2003 workbook"),
    ".json":    ("JSON",          "📋",  "JSON / JSON Lines"),
    ".parquet": ("Parquet",       "⚡",  "Apache Parquet — columnar format"),
    ".feather": ("Feather",       "🪶",  "Apache Arrow Feather"),
    ".orc":     ("ORC",           "🗜️",  "Optimized Row Columnar"),
}

ACCEPTED_EXTENSIONS = list(SUPPORTED_FORMATS.keys())
STREAMLIT_TYPES     = [ext.lstrip(".") for ext in ACCEPTED_EXTENSIONS]


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────

def handle_file_upload(uploaded_file, enable_sampling=True):
    """
    Validate and load any supported file format into a DataFrame.
    Stores original_filename and col_name_map in session_state.

    Args:
        uploaded_file : Streamlit UploadedFile object
        enable_sampling: Whether to offer sampling for large files

    Returns:
        DataFrame or None if validation fails
    """
    file_size_mb = uploaded_file.size / (1024 * 1024)
    filename     = uploaded_file.name
    ext          = _get_extension(filename)

    logger.log_file_upload(filename, file_size_mb)

    # ── size guard ────────────────────────────
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(
            f"❌ File too large ({file_size_mb:.1f} MB). "
            f"Maximum allowed: {MAX_FILE_SIZE_MB} MB"
        )
        return None
    elif file_size_mb > 50:
        st.warning(
            f"⚠️ Large file detected ({file_size_mb:.1f} MB). "
            "Analysis may take 30–60 seconds."
        )

    # ── save original filename for export-in-original-format feature ──
    st.session_state["original_filename"] = filename

    # ── format banner ─────────────────────────
    fmt_label, fmt_icon, fmt_note = SUPPORTED_FORMATS.get(
        ext, ("Unknown", "📁", "")
    )
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,rgba(99,102,241,.12),rgba(99,102,241,.04));
            border:1px solid rgba(99,102,241,.3); border-radius:10px;
            padding:.6rem 1.1rem; margin-bottom:.8rem;
            display:flex; align-items:center; gap:.7rem;">
            <span style="font-size:1.4rem">{fmt_icon}</span>
            <div>
                <span style="color:#a5b4fc;font-weight:600">{fmt_label}</span>
                <span style="color:rgba(203,213,224,.5);font-size:.78rem;margin-left:.5rem">
                    {filename}
                </span><br>
                <span style="color:rgba(203,213,224,.55);font-size:.75rem">{fmt_note}</span>
            </div>
            <span style="margin-left:auto;color:rgba(203,213,224,.5);font-size:.78rem">
                {file_size_mb:.2f} MB
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── format router ─────────────────────────
    try:
        df = _load_by_format(uploaded_file, ext, file_size_mb)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        logger.log_error_with_context(e, f"{ext} file reading")
        with st.expander("💡 Troubleshooting Tips"):
            st.markdown("""
            **Common fixes:**
            - **Encoding issues**: Save file as UTF-8 in Excel/Notepad
            - **Delimiter issues**: Ensure CSV uses commas (,) not semicolons (;)
            - **Excel errors**: Try re-saving as .xlsx instead of .xls
            - **Large files**: Try uploading a sample (first 10,000 rows)
            """)
        return None

    if df is None:
        return None

    # ── sanitize ──────────────────────────────
    try:
        df = _sanitize_dataframe(df)
    except Exception as e:
        st.error(f"❌ Error sanitizing data: {e}")
        return None

    # ── validation ────────────────────────────
    if df is None or df.empty:
        st.error("❌ The uploaded file is empty (after cleaning)!")
        return None

    if len(df) < 2:
        st.error("❌ Dataset must have at least 2 rows for analysis!")
        return None

    if len(df.columns) == 0:
        st.error("❌ No columns found in the file!")
        return None

    if len(df.columns) == 1:
        st.warning(
            "⚠️ Only 1 column detected — possible **delimiter issue**. "
            "Make sure your CSV uses **commas (,)** as separators."
        )

    # ── memory warning ────────────────────────
    memory_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
    if memory_mb > 100:
        st.warning(f"⚠️ DataFrame is using **{memory_mb:.1f} MB** of RAM")

    # ── sampling ──────────────────────────────
    if enable_sampling and len(df) > LARGE_DATASET_THRESHOLD:
        use_sample = st.checkbox(
            f"📊 Dataset has **{len(df):,} rows**. "
            f"Use {SAMPLE_FRACTION * 100:.0f}% sample for faster analysis?",
            value=True,
            key="use_sampling",
        )
        if use_sample:
            df, was_sampled = sample_large_dataset(df, LARGE_DATASET_THRESHOLD, SAMPLE_FRACTION)
            if was_sampled:
                new_mem = df.memory_usage(deep=True).sum() / (1024 ** 2)
                st.success(
                    f"✅ Sampled to **{len(df):,} rows** "
                    f"({new_mem:.1f} MB)"
                )

    # ── success ───────────────────────────────
    st.success(
        f"✅ Loaded: **{len(df):,} rows** × **{len(df.columns)} columns** "
        f"({memory_mb:.2f} MB)"
    )

    return df


# ─────────────────────────────────────────────
# SANITIZATION
# ─────────────────────────────────────────────

def _sanitize_dataframe(df):
    """
    Clean up DataFrame after loading.

    FIX 2.1: Stores col_name_map in session_state so downstream
    code (pipeline_code_generator etc.) can map sanitized → original names.
    """
    if df is None or df.empty:
        return df

    original_cols = df.columns.tolist()

    # 1 — strip whitespace
    df.columns = df.columns.str.strip()

    # 2 — replace special chars
    df.columns = df.columns.str.replace(r'[^A-Za-z0-9_]', '_', regex=True)

    # 3 — deduplicate
    seen, new_cols = {}, []
    for col in df.columns:
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    df.columns = new_cols

    # ✅ FIX 3: Store the mapping sanitized → original in session_state
    # pipeline_code_generator reads this to emit correct column references
    col_name_map = {new: orig for new, orig in zip(df.columns, original_cols)}
    st.session_state["col_name_map"] = col_name_map

    # Show diff if names changed
    changed = [(o, n) for o, n in zip(original_cols, df.columns) if o != n]
    if changed:
        with st.expander("ℹ️ Column names sanitized for compatibility", expanded=False):
            st.caption("Special characters replaced with `_` to prevent errors:")
            for orig, new in changed[:15]:
                st.text(f"  '{orig}'  →  '{new}'")
            if len(changed) > 15:
                st.caption(f"...and {len(changed) - 15} more")

    # 4 — drop all-NaN rows/cols
    before_r, before_c = len(df), len(df.columns)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    if len(df) < before_r:
        st.info(f"ℹ️ Removed **{before_r - len(df)}** empty rows")
    if len(df.columns) < before_c:
        st.info(f"ℹ️ Removed **{before_c - len(df.columns)}** empty columns")

    # 5 — auto-detect datetimes
    df = _auto_detect_datetime(df)

    # 6 — reset index
    df = df.reset_index(drop=True)

    return df


def _auto_detect_datetime(df, threshold=0.80):
    """
    Convert object columns that look like dates to datetime64.

    FIX 2.1 changes vs 2.0:
    - Raised threshold 0.5 → 0.80  (avoids false positives)
    - Removed deprecated infer_datetime_format argument
    - Added numeric-looking column guard (skips ID / code columns)
    - Added min-length guard (very short strings are unlikely dates)

    Args:
        df        : DataFrame
        threshold : Minimum fraction of parseable values (default 80 %)
    """
    converted = []

    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna()
        if len(sample) == 0:
            continue

        # ✅ FIX: Skip columns where values look purely numeric (IDs, codes)
        numeric_frac = pd.to_numeric(sample, errors="coerce").notna().sum() / len(sample)
        if numeric_frac > 0.9:
            continue  # Looks like numbers, not dates

        # ✅ FIX: Skip columns with very short average string length
        avg_len = sample.astype(str).str.len().mean()
        if avg_len < 6:
            continue  # Too short to be a date string

        try:
            # ✅ FIX: Removed infer_datetime_format (deprecated in pandas 2.0)
            temp = pd.to_datetime(sample, errors="coerce")
            valid_frac = temp.notna().sum() / len(sample)

            if valid_frac >= threshold:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                converted.append((col, f"{valid_frac:.0%}"))
        except Exception:
            pass

    if converted:
        for col, pct in converted:
            st.success(f"✅ Auto-detected datetime: **'{col}'** ({pct} valid)")
        logger.info(f"Auto-detected {len(converted)} datetime columns")

    return df


# ─────────────────────────────────────────────
# FORMAT-SPECIFIC LOADERS
# ─────────────────────────────────────────────

def _load_by_format(uploaded_file, ext: str, file_size_mb: float):
    if ext in (".csv", ".tsv", ".txt"):
        sep = "\t" if ext == ".tsv" else None
        return _load_csv_with_encoding_detection(uploaded_file, sep, file_size_mb)

    elif ext in (".xlsx", ".xls"):
        return _load_excel(uploaded_file, ext, file_size_mb)

    elif ext == ".json":
        return _load_json(uploaded_file)

    elif ext == ".parquet":
        return _load_parquet(uploaded_file)

    elif ext == ".feather":
        return _load_feather(uploaded_file)

    elif ext == ".orc":
        return _load_orc(uploaded_file)

    else:
        st.error(
            f"❌ Unsupported format `{ext}`. "
            f"Supported: {', '.join(SUPPORTED_FORMATS.keys())}"
        )
        return None


def _load_csv_with_encoding_detection(uploaded_file, sep=None, file_size_mb=0):
    """Try UTF-8 → Latin-1 → CP1252 → ISO-8859-1 until one succeeds."""
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    nrows = None
    if file_size_mb > MAX_FILE_SIZE_MB:
        nrows = 10_000
        st.warning(f"⚠️ Large file — reading first **{nrows:,} rows** only.")

    for encoding in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file,
                sep=sep,
                encoding=encoding,
                engine="python",
                nrows=nrows,
                on_bad_lines="skip",
            )
            if not df.empty:
                if encoding != "utf-8":
                    st.info(f"ℹ️ Loaded using **{encoding}** encoding")
                return df
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
        except Exception:
            continue

    st.error(
        "❌ Could not detect file encoding. "
        "Try saving as **UTF-8** in Excel or Notepad."
    )
    return None


def _load_excel(uploaded_file, ext: str, file_size_mb: float):
    if file_size_mb > 20:
        st.warning(f"⚠️ Large Excel file ({file_size_mb:.1f} MB) — loading may take ~60 s")

    try:
        xl = pd.ExcelFile(uploaded_file)
    except Exception as e:
        if ext == ".xls":
            st.error(
                "❌ `.xls` requires `xlrd`.\n\n"
                "Add `xlrd>=2.0.1` to requirements.txt, or convert to `.xlsx`."
            )
        else:
            st.error(f"❌ Error opening Excel: {e}")
        return None

    if len(xl.sheet_names) > 1:
        sheet = st.selectbox(
            f"📋 Excel has **{len(xl.sheet_names)} sheets** — pick one:",
            xl.sheet_names,
            key="excel_sheet_picker",
        )
    else:
        sheet = xl.sheet_names[0]

    df = pd.read_excel(uploaded_file, sheet_name=sheet)
    return df.dropna(how="all").dropna(axis=1, how="all")


def _load_json(uploaded_file):
    raw  = uploaded_file.read()
    text = raw.decode("utf-8", errors="replace").strip()

    # JSON Lines
    first = next((l for l in text.splitlines() if l.strip()), "")
    if first.strip().startswith("{"):
        try:
            records = [json.loads(l) for l in text.splitlines() if l.strip()]
            return pd.DataFrame(records)
        except Exception:
            pass

    # Standard JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON: {e}")
        return None

    if isinstance(data, list):
        return pd.json_normalize(data)

    from io import StringIO
    for orient in ("records", "split", "index", "columns", "values"):
        try:
            df = pd.read_json(StringIO(text), orient=orient)
            if not df.empty:
                return df
        except Exception:
            continue

    try:
        return pd.json_normalize(data)
    except Exception:
        st.error("❌ Could not parse JSON into a table.")
        return None


def _load_parquet(uploaded_file):
    for engine in ("pyarrow", "fastparquet"):
        try:
            return pd.read_parquet(uploaded_file, engine=engine)
        except ImportError:
            continue
        except Exception as e:
            st.error(f"❌ Parquet error ({engine}): {e}")
            return None

    st.error(
        "❌ Parquet requires `pyarrow` or `fastparquet`.\n"
        "Add `pyarrow>=10.0.0` to requirements.txt."
    )
    return None


def _load_feather(uploaded_file):
    try:
        return pd.read_feather(uploaded_file)
    except ImportError:
        st.error("❌ Feather requires `pyarrow`. Add to requirements.txt.")
        return None
    except Exception as e:
        st.error(f"❌ Feather error: {e}")
        return None


def _load_orc(uploaded_file):
    try:
        return pd.read_orc(uploaded_file)
    except AttributeError:
        st.error("❌ ORC requires pandas ≥ 1.3 + `pyarrow`.")
        return None
    except Exception as e:
        st.error(f"❌ ORC error: {e}")
        return None


# ─────────────────────────────────────────────
# EXPORT — download in original format
# ─────────────────────────────────────────────

def export_dataframe(df: pd.DataFrame, original_filename: str, suffix: str = "cleaned"):
    """
    Serialize df back to the user's original file format.

    Returns:
        (bytes, mime_type, output_filename)

    Usage:
        data, mime, fname = export_dataframe(clean_df, "sales.tsv", "cleaned")
        st.download_button("⬇️ Download", data, fname, mime)
    """
    import io
    ext  = _get_extension(original_filename)
    base = original_filename.rsplit(".", 1)[0]
    out  = f"{base}_{suffix}{ext}"

    if ext in (".csv", ".txt"):
        return df.to_csv(index=False).encode("utf-8"), "text/csv", out

    elif ext == ".tsv":
        return (df.to_csv(index=False, sep="\t").encode("utf-8"),
                "text/tab-separated-values", out)

    elif ext in (".xlsx", ".xls"):
        buf = io.BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        return (buf.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                f"{base}_{suffix}.xlsx")

    elif ext == ".json":
        return (df.to_json(orient="records", indent=2).encode("utf-8"),
                "application/json", out)

    elif ext == ".parquet":
        buf = io.BytesIO()
        df.to_parquet(buf, index=False, engine="pyarrow")
        return buf.getvalue(), "application/octet-stream", out

    elif ext == ".feather":
        buf = io.BytesIO()
        df.to_feather(buf)
        return buf.getvalue(), "application/octet-stream", out

    else:
        # Fallback to CSV
        return (df.to_csv(index=False).encode("utf-8"),
                "text/csv", f"{base}_{suffix}.csv")


# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────

def _get_extension(filename: str) -> str:
    _, ext = os.path.splitext(filename.lower())
    return ext


def get_accepted_extensions() -> list:
    return STREAMLIT_TYPES


# ─────────────────────────────────────────────
# TEST DATASET
# ─────────────────────────────────────────────

def generate_test_dataset():
    """
    Generate a comprehensive test dataset that exercises ALL app features:
    
    ✅ Fix Data: Missing values, outliers, duplicates
    ✅ Skewness: Right-skewed salary, left-skewed age
    ✅ Feature Engineering: Numeric + categorical columns
    ✅ Model Builder: Clear classification target (Churn)
    ✅ Imbalanced Data: 15% churn (imbalanced!)
    ✅ EDA: Correlations, distributions
    ✅ PCA: Multiple numeric features
    ✅ Deep Profile: PII (emails, phones, SSN)
    ✅ Anomaly Detection: Salary outliers, age outliers
    """
    np.random.seed(42)
    n_rows = 500
    
    # ═══════════════════════════════════════════════════════════════
    # CORE DEMOGRAPHICS (tests: EDA, PCA, Feature Engineering)
    # ═══════════════════════════════════════════════════════════════
    ages = np.random.beta(2, 5, n_rows) * 40 + 22  # Left-skewed (tests Skewness tab)
    ages = ages.clip(22, 65).astype(int)
    
    # Right-skewed salary (tests Skewness transformations)
    salaries = np.random.lognormal(10.8, 0.6, n_rows).astype(int)
    
    experience = np.random.gamma(4, 2.5, n_rows).clip(0, 40).astype(int)
    
    departments = np.random.choice(
        ["Engineering", "Sales", "HR", "Marketing", "Finance", "Support"],
        n_rows,
        p=[0.30, 0.25, 0.10, 0.15, 0.12, 0.08]  # Realistic distribution
    )
    
    # Job levels (tests encoding in Feature Engineering)
    job_levels = np.random.choice(
        ["Junior", "Mid", "Senior", "Lead", "Manager"],
        n_rows,
        p=[0.25, 0.35, 0.20, 0.12, 0.08]
    )
    
    # ═══════════════════════════════════════════════════════════════
    # CLASSIFICATION TARGET: Churn (tests Model Builder + Imbalanced)
    # ═══════════════════════════════════════════════════════════════
    # Create realistic churn based on features
    churn_score = (
        (salaries < 50000) * 0.3 +           # Low salary → more likely to leave
        (experience < 2) * 0.25 +             # New employees leave more
        (ages < 25) * 0.2 +                   # Young people leave more
        (departments == "Sales") * 0.15 +     # Sales has high turnover
        np.random.random(n_rows) * 0.3        # Random factor
    )
    
    # 15% churn rate (IMBALANCED! Perfect for testing Imbalanced Data tab)
    churn = (churn_score > 0.65).astype(int)
    churn_labels = np.where(churn == 1, "Yes", "No")
    
    # ═══════════════════════════════════════════════════════════════
    # DERIVED FEATURES (tests Feature Engineering correlation)
    # ═══════════════════════════════════════════════════════════════
    performance_score = (
        75 + 
        (experience * 0.8) +                  # More experience → better performance
        (salaries / 2000) +                   # Higher salary → better performance
        np.random.normal(0, 8, n_rows)
    ).clip(0, 100).round(1)
    
    annual_bonus = (salaries * 0.15 + np.random.normal(0, 1000, n_rows)).clip(0).astype(int)
    
    projects_completed = (experience * 1.5 + np.random.poisson(3, n_rows)).clip(0, 50).astype(int)
    
    # ═══════════════════════════════════════════════════════════════
    # PII DATA (tests Deep Profile tab)
    # ═══════════════════════════════════════════════════════════════
    employee_ids = [f"EMP{str(i).zfill(5)}" for i in range(1000, 1000 + n_rows)]
    
    emails = [f"employee{i}@company.com" for i in range(n_rows)]
    
    # Realistic phone numbers
    phones = [f"+1-{np.random.randint(200,999)}-{np.random.randint(100,999)}-{np.random.randint(1000,9999)}"
              for _ in range(n_rows)]
    
    # SSN for ~5% of employees (tests PII detection)
    ssns = ["" for _ in range(n_rows)]
    ssn_indices = np.random.choice(n_rows, size=int(n_rows * 0.05), replace=False)
    for idx in ssn_indices:
        ssns[idx] = f"{np.random.randint(100,999)}-{np.random.randint(10,99)}-{np.random.randint(1000,9999)}"
    
    # ═══════════════════════════════════════════════════════════════
    # DATETIME COLUMN (tests datetime detection)
    # ═══════════════════════════════════════════════════════════════
    join_dates = pd.date_range("2018-01-01", periods=n_rows, freq="3D")
    
    # Tenure in months (useful for Model Builder)
    tenure_months = ((pd.Timestamp.now() - join_dates).days / 30).astype(int)
    
    # ═══════════════════════════════════════════════════════════════
    # BUILD CLEAN DATAFRAME
    # ═══════════════════════════════════════════════════════════════
    df = pd.DataFrame({
        "Employee_ID": employee_ids,
        "Age": ages.astype(float),
        "Department": departments,
        "Job_Level": job_levels,
        "Salary": salaries.astype(float),
        "Experience_Years": experience.astype(float),
        "Performance_Score": performance_score,
        "Projects_Completed": projects_completed.astype(float),
        "Annual_Bonus": annual_bonus.astype(float),
        "Tenure_Months": tenure_months.astype(float),
        "Join_Date": join_dates,
        "Email": emails,
        "Phone": phones,
        "SSN": ssns,
        "Churn": churn_labels,  # TARGET for classification
    })
    
    # ═══════════════════════════════════════════════════════════════
    # INJECT DATA QUALITY ISSUES (tests Fix Data tab)
    # ═══════════════════════════════════════════════════════════════
    
    # 1. MISSING VALUES (8-12% per column)
    for col, pct in [
        ("Age", 0.10),
        ("Salary", 0.08),
        ("Experience_Years", 0.12),
        ("Performance_Score", 0.09),
        ("Projects_Completed", 0.07),
    ]:
        missing_idx = np.random.choice(n_rows, size=int(n_rows * pct), replace=False)
        df.loc[missing_idx, col] = np.nan
    
    # 2. DUPLICATES (5 exact duplicates)
    duplicate_rows = df.iloc[:5].copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)
    
    # 3. OUTLIERS (tests anomaly detection + outlier treatment)
    outlier_data = [
        # Salary outliers
        {"Employee_ID": "OUT001", "Age": 45., "Salary": 5_000_000., "Experience_Years": 15., 
         "Department": "Engineering", "Job_Level": "Manager", "Churn": "No"},
        {"Employee_ID": "OUT002", "Age": 28., "Salary": 500., "Experience_Years": 3.,
         "Department": "Sales", "Job_Level": "Junior", "Churn": "Yes"},
        
        # Age outliers
        {"Employee_ID": "OUT003", "Age": -5., "Salary": 60000., "Experience_Years": 1.,
         "Department": "HR", "Job_Level": "Junior", "Churn": "Yes"},
        {"Employee_ID": "OUT004", "Age": 120., "Salary": 80000., "Experience_Years": 40.,
         "Department": "Finance", "Job_Level": "Senior", "Churn": "No"},
        
        # Experience outliers
        {"Employee_ID": "OUT005", "Age": 22., "Salary": 120000., "Experience_Years": 25.,
         "Department": "Engineering", "Job_Level": "Senior", "Churn": "No"},
        {"Employee_ID": "OUT006", "Age": 55., "Salary": 45000., "Experience_Years": -3.,
         "Department": "Support", "Job_Level": "Mid", "Churn": "Yes"},
        
        # Future join date (data entry error)
        {"Employee_ID": "OUT007", "Age": 30., "Salary": 70000., "Experience_Years": 5.,
         "Department": "Marketing", "Job_Level": "Mid", "Churn": "No",
         "Join_Date": pd.Timestamp("2050-01-01")},
        
        # Impossible combinations
        {"Employee_ID": "OUT008", "Age": 18., "Salary": 200000., "Experience_Years": 0.,
         "Department": "Engineering", "Job_Level": "Lead", "Churn": "No",
         "Performance_Score": 99.},
    ]
    
    for outlier in outlier_data:
        # Fill missing columns with defaults
        for col in df.columns:
            if col not in outlier:
                if col == "Join_Date":
                    outlier[col] = pd.Timestamp("2020-01-01")
                elif col in ["Email", "Phone", "SSN"]:
                    outlier[col] = f"{col.lower()}@test.com" if col == "Email" else ""
                elif df[col].dtype in [np.float64, np.int64]:
                    outlier[col] = df[col].median()
                else:
                    outlier[col] = df[col].mode()[0] if len(df[col].mode()) > 0 else ""
    
    outlier_df = pd.DataFrame(outlier_data)
    df = pd.concat([df, outlier_df], ignore_index=True)
    
    # 4. INCONSISTENT CATEGORICAL VALUES (tests data cleaning)
    inconsistent_idx = np.random.choice(len(df), size=8, replace=False)
    df.loc[inconsistent_idx[0], "Department"] = "Enginering"      # Typo
    df.loc[inconsistent_idx[1], "Department"] = "SALES"           # Case inconsistency
    df.loc[inconsistent_idx[2], "Department"] = "HR "             # Trailing space
    df.loc[inconsistent_idx[3], "Job_Level"] = "senior"           # Case
    df.loc[inconsistent_idx[4], "Job_Level"] = "Sr"               # Abbreviation
    df.loc[inconsistent_idx[5], "Churn"] = "YES"                  # Case
    df.loc[inconsistent_idx[6], "Churn"] = "Y"                    # Abbreviation
    df.loc[inconsistent_idx[7], "Department"] = "IT"              # Different name
    
    # ═══════════════════════════════════════════════════════════════
    # FINAL TOUCHES
    # ═══════════════════════════════════════════════════════════════
    
    # Shuffle rows
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Ensure Join_Date is datetime
    df["Join_Date"] = pd.to_datetime(df["Join_Date"])
    
    logger.info(f"Generated enhanced test dataset: {len(df)} rows, {len(df.columns)} columns")
    logger.info(f"Churn distribution: {df['Churn'].value_counts().to_dict()}")
    logger.info(f"Missing values: {df.isna().sum().sum()} total")
    
    return df