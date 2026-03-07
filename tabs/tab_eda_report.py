"""
Tab: EDA Report
Auto-generated Exploratory Data Analysis — comprehensive, beautiful, downloadable
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
import datetime
import io

# ══════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════
EDA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

/* ── alert cards ── */
.eda-alert {
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin-bottom: .7rem;
    display: flex;
    align-items: flex-start;
    gap: .9rem;
    border: 1px solid;
    transition: transform .2s;
}
.eda-alert:hover { transform: translateX(4px); }
.eda-alert.critical {
    background: rgba(239,68,68,.08);
    border-color: rgba(239,68,68,.35);
}
.eda-alert.warning {
    background: rgba(251,191,36,.07);
    border-color: rgba(251,191,36,.3);
}
.eda-alert.info {
    background: rgba(99,102,241,.07);
    border-color: rgba(99,102,241,.25);
}
.eda-alert.success {
    background: rgba(16,185,129,.07);
    border-color: rgba(16,185,129,.25);
}
.alert-icon { font-size: 1.3rem; line-height: 1; flex-shrink:0; padding-top:.1rem; }
.alert-title { color:#e2e8f0; font-weight:600; font-size:.88rem; margin:0 0 .15rem 0; }
.alert-body  { color:rgba(203,213,224,.65); font-size:.78rem; margin:0; line-height:1.5; }

/* ── quality score ring ── */
.score-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1;
    margin: 0;
}
.score-label {
    font-size: .75rem;
    color: rgba(203,213,224,.5);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: .3rem;
}

/* ── section heading ── */
.eda-section-head {
    display: flex;
    align-items: center;
    gap: .7rem;
    margin: 1.6rem 0 1rem 0;
    padding-bottom: .5rem;
    border-bottom: 1px solid rgba(99,102,241,.2);
}
.eda-section-head .icon { font-size:1.3rem; }
.eda-section-head .title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #c7d2fe;
    margin: 0;
}
.eda-section-head .count {
    margin-left: auto;
    background: rgba(99,102,241,.2);
    color: #a5b4fc;
    border-radius: 20px;
    padding: .15rem .6rem;
    font-size: .72rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}

/* ── variable card ── */
.var-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(99,102,241,.18);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: .7rem;
    transition: border-color .25s, box-shadow .25s;
}
.var-card:hover {
    border-color: rgba(99,102,241,.5);
    box-shadow: 0 4px 20px rgba(99,102,241,.12);
}
.var-name {
    font-family: 'DM Mono', monospace;
    color: #a5b4fc;
    font-size: .88rem;
    font-weight: 500;
    margin: 0 0 .4rem 0;
}
.var-type-badge {
    display: inline-block;
    padding: .12rem .45rem;
    border-radius: 20px;
    font-size: .65rem;
    font-weight: 600;
    letter-spacing: .5px;
    margin-bottom: .6rem;
}
.badge-numeric  { background:rgba(99,102,241,.2);  color:#a5b4fc; border:1px solid rgba(99,102,241,.3); }
.badge-category { background:rgba(16,185,129,.15); color:#6ee7b7; border:1px solid rgba(16,185,129,.3); }
.badge-datetime { background:rgba(251,191,36,.15); color:#fbbf24; border:1px solid rgba(251,191,36,.3); }
.badge-text     { background:rgba(244,114,182,.15);color:#f9a8d4; border:1px solid rgba(244,114,182,.3); }

.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: .4rem;
    margin-top: .5rem;
}
.stat-cell {
    background: rgba(0,0,0,.25);
    border-radius: 8px;
    padding: .4rem .6rem;
    text-align: center;
}
.stat-val { color:#e2e8f0; font-family:'DM Mono',monospace; font-size:.82rem; font-weight:500; }
.stat-key { color:rgba(203,213,224,.45); font-size:.65rem; margin-top:.1rem; }

/* ── missing bar ── */
.miss-bar-wrap { margin-top:.5rem; }
.miss-bar-bg {
    background: rgba(255,255,255,.07);
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
}
.miss-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width .4s ease;
}
</style>
"""

# ══════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

def render_eda_tab(df: pd.DataFrame, col_types: dict, settings: dict = None):
    """Render the EDA Report tab"""
    settings = settings or {}
    # ✅ WIRED: sidebar 'Correlation Threshold' and 'Max Categories'
    _corr_threshold = float(settings.get('correlation_threshold', 0.7))
    _max_categories = int(settings.get('max_categories', 20))
    st.markdown(EDA_CSS, unsafe_allow_html=True)

    st.subheader("📋 EDA Report")
    st.caption("Auto-generated exploratory analysis — alerts, distributions, correlations & more")

    if df is None or df.empty:
        st.warning("⚠️ No data loaded. Upload a file first.")
        return

    # Pre-compute everything once
    report = _compute_report(df, col_types)

    # ── top bar: quality score + quick stats ──
    _render_header_bar(df, report)

    st.markdown("---")

    # ── five sections ──
    _render_alerts(report)
    _render_overview(df, report)
    _render_variable_analysis(df, report)
    _render_correlations(df, report)
    _render_missing_analysis(df, report)

    st.markdown("---")

    # ── export ──
    _render_export(df, report)


# ══════════════════════════════════════════════════════════════════════
# COMPUTATION
# ══════════════════════════════════════════════════════════════════════

