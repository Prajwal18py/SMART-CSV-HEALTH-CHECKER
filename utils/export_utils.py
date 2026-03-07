"""
Export Utilities
Shared download helper — all tabs import from here.
Returns the user's data in whatever format they originally uploaded.
"""
import io
import streamlit as st
import pandas as pd


def smart_download_button(
    df: pd.DataFrame,
    label: str,
    suffix: str,
    key: str,
    button_type: str = "secondary",
    button_width: str = "stretch",
    help_text: str = "",
):
    """
    Drop-in replacement for st.download_button.
    Automatically uses the user's original file format.

    Args:
        df               : DataFrame to export
        label            : Button label text
        suffix           : Added to filename e.g. "cleaned" → "sales_cleaned.tsv"
        key              : Unique Streamlit key
        button_type      : "primary" or "secondary"
        button_width: "stretch" or "content" — controls button width
        help_text        : Tooltip text

    Usage (identical to before, just swap the function):
        smart_download_button(cleaned_df, "⬇️ Download", "cleaned", key="dl_fix")
    """
    data, mime, filename = _serialize(df, suffix)

    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        type=button_type,
        width=button_width,
        key=key,
        help=help_text or f"Downloads as {filename}",
    )


# ─────────────────────────────────────────────
# INTERNALS
# ─────────────────────────────────────────────

def _serialize(df: pd.DataFrame, suffix: str):
    """
    Serialize df to the user's original upload format.
    Falls back to CSV if format unknown / not writable.

    Returns:
        (bytes, mime_type, filename)
    """
    import os

    original = st.session_state.get("original_filename", "data.csv")
    _, ext = os.path.splitext(original.lower())
    base = original.rsplit(".", 1)[0]
    out  = f"{base}_{suffix}{ext}"

    # ── CSV ──────────────────────────────────
    if ext in (".csv", ".txt"):
        return (
            df.to_csv(index=False).encode("utf-8"),
            "text/csv",
            out,
        )

    # ── TSV ──────────────────────────────────
    elif ext == ".tsv":
        return (
            df.to_csv(index=False, sep="\t").encode("utf-8"),
            "text/tab-separated-values",
            out,
        )

    # ── Excel ────────────────────────────────
    elif ext in (".xlsx", ".xls"):
        buf = io.BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        return (
            buf.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            f"{base}_{suffix}.xlsx",   # always save as .xlsx (not .xls)
        )

    # ── JSON ─────────────────────────────────
    elif ext == ".json":
        return (
            df.to_json(orient="records", indent=2).encode("utf-8"),
            "application/json",
            out,
        )

    # ── Parquet ──────────────────────────────
    elif ext == ".parquet":
        buf = io.BytesIO()
        df.to_parquet(buf, index=False, engine="pyarrow")
        return buf.getvalue(), "application/octet-stream", out

    # ── Feather ──────────────────────────────
    elif ext == ".feather":
        buf = io.BytesIO()
        df.to_feather(buf)
        return buf.getvalue(), "application/octet-stream", out

    # ── ORC ──────────────────────────────────
    elif ext == ".orc":
        buf = io.BytesIO()
        df.to_orc(buf)
        return buf.getvalue(), "application/octet-stream", out

    # ── Fallback → CSV ───────────────────────
    else:
        return (
            df.to_csv(index=False).encode("utf-8"),
            "text/csv",
            f"{base}_{suffix}.csv",
        )


def get_format_label() -> str:
    """Return a short label like 'TSV' or 'Parquet' for display in buttons."""
    import os
    original = st.session_state.get("original_filename", "data.csv")
    _, ext = os.path.splitext(original.lower())
    labels = {
        ".csv": "CSV", ".tsv": "TSV", ".txt": "TXT",
        ".xlsx": "Excel", ".xls": "Excel",
        ".json": "JSON", ".parquet": "Parquet",
        ".feather": "Feather", ".orc": "ORC",
    }
    return labels.get(ext, "CSV")