def _compute_report(df: pd.DataFrame, col_types: dict) -> dict:
    numeric_cols  = col_types.get("numeric",     [])
    category_cols = col_types.get("categorical",  [])
    datetime_cols = col_types.get("datetime",     [])

    # ── missing ──────────────────────────────
    missing       = df.isnull().sum()
    missing_pct   = (missing / len(df) * 100).round(2)

    # ── duplicates ───────────────────────────
    n_dupes = int(df.duplicated().sum())

    # ── per-column stats ─────────────────────
    col_stats = {}
    for col in df.columns:
        s = df[col]
        miss_n   = int(s.isna().sum())
        miss_p   = round(miss_n / len(df) * 100, 2)
        n_unique = int(s.nunique(dropna=True))
        dtype    = str(s.dtype)

        if col in numeric_cols:
            vals = s.dropna()
            sk   = float(vals.skew())   if len(vals) > 2 else 0.0
            kurt = float(vals.kurtosis()) if len(vals) > 2 else 0.0
            col_stats[col] = {
                "type": "numeric", "dtype": dtype,
                "missing_n": miss_n, "missing_pct": miss_p,
                "unique": n_unique,
                "mean":   round(float(vals.mean()), 4)   if len(vals) else None,
                "median": round(float(vals.median()), 4) if len(vals) else None,
                "std":    round(float(vals.std()),  4)   if len(vals) else None,
                "min":    round(float(vals.min()),  4)   if len(vals) else None,
                "max":    round(float(vals.max()),  4)   if len(vals) else None,
                "q25":    round(float(vals.quantile(.25)), 4) if len(vals) else None,
                "q75":    round(float(vals.quantile(.75)), 4) if len(vals) else None,
                "skew":   round(sk, 3),
                "kurt":   round(kurt, 3),
                "zeros":  int((vals == 0).sum()),
                "negatives": int((vals < 0).sum()),
            }
        elif col in category_cols:
            vc = s.value_counts(dropna=True)
            col_stats[col] = {
                "type": "categorical", "dtype": dtype,
                "missing_n": miss_n, "missing_pct": miss_p,
                "unique": n_unique,
                "top_value":   str(vc.index[0]) if len(vc) else "—",
                "top_count":   int(vc.iloc[0])  if len(vc) else 0,
                "top_pct":     round(vc.iloc[0] / len(df) * 100, 1) if len(vc) else 0,
                "value_counts": vc.head(10).to_dict(),
            }
        elif col in datetime_cols:
            col_stats[col] = {
                "type": "datetime", "dtype": dtype,
                "missing_n": miss_n, "missing_pct": miss_p,
                "unique": n_unique,
                "min": str(df[col].min()),
                "max": str(df[col].max()),
            }
        else:
            avg_len = round(s.dropna().astype(str).str.len().mean(), 1) if miss_n < len(df) else 0
            col_stats[col] = {
                "type": "text", "dtype": dtype,
                "missing_n": miss_n, "missing_pct": miss_p,
                "unique": n_unique,
                "avg_length": avg_len,
            }

    # ── quality score ────────────────────────
    score = _compute_quality_score(df, col_stats, n_dupes)

    # ── alerts ───────────────────────────────
    alerts = _generate_alerts(df, col_stats, n_dupes, numeric_cols, category_cols)

    # ── correlations ─────────────────────────
    corr_matrix = None
    top_corrs   = []
    if len(numeric_cols) >= 2:
        num_df      = df[numeric_cols].dropna()
        corr_matrix = num_df.corr()
        # Top pairs (upper triangle, abs > 0.5)
        seen = set()
        for c1 in numeric_cols:
            for c2 in numeric_cols:
                if c1 != c2 and (c2, c1) not in seen:
                    val = corr_matrix.loc[c1, c2]
                    if not np.isnan(val):
                        top_corrs.append((c1, c2, round(float(val), 3)))
                    seen.add((c1, c2))
        top_corrs.sort(key=lambda x: abs(x[2]), reverse=True)

    return {
        "n_rows":       len(df),
        "n_cols":       len(df.columns),
        "n_dupes":      n_dupes,
        "missing":      missing,
        "missing_pct":  missing_pct,
        "total_missing":int(missing.sum()),
        "numeric_cols": numeric_cols,
        "category_cols":category_cols,
        "datetime_cols":datetime_cols,
        "col_stats":    col_stats,
        "quality_score":score,
        "alerts":       alerts,
        "corr_matrix":  corr_matrix,
        "top_corrs":    top_corrs,
        "memory_mb":    round(df.memory_usage(deep=True).sum() / 1024**2, 2),
    }


def _compute_quality_score(df, col_stats, n_dupes):
    score = 100.0
    # Missing values penalty
    total_cells = len(df) * len(df.columns)
    total_missing = sum(v["missing_n"] for v in col_stats.values())
    missing_rate = total_missing / total_cells if total_cells else 0
    score -= missing_rate * 40

    # Duplicates penalty
    dupe_rate = n_dupes / len(df) if len(df) else 0
    score -= dupe_rate * 20

    # Skewness penalty
    high_skew = sum(1 for v in col_stats.values()
                    if v["type"] == "numeric" and abs(v.get("skew", 0)) > 2)
    num_cols = sum(1 for v in col_stats.values() if v["type"] == "numeric")
    if num_cols:
        score -= (high_skew / num_cols) * 15

    # High cardinality penalty
    high_card = sum(1 for v in col_stats.values()
                    if v["type"] == "categorical" and v.get("unique", 0) > 50)
    cat_cols = sum(1 for v in col_stats.values() if v["type"] == "categorical")
    if cat_cols:
        score -= (high_card / cat_cols) * 10

    return max(0, min(100, round(score, 1)))


def _generate_alerts(df, col_stats, n_dupes, numeric_cols, category_cols):
    alerts = []

    # Missing values
    high_miss = [(c, v["missing_pct"]) for c, v in col_stats.items()
                 if v["missing_pct"] > 20]
    if high_miss:
        cols_str = ", ".join(f"{c} ({p}%)" for c, p in sorted(high_miss, key=lambda x: -x[1])[:5])
        alerts.append(("critical", "🚨", "High Missing Values",
                        f"{len(high_miss)} column(s) missing >20% of data: {cols_str}"))

    any_miss = [(c, v["missing_pct"]) for c, v in col_stats.items()
                if 0 < v["missing_pct"] <= 20]
    if any_miss:
        alerts.append(("warning", "⚠️", "Missing Values Detected",
                        f"{len(any_miss)} column(s) have some missing values (≤20%). "
                        "Visit Fix Data tab to handle them."))

    # Duplicates
    if n_dupes > 0:
        dupe_pct = round(n_dupes / len(df) * 100, 1)
        lvl = "critical" if dupe_pct > 5 else "warning"
        alerts.append((lvl, "♊", "Duplicate Rows",
                        f"{n_dupes:,} duplicate rows detected ({dupe_pct}% of dataset). "
                        "Remove in the Fix Data tab."))

    # Severe skewness
    severe_skew = [(c, v["skew"]) for c, v in col_stats.items()
                   if v["type"] == "numeric" and abs(v.get("skew", 0)) > 2]
    if severe_skew:
        cols_str = ", ".join(f"{c} (skew={s:.1f})" for c, s in severe_skew[:4])
        alerts.append(("warning", "📐", "Severe Skewness",
                        f"{len(severe_skew)} numeric column(s) are highly skewed: {cols_str}. "
                        "Fix in Skewness tab."))

    # Outlier-prone (using IQR)
    outlier_cols = []
    for c in numeric_cols:
        s = df[c].dropna()
        if len(s) < 4:
            continue
        q1, q3 = s.quantile(.25), s.quantile(.75)
        iqr = q3 - q1
        if iqr > 0:
            n_out = int(((s < q1 - 3*iqr) | (s > q3 + 3*iqr)).sum())
            if n_out > 0:
                outlier_cols.append((c, n_out))
    if outlier_cols:
        cols_str = ", ".join(f"{c}({n})" for c, n in sorted(outlier_cols, key=lambda x: -x[1])[:5])
        alerts.append(("warning", "📊", "Potential Outliers",
                        f"Extreme outliers (3×IQR) found in: {cols_str}. "
                        "Review in Fix Data tab."))

    # High cardinality
    high_card = [(c, v["unique"]) for c, v in col_stats.items()
                 if v["type"] == "categorical" and v.get("unique", 0) > 50]
    if high_card:
        cols_str = ", ".join(f"{c} ({u} cats)" for c, u in high_card[:3])
        alerts.append(("info", "🗂️", "High Cardinality Columns",
                        f"{len(high_card)} categorical column(s) have >50 unique values: {cols_str}. "
                        "Consider grouping rare categories."))

    # Constant / near-constant columns
    const_cols = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
    if const_cols:
        alerts.append(("info", "🔒", "Constant Columns",
                        f"{len(const_cols)} column(s) have only 1 unique value: {', '.join(const_cols[:5])}. "
                        "These add no information and can be dropped."))

    # Negative values in likely-positive columns
    neg_cols = [(c, v["negatives"]) for c, v in col_stats.items()
                if v["type"] == "numeric" and v.get("negatives", 0) > 0
                and any(kw in c.lower() for kw in ("age","salary","price","count","revenue","amount","score"))]
    if neg_cols:
        alerts.append(("warning", "➖", "Unexpected Negative Values",
                        f"Negative values in columns that should be positive: "
                        + ", ".join(f"{c}({n})" for c, n in neg_cols[:4])))

    # All good
    if not alerts:
        alerts.append(("success", "✅", "Data Looks Clean!",
                        "No critical issues detected. Your data appears to be in good shape."))

    return alerts


# ══════════════════════════════════════════════════════════════════════
# RENDERING SECTIONS
# ══════════════════════════════════════════════════════════════════════

def _render_header_bar(df, report):
    score = report["quality_score"]
    score_color = ("#6ee7b7" if score >= 80 else
                   "#fbbf24" if score >= 55 else "#f87171")

    hcol1, hcol2, hcol3, hcol4, hcol5, hcol6 = st.columns([1.4, 1, 1, 1, 1, 1])

    with hcol1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(30,41,59,.9),rgba(15,23,42,.9));
                    border:1px solid rgba(99,102,241,.25);border-radius:14px;
                    padding:1rem;text-align:center;">
            <p class="score-number" style="color:{score_color}">{score}</p>
            <p class="score-label">Data Quality</p>
            <div style="background:rgba(0,0,0,.3);border-radius:6px;height:6px;margin-top:.5rem;">
                <div style="background:{score_color};width:{score}%;height:100%;border-radius:6px;
                            transition:width .6s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    metrics = [
        ("📏", f"{report['n_rows']:,}", "Rows"),
        ("📊", f"{report['n_cols']}", "Columns"),
        ("❓", f"{report['total_missing']:,}", "Missing"),
        ("♊", f"{report['n_dupes']:,}", "Duplicates"),
        ("💾", f"{report['memory_mb']} MB", "Memory"),
    ]
    for col, (icon, val, label) in zip([hcol2, hcol3, hcol4, hcol5, hcol6], metrics):
        with col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(30,41,59,.8),rgba(15,23,42,.8));
                        border:1px solid rgba(99,102,241,.18);border-radius:12px;
                        padding:.9rem;text-align:center;height:100%;">
                <div style="font-size:1.3rem">{icon}</div>
                <div style="font-family:'DM Mono',monospace;color:#e2e8f0;
                            font-size:1.1rem;font-weight:500;margin:.2rem 0">{val}</div>
                <div style="color:rgba(203,213,224,.45);font-size:.7rem">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_alerts(report):
    alerts = report["alerts"]
    st.markdown(f"""
    <div class="eda-section-head">
        <span class="icon">🚨</span>
        <p class="title">Alerts & Recommendations</p>
        <span class="count">{len(alerts)}</span>
    </div>
    """, unsafe_allow_html=True)

    for level, icon, title, body in alerts:
        st.markdown(f"""
        <div class="eda-alert {level}">
            <span class="alert-icon">{icon}</span>
            <div>
                <p class="alert-title">{title}</p>
                <p class="alert-body">{body}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_overview(df, report):
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🗂️</span>
        <p class="title">Dataset Overview</p>
    </div>
    """, unsafe_allow_html=True)

    nc = len(report["numeric_cols"])
    cc = len(report["category_cols"])
    dc = len(report["datetime_cols"])
    tc = report["n_cols"] - nc - cc - dc

    # Column type donut
    c1, c2 = st.columns([1, 1.5])

    with c1:
        all_labels = ["Numeric", "Categorical", "Datetime", "Text/Other"]
        all_values = [nc, cc, dc, tc]
        all_colors = ["#6366f1", "#6ee7b7", "#fbbf24", "#f9a8d4"]
        # ✅ Filter out zero-value slices so they don't clutter the legend/chart
        labels = [l for l, v in zip(all_labels, all_values) if v > 0]
        values = [v for v in all_values if v > 0]
        colors = [c for c, v in zip(all_colors, all_values) if v > 0]

        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=.62,
            marker=dict(colors=colors, line=dict(color='rgba(0,0,0,.4)', width=2)),
            textinfo="percent",          # ✅ percent only on slice, label in legend
            textposition="inside",       # ✅ keep text inside slice, no overlap
            textfont=dict(color='#fff', size=11),
            hovertemplate="%{label}: %{value} cols (%{percent})<extra></extra>"
        ))
        fig.add_annotation(
            text=f"<b>{report['n_cols']}</b><br><span style='font-size:10px'>cols</span>",
            x=.5, y=.5, showarrow=False,
            font=dict(size=18, color='#e2e8f0')
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(
                font=dict(color='#cbd5e1', size=11),
                bgcolor='rgba(0,0,0,0)',
                orientation='v',
                x=1.02, y=0.5,
                xanchor='left', yanchor='middle'
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=10, l=10, r=100),  # ✅ right margin for legend
            height=240,
            title=dict(text="Column Types", font=dict(color='#a5b4fc', size=13), x=.5)
        )
        st.plotly_chart(fig, width='stretch')

    with c2:
        # Column summary table
        rows = []
        for col in df.columns:
            cs = report["col_stats"][col]
            rows.append({
                "Column":     col,
                "Type":       cs["type"].capitalize(),
                "dtype":      cs["dtype"],
                "Missing %":  f"{cs['missing_pct']}%",
                "Unique":     cs["unique"],
            })
        summary_df = pd.DataFrame(rows)
        st.dataframe(
            summary_df.style
                .apply(lambda x: [
                    "color: #f87171" if v.endswith('%') and float(v[:-1]) > 20
                    else "color: #fbbf24" if v.endswith('%') and float(v[:-1]) > 0
                    else "" for v in x
                ], subset=["Missing %"]),
            width='stretch', height=240
        )


def _render_variable_analysis(df, report):
    n_cols = report["n_cols"]
    st.markdown(f"""
    <div class="eda-section-head">
        <span class="icon">🔬</span>
        <p class="title">Variable Analysis</p>
        <span class="count">{n_cols} columns</span>
    </div>
    """, unsafe_allow_html=True)

    # Tabs: Numeric | Categorical | All
    numeric_cols  = report["numeric_cols"]
    category_cols = report["category_cols"]

    tab_n, tab_c, tab_all = st.tabs([
        f"📈 Numeric ({len(numeric_cols)})",
        f"🏷️ Categorical ({len(category_cols)})",
        f"📋 All Columns",
    ])

    with tab_n:
        if not numeric_cols:
            st.info("No numeric columns found.")
        else:
            _render_numeric_vars(df, report, numeric_cols)

    with tab_c:
        if not category_cols:
            st.info("No categorical columns found.")
        else:
            _render_categorical_vars(df, report, category_cols)

    with tab_all:
        _render_all_vars(df, report)


def _render_numeric_vars(df, report, numeric_cols):
    # Distribution grid — 2 per row
    for i in range(0, len(numeric_cols), 2):
        cols_pair = numeric_cols[i:i+2]
        grid_cols = st.columns(len(cols_pair))

        for gcol, col in zip(grid_cols, cols_pair):
            with gcol:
                cs = report["col_stats"][col]
                s  = df[col].dropna()

                # Stat card header
                miss_color = "#f87171" if cs["missing_pct"] > 20 else (
                             "#fbbf24" if cs["missing_pct"] > 0  else "#6ee7b7")
                skew_flag  = " 📐" if abs(cs.get("skew", 0)) > 1 else ""

                st.markdown(f"""
                <div class="var-card">
                    <p class="var-name">{col}{skew_flag}</p>
                    <span class="var-type-badge badge-numeric">NUMERIC</span>
                    <div class="stat-grid">
                        <div class="stat-cell">
                            <div class="stat-val">{cs['mean'] if cs['mean'] is not None else '—'}</div>
                            <div class="stat-key">mean</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val">{cs['median'] if cs['median'] is not None else '—'}</div>
                            <div class="stat-key">median</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val">{cs['std'] if cs['std'] is not None else '—'}</div>
                            <div class="stat-key">std</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val" style="color:{miss_color}">{cs['missing_pct']}%</div>
                            <div class="stat-key">missing</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val">{cs['min'] if cs['min'] is not None else '—'}</div>
                            <div class="stat-key">min</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val">{cs['max'] if cs['max'] is not None else '—'}</div>
                            <div class="stat-key">max</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val">{cs['skew']}</div>
                            <div class="stat-key">skew</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val">{cs['kurt']}</div>
                            <div class="stat-key">kurtosis</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Histogram + KDE
                if len(s) > 1:
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(
                        x=s, nbinsx=30,
                        marker=dict(color='rgba(99,102,241,.6)',
                                    line=dict(color='rgba(99,102,241,.9)', width=.5)),
                        name="count", showlegend=False
                    ))
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(t=5, b=5, l=5, r=5), height=160,
                        xaxis=dict(color='#64748b', tickfont=dict(size=9)),
                        yaxis=dict(color='#64748b', tickfont=dict(size=9)),
                        bargap=.05
                    )
                    st.plotly_chart(fig, width='stretch')

                    # Box plot (compact)
                    fig2 = go.Figure(go.Box(
                        x=s, marker_color='#6366f1',
                        line_color='#818cf8', fillcolor='rgba(99,102,241,.15)',
                        showlegend=False, name=col,
                        boxpoints='outliers',
                        marker=dict(size=4, color='#f87171', opacity=.6)
                    ))
                    fig2.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(t=2, b=2, l=5, r=5), height=80,
                        xaxis=dict(color='#64748b', tickfont=dict(size=8)),
                        yaxis=dict(visible=False)
                    )
                    st.plotly_chart(fig2, width='stretch')


def _render_categorical_vars(df, report, category_cols):
    for i in range(0, len(category_cols), 2):
        cols_pair = category_cols[i:i+2]
        grid_cols = st.columns(len(cols_pair))

        for gcol, col in zip(grid_cols, cols_pair):
            with gcol:
                cs = report["col_stats"][col]
                vc_dict = cs.get("value_counts", {})
                miss_color = "#f87171" if cs["missing_pct"] > 20 else (
                             "#fbbf24" if cs["missing_pct"] > 0  else "#6ee7b7")

                st.markdown(f"""
                <div class="var-card">
                    <p class="var-name">{col}</p>
                    <span class="var-type-badge badge-category">CATEGORICAL</span>
                    <div class="stat-grid" style="grid-template-columns:repeat(3,1fr)">
                        <div class="stat-cell">
                            <div class="stat-val">{cs['unique']}</div>
                            <div class="stat-key">unique</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val" style="color:{miss_color}">{cs['missing_pct']}%</div>
                            <div class="stat-key">missing</div>
                        </div>
                        <div class="stat-cell">
                            <div class="stat-val">{cs['top_pct']}%</div>
                            <div class="stat-key">top freq</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if vc_dict:
                    vc_df = pd.DataFrame({
                        "Value": list(vc_dict.keys()),
                        "Count": list(vc_dict.values())
                    }).sort_values("Count", ascending=True).tail(10)

                    fig = px.bar(
                        vc_df, x="Count", y="Value", orientation="h",
                        color="Count", color_continuous_scale="Viridis",
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(t=5, b=5, l=5, r=5), height=max(160, len(vc_df)*22),
                        xaxis=dict(color='#64748b', tickfont=dict(size=9)),
                        yaxis=dict(color='#64748b', tickfont=dict(size=9)),
                        showlegend=False, coloraxis_showscale=False
                    )
                    st.plotly_chart(fig, width='stretch')


def _render_all_vars(df, report):
    rows = []
    for col, cs in report["col_stats"].items():
        row = {
            "Column":    col,
            "Type":      cs["type"],
            "dtype":     cs["dtype"],
            "Unique":    cs["unique"],
            "Missing N": cs["missing_n"],
            "Missing %": cs["missing_pct"],
        }
        if cs["type"] == "numeric":
            row.update({
                "Mean":   cs.get("mean"),
                "Std":    cs.get("std"),
                "Min":    cs.get("min"),
                "Max":    cs.get("max"),
                "Skew":   cs.get("skew"),
            })
        rows.append(row)

    st.dataframe(
        pd.DataFrame(rows).style.background_gradient(
            subset=["Missing %"], cmap="Reds"
        ),
        width='stretch', height=500
    )


def _render_correlations(df, report):
    numeric_cols = report["numeric_cols"]
    if len(numeric_cols) < 2:
        return

    st.markdown(f"""
    <div class="eda-section-head">
        <span class="icon">🔥</span>
        <p class="title">Correlation Analysis</p>
        <span class="count">{len(numeric_cols)} numeric cols</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])

    with c1:
        corr = report["corr_matrix"]
        fig = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.columns.tolist(),
            colorscale=[[0, '#1e3a5f'], [.5, '#1e293b'], [1, '#7c3aed']],
            zmid=0, zmin=-1, zmax=1,
            text=np.round(corr.values, 2),
            texttemplate='%{text}',
            textfont=dict(size=9, color='white'),
            showscale=True,
            colorbar=dict(
                tickfont=dict(color='#94a3b8', size=10),
                title=dict(text="r", font=dict(color='#94a3b8'))
            )
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            height=max(320, len(numeric_cols) * 28),
            xaxis=dict(color='#94a3b8', tickfont=dict(size=10), tickangle=-35),
            yaxis=dict(color='#94a3b8', tickfont=dict(size=10)),
            title=dict(text="Correlation Heatmap", font=dict(color='#a5b4fc', size=13))
        )
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.markdown("**Top Correlated Pairs**")
        top = report["top_corrs"][:15]
        if top:
            for c1n, c2n, r in top:
                color = "#6ee7b7" if r > .7 else ("#fbbf24" if r > .3 else (
                        "#f87171" if r < -.3 else "#94a3b8"))
                bar_w = int(abs(r) * 100)
                sign  = "+" if r >= 0 else "−"
                st.markdown(f"""
                <div style="margin-bottom:.45rem;">
                    <div style="display:flex;justify-content:space-between;
                                color:rgba(203,213,224,.7);font-size:.73rem;margin-bottom:.2rem;">
                        <span style="font-family:'DM Mono',monospace">{c1n} × {c2n}</span>
                        <span style="color:{color};font-weight:600">{sign}{abs(r):.3f}</span>
                    </div>
                    <div style="background:rgba(255,255,255,.07);border-radius:3px;height:5px;">
                        <div style="background:{color};width:{bar_w}%;height:100%;
                                    border-radius:3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No strong correlations found.")

    # Scatter for top pair
    if top:
        c1n, c2n, r = top[0]
        with st.expander(f"🔍 Scatter: {c1n} vs {c2n}  (r={r})", expanded=False):
            scatter_df = df[[c1n, c2n]].dropna()
            fig = px.scatter(
                scatter_df, x=c1n, y=c2n,
                trendline="ols",
                color_discrete_sequence=["#6366f1"],
                title=f"r = {r}"
            )
            fig.update_traces(marker=dict(size=5, opacity=.5))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'), height=350,
                title=dict(font=dict(color='#a5b4fc'))
            )
            st.plotly_chart(fig, width='stretch')


def _render_missing_analysis(df, report):
    if report["total_missing"] == 0:
        return

    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">❓</span>
        <p class="title">Missing Value Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    miss_data = {
        col: report["col_stats"][col]["missing_pct"]
        for col in df.columns
        if report["col_stats"][col]["missing_pct"] > 0
    }

    if not miss_data:
        st.success("✅ No missing values!")
        return

    miss_df = pd.DataFrame({
        "Column":  list(miss_data.keys()),
        "Missing": list(miss_data.values())
    }).sort_values("Missing", ascending=True)

    c1, c2 = st.columns([3, 1])

    with c1:
        colors = ["#f87171" if v > 20 else "#fbbf24" if v > 5 else "#818cf8"
                  for v in miss_df["Missing"]]

        # ── FIX: Split labels into inside (wide bars) and outside (narrow bars)
        #         to prevent clipping on small bars. Use customdata for full label.
        fig = go.Figure(go.Bar(
            x=miss_df["Missing"],
            y=miss_df["Column"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,.3)', width=.5)
            ),
            # ── Use customdata to carry the text label safely
            customdata=miss_df["Missing"].apply(lambda x: f"{x:.1f}%"),
            # ── Show label outside the bar for ALL bars so nothing is clipped
            text=miss_df["Missing"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            textfont=dict(color='#e2e8f0', size=10),
            cliponaxis=False,
        ))
        fig.add_vline(x=5,  line_dash="dot", line_color="rgba(251,191,36,.5)",
                      annotation_text="5%",  annotation_font=dict(color='#fbbf24', size=10))
        fig.add_vline(x=20, line_dash="dot", line_color="rgba(239,68,68,.5)",
                      annotation_text="20%", annotation_font=dict(color='#f87171', size=10))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=45, b=10, l=10, r=70),   # ── t=45 gives title room above the plot area
            height=max(200, len(miss_df) * 30),
            xaxis=dict(
                title="% Missing",
                color='#64748b',
                tickfont=dict(size=10),
                range=[0, 115],   # ── extend axis range so outside labels are never cut off
            ),
            yaxis=dict(color='#cbd5e1', tickfont=dict(size=11)),
            title=dict(
                text="Missing Values by Column",
                font=dict(color='#a5b4fc', size=13),
                pad=dict(b=8),   # ── push title text down slightly from paper top
            )
        )
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.markdown("**Action Guide**")
        st.markdown("""
        <div style="font-size:.8rem;color:rgba(203,213,224,.7);line-height:1.8">
            <div style="color:#818cf8">🔵 &lt;5% missing</div>
            <div style="color:rgba(203,213,224,.4);font-size:.72rem;margin-bottom:.5rem">
                Safe to impute with mean/mode
            </div>
            <div style="color:#fbbf24">🟡 5–20% missing</div>
            <div style="color:rgba(203,213,224,.4);font-size:.72rem;margin-bottom:.5rem">
                Use MICE or KNN imputation
            </div>
            <div style="color:#f87171">🔴 &gt;20% missing</div>
            <div style="color:rgba(203,213,224,.4);font-size:.72rem">
                Consider dropping the column
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        st.caption("Go to Fix Data tab to handle missing values")


# ══════════════════════════════════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════════════════════════════════

def _render_export(df, report):
    st.markdown("### 📥 Export Report")
    st.caption("Download a shareable version of this analysis")

    e1, e2, e3 = st.columns(3)

    with e1:
        pdf_bytes = _build_pdf_report(df, report)
        st.download_button(
            "📑 Download PDF Report",
            data=pdf_bytes,
            file_name=f"eda_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            width='stretch',
            type="primary"
        )

    with e2:
        md_report = _build_markdown_report(df, report)
        st.download_button(
            "📄 Download as Markdown",
            data=md_report,
            file_name=f"eda_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            width='stretch',
        )

    with e3:
        csv_summary = _build_csv_summary(report)
        st.download_button(
            "📊 Download Stats as CSV",
            data=csv_summary,
            file_name=f"column_stats_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            width='stretch'
        )


def _build_markdown_report(df, report) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# EDA Report",
        f"*Generated: {now}*",
        "",
        "## Data Quality Score",
        f"**{report['quality_score']} / 100**",
        "",
        "## Dataset Overview",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Rows | {report['n_rows']:,} |",
        f"| Columns | {report['n_cols']} |",
        f"| Missing Values | {report['total_missing']:,} |",
        f"| Duplicate Rows | {report['n_dupes']:,} |",
        f"| Memory | {report['memory_mb']} MB |",
        f"| Numeric Cols | {len(report['numeric_cols'])} |",
        f"| Categorical Cols | {len(report['category_cols'])} |",
        "",
        "## Alerts",
    ]
    for level, icon, title, body in report["alerts"]:
        lines += [f"### {icon} {title}", body, ""]

    lines += ["## Column Statistics", "| Column | Type | Missing % | Unique | Mean | Std |",
              "|--------|------|-----------|--------|------|-----|"]
    for col, cs in report["col_stats"].items():
        mean = cs.get("mean", "—") or "—"
        std  = cs.get("std",  "—") or "—"
        lines.append(f"| {col} | {cs['type']} | {cs['missing_pct']}% | {cs['unique']} | {mean} | {std} |")

    if report["top_corrs"]:
        lines += ["", "## Top Correlations", "| Col A | Col B | r |", "|-------|-------|---|"]
        for c1, c2, r in report["top_corrs"][:10]:
            lines.append(f"| {c1} | {c2} | {r:.3f} |")

    return "\n".join(lines)


def _build_csv_summary(report) -> str:
    rows = []
    for col, cs in report["col_stats"].items():
        rows.append({
            "column":      col,
            "type":        cs["type"],
            "dtype":       cs["dtype"],
            "missing_n":   cs["missing_n"],
            "missing_pct": cs["missing_pct"],
            "unique":      cs["unique"],
            "mean":        cs.get("mean", ""),
            "median":      cs.get("median", ""),
            "std":         cs.get("std", ""),
            "min":         cs.get("min", ""),
            "max":         cs.get("max", ""),
            "skew":        cs.get("skew", ""),
            "kurtosis":    cs.get("kurt", ""),
        })
    return pd.DataFrame(rows).to_csv(index=False)


def _build_pdf_report(df, report) -> bytes:
    """Generate a professional PDF EDA report using reportlab."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    buf = BytesIO()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Page setup ──────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title="EDA Report",
        author="DataForge Studio"
    )

    W = A4[0] - 36*mm  # usable width

    # ── Colour palette ───────────────────────────────────────────────
    C_BG       = colors.HexColor("#0f172a")
    C_CARD     = colors.HexColor("#1e293b")
    C_INDIGO   = colors.HexColor("#6366f1")
    C_INDIGO_L = colors.HexColor("#a5b4fc")
    C_GREEN    = colors.HexColor("#6ee7b7")
    C_YELLOW   = colors.HexColor("#fbbf24")
    C_RED      = colors.HexColor("#f87171")
    C_TEXT     = colors.HexColor("#e2e8f0")
    C_MUTED    = colors.HexColor("#94a3b8")
    C_WHITE    = colors.white
    C_BORDER   = colors.HexColor("#334155")

    # ── Styles ───────────────────────────────────────────────────────
    base = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    sTitle  = S("sTitle",  fontSize=28, textColor=C_WHITE,
                fontName="Helvetica-Bold", spaceAfter=6, alignment=TA_CENTER)
    sSub    = S("sSub",    fontSize=10, textColor=C_INDIGO_L,
                fontName="Helvetica", spaceAfter=2, alignment=TA_CENTER)
    sH1     = S("sH1",     fontSize=13, textColor=C_INDIGO_L,
                fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=5)
    sH2     = S("sH2",     fontSize=10, textColor=C_TEXT,
                fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
    sBody   = S("sBody",   fontSize=9,  textColor=C_MUTED,
                fontName="Helvetica",  spaceAfter=2, leading=13)
    sSmall  = S("sSmall",  fontSize=8,  textColor=C_MUTED,
                fontName="Helvetica",  spaceAfter=1)
    sMono   = S("sMono",   fontSize=8,  textColor=C_TEXT,
                fontName="Courier",    spaceAfter=1)
    sCenter = S("sCenter", fontSize=9,  textColor=C_TEXT,
                fontName="Helvetica",  alignment=TA_CENTER)

    # Score colour
    score = report["quality_score"]
    score_color = C_GREEN if score >= 80 else (C_YELLOW if score >= 55 else C_RED)

    # ── Helper: section divider ──────────────────────────────────────
    def divider():
        return HRFlowable(width="100%", thickness=1,
                          color=C_INDIGO, spaceAfter=8, spaceBefore=2)

    # ── Helper: alert level colour ───────────────────────────────────
    def alert_color(level):
        return {
            "critical": C_RED,
            "warning":  C_YELLOW,
            "info":     C_INDIGO_L,
            "success":  C_GREEN,
        }.get(level, C_MUTED)

    # ── Helper: simple two-col key/value table ───────────────────────
    def kv_table(pairs, col_widths=None):
        if col_widths is None:
            col_widths = [W * 0.38, W * 0.62]
        data = [
            [
                Paragraph(f"<b>{k}</b>", S("kvk", fontSize=8, textColor=C_MUTED,
                                            fontName="Helvetica-Bold")),
                Paragraph(str(v), S("kvv", fontSize=8, textColor=C_TEXT,
                                    fontName="Courier"))
            ]
            for k, v in pairs
        ]
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, colors.HexColor("#1a2840")]),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
            ("LINEAFTER",     (0, 0), (0, -1), 1, colors.HexColor("#334155")),
        ]))
        return t

    # ════════════════════════════════════════════════════════════════
    # BUILD STORY
    # ════════════════════════════════════════════════════════════════
    story = []

    # ── COVER BLOCK ─────────────────────────────────────────────────
    # Title banner
    cover_data = [[Paragraph("EDA Report", sTitle)]]
    cover_table = Table(cover_data, colWidths=[W])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 22),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("BOX",           (0, 0), (-1, -1), 2, C_INDIGO),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Generated: {now}  •  DataForge Studio", sSub))
    story.append(Spacer(1, 10))

    # ── Quality score + overview metrics side-by-side ────────────────
    score_label = "Excellent" if score >= 80 else ("Good" if score >= 55 else "Needs Work")
    score_para = Paragraph(
        f'<b><font size="22" color="{score_color.hexval()}">{score}</font></b>'
        f'<br/><font size="8" color="{C_MUTED.hexval()}">/ 100 — {score_label}</font>',
        S("sc", fontName="Helvetica-Bold", alignment=TA_CENTER, leading=26)
    )

    overview_items = [
        ("Rows",         f"{report['n_rows']:,}"),
        ("Columns",      f"{report['n_cols']}  ({len(report['numeric_cols'])} numeric, "
                         f"{len(report['category_cols'])} categorical)"),
        ("Missing",      f"{report['total_missing']:,} cells"),
        ("Duplicates",   f"{report['n_dupes']:,} rows"),
        ("Memory",       f"{report['memory_mb']} MB"),
    ]

    metrics_rows = []
    for k, v in overview_items:
        metrics_rows.append([
            Paragraph(f"<b>{k}</b>", S("mk", fontSize=8, textColor=C_MUTED,
                                        fontName="Helvetica-Bold")),
            Paragraph(v, S("mv", fontSize=8, textColor=C_TEXT, fontName="Courier")),
        ])

    metrics_tbl = Table(metrics_rows, colWidths=[W * 0.28, W * 0.52])
    metrics_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, colors.HexColor("#1a2840")]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
    ]))

    # Score badge on left, metrics on right
    score_box_data = [[score_para]]
    score_box = Table(score_box_data, colWidths=[W * 0.18])
    score_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_CARD),
        ("BOX",           (0, 0), (-1, -1), 2, score_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))

    header_row = Table([[score_box, Spacer(6, 1), metrics_tbl]],
                       colWidths=[W * 0.20, 6, W * 0.80 - 6])
    header_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(header_row)
    story.append(Spacer(1, 14))

    # ── SECTION 1: ALERTS ────────────────────────────────────────────
    story.append(Paragraph("1. Alerts & Recommendations", sH1))
    story.append(divider())

    for level, icon, title, body in report["alerts"]:
        ac = alert_color(level)
        title_para = Paragraph(
            f"<b>{title}</b>",
            S("at", fontSize=9, textColor=ac, fontName="Helvetica-Bold")
        )
        body_para = Paragraph(body, sBody)
        alert_data = [[title_para, body_para]]
        at = Table(alert_data, colWidths=[W * 0.26, W * 0.74])
        at.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), C_CARD),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (0, -1), 10),
            ("LEFTPADDING",   (1, 0), (1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("LINEAFTER",     (0, 0), (0, -1), 3, ac),
            ("GRID",          (0, 0), (-1, -1), 0.2, C_BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(KeepTogether([at, Spacer(1, 5)]))

    story.append(Spacer(1, 8))

    # ── SECTION 2: COLUMN STATS TABLE ────────────────────────────────
    story.append(Paragraph("2. Column Statistics", sH1))
    story.append(divider())

    # Header row
    hdr_labels = ["Column", "Type", "Missing %", "Unique", "Mean", "Std Dev", "Skew"]
    hdr_widths = [W*0.22, W*0.09, W*0.10, W*0.08, W*0.16, W*0.16, W*0.09]

    def make_hdr(label):
        return Paragraph(f"<b>{label}</b>",
                         S(f"h_{label}", fontSize=8, textColor=C_WHITE,
                           fontName="Helvetica-Bold", alignment=TA_CENTER))

    tdata = [[make_hdr(h) for h in hdr_labels]]

    for col, cs in report["col_stats"].items():
        miss_pct = cs["missing_pct"]
        miss_color = C_RED if miss_pct > 20 else (C_YELLOW if miss_pct > 0 else C_GREEN)

        def cell(txt, color=C_TEXT, bold=False, align=TA_CENTER):
            fn = "Helvetica-Bold" if bold else "Helvetica"
            return Paragraph(
                f'<font color="{color.hexval()}">{txt}</font>',
                S("td", fontSize=8, fontName=fn, alignment=align)
            )

        tdata.append([
            Paragraph(
                f'<font color="{C_INDIGO_L.hexval()}">{col}</font>',
                S("tdc", fontSize=8, fontName="Courier", alignment=TA_LEFT)
            ),
            cell(cs["type"][:4].upper(), C_MUTED),
            cell(f"{miss_pct}%", miss_color, bold=(miss_pct > 20)),
            cell(str(cs["unique"])),
            cell(str(cs.get("mean", "—") or "—")),
            cell(str(cs.get("std",  "—") or "—")),
            cell(str(cs.get("skew", "—") or "—")),
        ])

    col_table = Table(tdata, colWidths=hdr_widths, repeatRows=1)
    col_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_INDIGO),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_CARD, colors.HexColor("#1a2840")]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("GRID",          (0, 0), (-1, -1), 0.25, C_BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(col_table)
    story.append(Spacer(1, 10))

    # ── SECTION 3: NUMERIC SUMMARIES ─────────────────────────────────
    numeric_cols = report["numeric_cols"]
    if numeric_cols:
        story.append(PageBreak())
        story.append(Paragraph("3. Numeric Column Details", sH1))
        story.append(divider())

        # Render in a 2-column grid layout for compactness
        pairs = [(numeric_cols[i], numeric_cols[i+1] if i+1 < len(numeric_cols) else None)
                 for i in range(0, len(numeric_cols), 2)]

        for left_col, right_col in pairs:
            def make_col_block(col):
                cs = report["col_stats"][col]
                skew_flag = " ⚠ High Skew" if abs(cs.get("skew", 0)) > 1 else ""
                skew_color = C_YELLOW if abs(cs.get("skew", 0)) > 1 else C_TEXT
                header = Paragraph(
                    f'<font color="{C_INDIGO_L.hexval()}"><b>{col}</b></font>'
                    f'<font color="{skew_color.hexval()}" size="7">{skew_flag}</font>',
                    S("nh", fontSize=9, fontName="Helvetica-Bold")
                )
                stat_pairs = [
                    ("Mean / Median", f"{cs.get('mean','—')} / {cs.get('median','—')}"),
                    ("Std Dev",       f"{cs.get('std','—')}"),
                    ("Min / Max",     f"{cs.get('min','—')} / {cs.get('max','—')}"),
                    ("Q25 / Q75",     f"{cs.get('q25','—')} / {cs.get('q75','—')}"),
                    ("Skew / Kurt",   f"{cs.get('skew','—')} / {cs.get('kurt','—')}"),
                    ("Zeros",         f"{cs.get('zeros',0)}"),
                    ("Missing",       f"{cs['missing_n']} ({cs['missing_pct']}%)"),
                ]
                stat_rows = []
                for k, v in stat_pairs:
                    stat_rows.append([
                        Paragraph(f"<b>{k}</b>", S("sk", fontSize=7.5, textColor=C_MUTED,
                                                    fontName="Helvetica-Bold")),
                        Paragraph(v, S("sv", fontSize=7.5, textColor=C_TEXT,
                                       fontName="Courier")),
                    ])
                inner = Table(stat_rows, colWidths=[(W/2 - 6) * 0.45, (W/2 - 6) * 0.55])
                inner.setStyle(TableStyle([
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, colors.HexColor("#1a2840")]),
                    ("TOPPADDING",    (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
                    ("GRID",          (0, 0), (-1, -1), 0.2, C_BORDER),
                ]))
                return [header, Spacer(1, 3), inner, Spacer(1, 8)]

            left_block  = make_col_block(left_col)
            right_block = make_col_block(right_col) if right_col else [Spacer(1, 1)]

            # Wrap each block in a single-cell table to constrain width
            def wrap(block, width):
                cell_data = [[item] for item in block]
                t = Table(cell_data, colWidths=[width])
                t.setStyle(TableStyle([
                    ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING",   (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
                ]))
                return t

            col_w = W / 2 - 4
            row_tbl = Table(
                [[wrap(left_block, col_w), Spacer(8, 1), wrap(right_block, col_w)]],
                colWidths=[col_w, 8, col_w]
            )
            row_tbl.setStyle(TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ]))
            story.append(row_tbl)

    # ── SECTION 4: CORRELATIONS ───────────────────────────────────────
    top_corrs = report.get("top_corrs", [])
    if top_corrs:
        story.append(PageBreak())
        story.append(Paragraph("4. Top Correlations", sH1))
        story.append(divider())

        corr_hdr_labels = ["Column A", "Column B", "r Value", "Strength"]
        corr_hdr_widths = [W*0.32, W*0.32, W*0.16, W*0.20]

        corr_hdr_row = [
            Paragraph(f"<b>{h}</b>",
                      S(f"ch{i}", fontSize=8, textColor=C_WHITE,
                        fontName="Helvetica-Bold", alignment=TA_CENTER))
            for i, h in enumerate(corr_hdr_labels)
        ]
        corr_data = [corr_hdr_row]

        for c1n, c2n, r in top_corrs[:20]:
            strength = ("Strong" if abs(r) > 0.7 else
                        "Moderate" if abs(r) > 0.3 else "Weak")
            rc = C_GREEN if r > 0.7 else (C_RED if r < -0.3 else C_YELLOW)
            corr_data.append([
                Paragraph(c1n, S("cca", fontSize=8, fontName="Courier",
                                 textColor=C_INDIGO_L)),
                Paragraph(c2n, S("ccb", fontSize=8, fontName="Courier",
                                 textColor=C_INDIGO_L)),
                Paragraph(
                    f'<font color="{rc.hexval()}"><b>{r:+.3f}</b></font>',
                    S("cr", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER)
                ),
                Paragraph(strength, S("cs", fontSize=8, textColor=C_MUTED,
                                      alignment=TA_CENTER)),
            ])

        corr_tbl = Table(corr_data, colWidths=corr_hdr_widths, repeatRows=1)
        corr_tbl.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0), C_INDIGO),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_CARD, colors.HexColor("#1a2840")]),
            ("TOPPADDING",     (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
            ("LEFTPADDING",    (0, 0), (-1, -1), 7),
            ("RIGHTPADDING",   (0, 0), (-1, -1), 7),
            ("GRID",           (0, 0), (-1, -1), 0.25, C_BORDER),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(corr_tbl)

    # ── FOOTER NOTE ───────────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_INDIGO))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated by DataForge Studio  •  {now}",
        S("footer", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)
    ))

    # ── BUILD ─────────────────────────────────────────────────────────
    doc.build(story)
    return buf.getvalue()