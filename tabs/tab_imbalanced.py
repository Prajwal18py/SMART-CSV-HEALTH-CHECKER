"""
Tab: Imbalanced Data Handler
Detect and fix class imbalance using SMOTE, ADASYN, Undersampling, and Class Weights
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.export_utils import smart_download_button, get_format_label

IMBALANCED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&display=swap');

.eda-section-head {
    display: flex; align-items: center; gap: .7rem;
    margin: 1.6rem 0 1rem 0; padding-bottom: .5rem;
    border-bottom: 1px solid rgba(99,102,241,.2);
}
.eda-section-head .icon { font-size:1.3rem; }
.eda-section-head .title {
    font-family: 'Syne', sans-serif; font-size: 1.05rem;
    font-weight: 700; color: #c7d2fe; margin: 0;
}
.eda-section-head .count {
    margin-left: auto; background: rgba(99,102,241,.2);
    color: #a5b4fc; border-radius: 20px; padding: .15rem .6rem;
    font-size: .72rem; font-weight: 600; font-family: 'DM Mono', monospace;
}

.technique-card {
    background: linear-gradient(135deg, rgba(30,41,59,.9), rgba(15,23,42,.9));
    border: 1px solid rgba(99,102,241,.2); border-radius: 14px;
    padding: 1.2rem; margin-bottom: .8rem;
    transition: border-color .25s, box-shadow .25s, transform .2s;
}
.technique-card:hover {
    border-color: rgba(99,102,241,.5);
    box-shadow: 0 4px 20px rgba(99,102,241,.15);
    transform: translateY(-2px);
}
.technique-card.selected {
    border-color: rgba(99,102,241,.8);
    background: linear-gradient(135deg, rgba(99,102,241,.15), rgba(139,92,246,.1));
    box-shadow: 0 0 20px rgba(99,102,241,.25);
}

.imbalance-badge {
    display: inline-block; padding: .2rem .7rem; border-radius: 20px;
    font-size: .72rem; font-weight: 600; letter-spacing: .5px;
}
.badge-severe { background: rgba(239,68,68,.2); color: #fca5a5; border: 1px solid rgba(239,68,68,.3); }
.badge-moderate { background: rgba(251,191,36,.2); color: #fbbf24; border: 1px solid rgba(251,191,36,.3); }
.badge-mild { background: rgba(99,102,241,.2); color: #a5b4fc; border: 1px solid rgba(99,102,241,.3); }
.badge-balanced { background: rgba(16,185,129,.2); color: #6ee7b7; border: 1px solid rgba(16,185,129,.3); }
</style>
"""


def render_imbalanced_tab(df, col_types, settings=None):
    """Render the Imbalanced Data Handler tab"""
    settings = settings or {}
    _imbalance_threshold = float(settings.get('imbalance_threshold', 0.3))
    _smote_k_default    = int(settings.get('smote_k_neighbors', 5))
    st.markdown(IMBALANCED_CSS, unsafe_allow_html=True)
    st.subheader("⚖️ Imbalanced Data Handler")
    st.caption("Detect class imbalance and fix it with SMOTE, ADASYN, Undersampling, or Class Weights")

    # Use best available data
    # Use best available data (but NOT balanced_df — we're creating it!)
    working_df = df
    for key in ['engineered_df', 'skew_fixed_df', 'global_cleaned_df', 'anomaly_cleaned_df']:
        val = st.session_state.get(key)
        if val is not None and isinstance(val, pd.DataFrame) and len(val) > 0:
            working_df = val
            break

    fmt_label = get_format_label()
    # ── Workflow banner if coming from Model Builder ────────────────
    if st.session_state.get('trained_model') is not None:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
                    border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 1rem 1.5rem;
                    display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">🔄</span>
            <div>
                <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 0.95rem;">Coming from Model Builder?</p>
                <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">
                    Fix your class imbalance below, then return to <strong>Model Builder</strong> to retrain with balanced data!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── STEP 1: Select target column ────────────────────────────────
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🎯</span>
        <p class="title">Step 1: Select Target Column</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggest likely classification targets
    categorical_cols = col_types.get('categorical', [])
    numeric_low_card = [c for c in col_types.get('numeric', [])
                        if working_df[c].nunique() <= 10]
    candidate_targets = categorical_cols + numeric_low_card

    all_cols = working_df.columns.tolist()
    default_idx = all_cols.index(candidate_targets[0]) if candidate_targets else 0

    target_col = st.selectbox(
        "Select the target/label column (the one you want to classify):",
        all_cols,
        index=default_idx,
        help="This should be your classification target — the column with class labels"
    )

    if target_col not in working_df.columns:
        st.warning("Select a valid target column.")
        return

    # Drop missing in target
    analysis_df = working_df.dropna(subset=[target_col]).copy()
    vc = analysis_df[target_col].value_counts()
    n_classes = len(vc)

    if n_classes < 2:
        st.error("❌ Target column needs at least 2 unique classes.")
        return
    if n_classes > 20:
        st.warning(f"⚠️ {n_classes} unique values detected — this looks like a regression target, not classification.")
        return

    # ── IMBALANCE ANALYSIS ───────────────────────────────────────────
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">📊</span>
        <p class="title">Step 2: Imbalance Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    majority_count = vc.iloc[0]
    minority_count = vc.iloc[-1]
    ratio = minority_count / majority_count
    imbalance_ratio = majority_count / minority_count

    # ✅ WIRED: sidebar 'Imbalance Alert Threshold' controls severity boundary
    # Threshold = minority/majority ratio below which imbalance is flagged
    if ratio >= 0.8:
        severity = "balanced"
        badge_class = "badge-balanced"
        severity_label = "✅ Balanced"
        recommendation = "Your data is well balanced. No action needed, but you can still apply techniques for experimentation."
    elif ratio >= 0.5:
        severity = "mild"
        badge_class = "badge-mild"
        severity_label = "🔵 Mildly Imbalanced"
        recommendation = "Mild imbalance. Class Weights or light SMOTE recommended."
    elif ratio >= 0.2:
        severity = "moderate"
        badge_class = "badge-moderate"
        severity_label = "⚠️ Moderately Imbalanced"
        recommendation = "Significant imbalance. SMOTE or ADASYN strongly recommended."
    else:
        severity = "severe"
        badge_class = "badge-severe"
        severity_label = "🚨 Severely Imbalanced"
        recommendation = "Severe imbalance. SMOTE/ADASYN essential — model will be heavily biased without fixing this."

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Samples", f"{len(analysis_df):,}")
    with m2:
        st.metric("Classes", n_classes)
    with m3:
        st.metric("Imbalance Ratio", f"{imbalance_ratio:.1f}:1")
    with m4:
        st.markdown(f"""
        <div style="padding:.8rem;background:rgba(30,41,59,.8);border-radius:10px;text-align:center">
            <div style="color:rgba(203,213,224,.5);font-size:.72rem;margin-bottom:.3rem">SEVERITY</div>
            <span class="imbalance-badge {badge_class}">{severity_label}</span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"💡 **Recommendation:** {recommendation}")

    # Class distribution chart + table side by side
    c1, c2 = st.columns([2, 1])

    with c1:
        colors = px.colors.sequential.Viridis[::-1][:len(vc)]
        fig = go.Figure(go.Bar(
            x=[str(v) for v in vc.index],
            y=vc.values,
            marker=dict(
                color=vc.values,
                colorscale='Viridis',
                showscale=False,
                line=dict(color='rgba(0,0,0,.3)', width=.5)
            ),
            text=[f"{v:,}<br>({v/len(analysis_df)*100:.1f}%)" for v in vc.values],
            textposition='outside',
            textfont=dict(color='#e2e8f0', size=10),
        ))
        fig.update_layout(
            title=dict(text=f"Class Distribution — {target_col}",
                      font=dict(color='#a5b4fc', size=13)),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(color='#94a3b8', title="Class"),
            yaxis=dict(color='#94a3b8', title="Count"),
            font=dict(color='#e2e8f0'), height=300,
            margin=dict(t=40, b=20, l=10, r=10)
        )
        st.plotly_chart(fig, width='stretch')

    with c2:
        dist_df = pd.DataFrame({
            'Class':   vc.index.astype(str),
            'Count':   vc.values,
            '%':       (vc.values / len(analysis_df) * 100).round(1)
        })
        st.dataframe(dist_df, hide_index=True, height=300)

    st.markdown("---")

    # ── STEP 3: Choose technique ─────────────────────────────────────
    st.markdown("""
    <div class="eda-section-head">
        <span class="icon">🧪</span>
        <p class="title">Step 3: Choose Balancing Technique</p>
    </div>
    """, unsafe_allow_html=True)

    techniques = {
        "SMOTE": {
            "icon": "🔬",
            "full": "Synthetic Minority Over-sampling Technique",
            "desc": "Creates synthetic samples for minority classes by interpolating between existing minority samples. Best general-purpose technique.",
            "best_for": "Most classification problems. Works great when minority class > 100 samples.",
            "pros": "No data loss • Creates realistic samples • Well proven",
            "cons": "Can create noisy samples • Slow on large datasets",
            "badge": "⭐ Most Popular",
            "recommended": severity in ["moderate", "severe"]
        },
        "ADASYN": {
            "icon": "🧠",
            "full": "Adaptive Synthetic Sampling",
            "desc": "Like SMOTE but focuses on harder-to-learn minority samples near the decision boundary. Smarter distribution.",
            "best_for": "Complex decision boundaries. When SMOTE isn't giving good results.",
            "pros": "Focuses on hard samples • Better boundary handling",
            "cons": "Can amplify noise • More complex",
            "badge": "🎯 Advanced",
            "recommended": severity == "severe"
        },
        "Random Undersampling": {
            "icon": "✂️",
            "full": "Random Majority Undersampling",
            "desc": "Randomly removes samples from the majority class until classes are balanced. Simple and fast.",
            "best_for": "Very large datasets where you can afford to lose data.",
            "pros": "Fast • No synthetic data • Reduces training time",
            "cons": "Loses potentially useful data",
            "badge": "⚡ Fast",
            "recommended": severity in ["mild", "moderate"] and len(analysis_df) > 10000
        },
        "Class Weights": {
            "icon": "⚖️",
            "full": "Class Weight Balancing",
            "desc": "Doesn't change the data. Instead adds a 'class_weight' column that ML models use to penalize mistakes on minority classes more heavily.",
            "best_for": "When you can't modify the data (time series, ordered data). Use directly in sklearn with class_weight='balanced'.",
            "pros": "No data modification • Works with any sklearn model",
            "cons": "Must be manually passed to model",
            "badge": "🛡️ Safe",
            "recommended": severity == "mild"
        }
    }

    selected_technique = st.session_state.get('imb_technique', 'SMOTE')

    cols = st.columns(2)
    for idx, (name, info) in enumerate(techniques.items()):
        with cols[idx % 2]:
            is_selected = selected_technique == name
            is_recommended = info['recommended']
            border_color = "rgba(99,102,241,.8)" if is_selected else ("rgba(16,185,129,.4)" if is_recommended else "rgba(99,102,241,.2)")
            bg = "rgba(99,102,241,.12)" if is_selected else "rgba(30,41,59,.8)"

            # ── FIX: Build HTML parts as plain Python strings first,
            #         then join — avoids apostrophe/quote escaping issues
            #         that caused raw HTML to leak into the card body.
            recommended_html = (
                '<div style="color:#6ee7b7;font-size:.7rem;margin-bottom:.3rem">'
                '✅ Recommended for your data</div>'
            ) if is_recommended else ""

            card_html = (
                f'<div style="background:{bg};border:2px solid {border_color};border-radius:14px;'
                f'padding:1.1rem;margin-bottom:.5rem;min-height:160px">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem">'
                f'<span style="color:#e2e8f0;font-weight:700;font-size:.95rem">{info["icon"]} {name}</span>'
                f'<span style="background:rgba(99,102,241,.2);color:#a5b4fc;border-radius:20px;'
                f'padding:.1rem .5rem;font-size:.65rem">{info["badge"]}</span>'
                f'</div>'
                f'{recommended_html}'
                f'<p style="color:rgba(203,213,224,.7);font-size:.78rem;margin:0 0 .5rem 0;line-height:1.4">{info["desc"]}</p>'
                f'<div style="font-size:.7rem;color:#94a3b8">'
                f'<b style="color:#a5b4fc">Best for:</b> {info["best_for"]}'
                f'</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            btn_label = "✓ Selected" if is_selected else "Select"
            if st.button(btn_label, key=f"imb_btn_{idx}",
                        type="primary" if is_selected else "secondary",
                        width='stretch'):
                st.session_state['imb_technique'] = name
                st.rerun()

    st.markdown("---")

    # ── STEP 4: Configure & Apply ────────────────────────────────────
    selected_technique = st.session_state.get('imb_technique', 'SMOTE')

    st.markdown(f"""
    <div class="eda-section-head">
        <span class="icon">⚙️</span>
        <p class="title">Step 4: Configure & Apply — {selected_technique}</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature columns — only numeric (required for SMOTE/ADASYN interpolation math)
    # Categorical cols are excluded from interpolation but re-attached afterward
    feature_cols = [c for c in working_df.columns
                   if c != target_col and working_df[c].dtype in [np.float64, np.int64, float, int]]
    
    # Non-numeric columns to preserve (re-attached after balancing)
    other_cols = [c for c in working_df.columns
                 if c != target_col and c not in feature_cols]
    
    if other_cols:
        st.info(
            f"ℹ️ **{len(other_cols)} categorical column(s)** will be excluded from SMOTE interpolation "
            f"but preserved in the output by sampling: `{', '.join(other_cols[:4])}`"
            + (f" +{len(other_cols)-4} more" if len(other_cols) > 4 else ""),
            icon="📋"
        )

    if selected_technique in ["SMOTE", "ADASYN"] and len(feature_cols) == 0:
        st.error("❌ SMOTE/ADASYN require numeric feature columns. Use Class Weights or Undersampling instead.")
        return

    cfg1, cfg2 = st.columns(2)

    with cfg1:
        if selected_technique in ["SMOTE", "ADASYN"]:
            # ✅ WIRED: sidebar 'SMOTE K Neighbors' sets the default value
            k_neighbors = st.slider(
                "K Neighbors",
                min_value=1, max_value=10, value=_smote_k_default,
                help="Nearest neighbors for synthetic sample generation. Default set by sidebar ⚙️ SMOTE K Neighbors."
            )
            target_strategy = st.selectbox(
                "Sampling Strategy",
                ["auto (balance all classes)", "minority (only smallest)", "not majority (all except largest)"],
                help="Which classes to oversample"
            )
        elif selected_technique == "Random Undersampling":
            target_strategy = st.selectbox(
                "Sampling Strategy",
                ["auto (balance all classes)", "majority (only largest class)", "not minority (all except smallest)"],
            )
            random_seed = st.number_input("Random Seed", 0, 999, 42)
        else:  # Class Weights
            st.info("Class Weights doesn't modify data. It generates a weight mapping you pass to your ML model.")

    with cfg2:
        if selected_technique in ["SMOTE", "ADASYN", "Random Undersampling"]:
            random_seed = st.number_input("Random Seed", 0, 999, 42,
                                          key="rs_imb")

            # Preview what the result will look like
            n_minority = vc.iloc[-1]
            n_majority = vc.iloc[0]

            if selected_technique in ["SMOTE", "ADASYN"]:
                new_total = n_majority * n_classes
                new_minority = n_majority
                delta = new_total - len(analysis_df)
                st.metric("Rows After Balancing", f"~{new_total:,}", delta=f"+{delta:,} synthetic")
            else:
                new_total = n_minority * n_classes
                delta = new_total - len(analysis_df)
                st.metric("Rows After Balancing", f"~{new_total:,}", delta=f"{delta:,} removed")

    # ── APPLY ────────────────────────────────────────────────────────
    apply_col, _ = st.columns([1, 2])
    with apply_col:
        apply_btn = st.button(
            f"🚀 Apply {selected_technique}",
            type="primary",
            width='stretch'
        )

    if apply_btn:
        with st.status(f"⚖️ Applying {selected_technique}...", expanded=True) as status:

            try:
                X = analysis_df[feature_cols].copy()
                y = analysis_df[target_col].copy()

                # Encode target if categorical
                from sklearn.preprocessing import LabelEncoder
                le = None
                if y.dtype == object or str(y.dtype) == 'category':
                    le = LabelEncoder()
                    y_encoded = le.fit_transform(y)
                else:
                    y_encoded = y.values

                if selected_technique == "SMOTE":
                    st.write("🔬 Running SMOTE...")
                    X_res, y_res = _smote(X.values, y_encoded, k=k_neighbors,
                                          random_state=random_seed)

                elif selected_technique == "ADASYN":
                    st.write("🧠 Running ADASYN...")
                    X_res, y_res = _adasyn(X.values, y_encoded, k=k_neighbors,
                                           random_state=random_seed)

                elif selected_technique == "Random Undersampling":
                    st.write("✂️ Running Random Undersampling...")
                    X_res, y_res = _random_undersample(X.values, y_encoded,
                                                        random_state=random_seed)

                else:  # Class Weights
                    st.write("⚖️ Computing class weights...")
                    weights = _compute_class_weights(y_encoded)
                    st.session_state['class_weights'] = {
                        (le.inverse_transform([k])[0] if le else k): v
                        for k, v in weights.items()
                    }
                    status.update(label="✅ Class weights computed!", state="complete", expanded=False)

                    # Show weights
                    w_df = pd.DataFrame([
                        {'Class': (le.inverse_transform([k])[0] if le else k),
                         'Weight': round(v, 4),
                         'Interpretation': '↑ Penalized more' if v > 1 else '↓ Penalized less'}
                        for k, v in weights.items()
                    ])
                    st.dataframe(w_df, hide_index=True)

                    st.code(
                        f"# Use in sklearn:\n"
                        f"class_weights = {dict(st.session_state['class_weights'])}\n"
                        f"model = RandomForestClassifier(class_weight=class_weights)\n"
                        f"# OR simply:\n"
                        f"model = RandomForestClassifier(class_weight='balanced')",
                        language='python'
                    )
                    return

                # Decode target back
                if le is not None:
                    y_final = le.inverse_transform(y_res.astype(int))
                else:
                    y_final = y_res

                # Build result DataFrame
                result_df = pd.DataFrame(X_res, columns=feature_cols)
                result_df[target_col] = y_final

                # ✅ Re-attach non-numeric columns (mode-filled for synthetic rows)
                if other_cols and selected_technique in ["SMOTE", "ADASYN"]:
                    n_original = len(analysis_df)
                    n_synthetic = len(result_df) - n_original
                    for col in other_cols:
                        original_vals = analysis_df[col].reset_index(drop=True)
                        if n_synthetic > 0:
                            # Fill synthetic rows with mode of their class
                            mode_val = analysis_df[col].mode().iloc[0] if not analysis_df[col].mode().empty else None
                            synthetic_vals = pd.Series([mode_val] * n_synthetic)
                            result_df[col] = pd.concat([original_vals, synthetic_vals], ignore_index=True)
                        else:
                            result_df[col] = original_vals
                elif other_cols and selected_technique == "Random Undersampling":
                    # For undersampling, just map back using index
                    result_df[other_cols] = analysis_df[other_cols].iloc[:len(result_df)].reset_index(drop=True)


                st.session_state['balanced_df'] = result_df
                status.update(label="✅ Balancing complete!", state="complete", expanded=False)

                # Results
                st.markdown("---")
                new_vc = pd.Series(y_final).value_counts()

                r1, r2, r3 = st.columns(3)
                with r1:
                    st.metric("Original Rows", f"{len(analysis_df):,}")
                with r2:
                    st.metric("New Rows", f"{len(result_df):,}",
                              delta=f"{len(result_df)-len(analysis_df):+,}")
                with r3:
                    new_ratio = new_vc.min() / new_vc.max()
                    st.metric("New Balance Ratio", f"{new_ratio:.2f}",
                              delta="↑ More balanced" if new_ratio > ratio else "")

                # Before/After chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Before',
                    x=[str(c) for c in vc.index],
                    y=vc.values,
                    marker_color='rgba(99,102,241,.6)',
                ))
                fig.add_trace(go.Bar(
                    name='After',
                    x=[str(c) for c in new_vc.index],
                    y=new_vc.values,
                    marker_color='rgba(16,185,129,.7)',
                ))
                fig.update_layout(
                    barmode='group',
                    title=dict(text="Before vs After Balancing",
                              font=dict(color='#a5b4fc')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=300,
                    legend=dict(bgcolor='rgba(0,0,0,0)'),
                    xaxis=dict(color='#94a3b8'),
                    yaxis=dict(color='#94a3b8'),
                )
                st.plotly_chart(fig, width='stretch')

                with st.expander("👀 Preview Balanced Data"):
                    st.dataframe(result_df.head(50), height=300)

                smart_download_button(
                    result_df,
                    label=f"⬇️ Download Balanced {fmt_label}",
                    suffix=f"balanced_{selected_technique.lower().replace(' ','_')}",
                    key="dl_balanced",
                    button_width='stretch'
                )

                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
                            border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 14px; padding: 1.2rem 1.5rem;
                            margin-top: 1rem; display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2rem;">✅</span>
                    <div>
                        <p style="color: #6ee7b7; font-weight: 700; margin: 0; font-size: 1.05rem;">
                            Balancing Complete!
                        </p>
                        <p style="color: rgba(203,213,224,0.75); margin: 0.3rem 0 0 0; font-size: 0.88rem;">
                            🔄 Return to the <strong>🤖 Model Builder</strong> tab to retrain your model with balanced data.
                            You should see significantly improved accuracy!
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.caption("Try selecting different feature columns or switching to Class Weights.")


# ══════════════════════════════════════════════════════════════════════
# BALANCING ALGORITHMS (pure numpy — no imblearn dependency)
# ══════════════════════════════════════════════════════════════════════

def _smote(X, y, k=5, random_state=42):
    """Pure numpy SMOTE implementation."""
    rng = np.random.RandomState(random_state)
    classes, counts = np.unique(y, return_counts=True)
    majority_count = counts.max()

    X_res = list(X)
    y_res = list(y)

    for cls, cnt in zip(classes, counts):
        if cnt >= majority_count:
            continue

        X_cls = X[y == cls]
        n_needed = majority_count - cnt

        for _ in range(n_needed):
            # Pick a random sample from minority class
            idx = rng.randint(0, len(X_cls))
            sample = X_cls[idx]

            # Find k nearest neighbors
            dists = np.sqrt(((X_cls - sample) ** 2).sum(axis=1))
            nn_indices = np.argsort(dists)[1:k+1]  # exclude self

            if len(nn_indices) == 0:
                X_res.append(sample)
            else:
                # Pick random neighbor and interpolate
                nn_idx = rng.choice(nn_indices)
                neighbor = X_cls[nn_idx]
                alpha = rng.random()
                synthetic = sample + alpha * (neighbor - sample)
                X_res.append(synthetic)

            y_res.append(cls)

    return np.array(X_res), np.array(y_res)


def _adasyn(X, y, k=5, random_state=42):
    """Pure numpy ADASYN — adaptive oversampling."""
    rng = np.random.RandomState(random_state)
    classes, counts = np.unique(y, return_counts=True)
    majority_count = counts.max()

    X_res = list(X)
    y_res = list(y)

    for cls, cnt in zip(classes, counts):
        if cnt >= majority_count:
            continue

        X_cls = X[y == cls]
        X_maj = X[y != cls]
        n_needed = majority_count - cnt

        # Compute density ratio — how hard each minority sample is to learn
        ratios = []
        for sample in X_cls:
            all_dists = np.sqrt(((X - sample) ** 2).sum(axis=1))
            nn_indices = np.argsort(all_dists)[1:k+1]
            nn_labels = y[nn_indices]
            ratio = np.sum(nn_labels != cls) / k
            ratios.append(ratio)

        ratios = np.array(ratios)
        if ratios.sum() == 0:
            ratios = np.ones(len(ratios))
        ratios = ratios / ratios.sum()  # normalize

        # Generate samples proportional to difficulty
        n_per_sample = (ratios * n_needed).astype(int)
        remainder = n_needed - n_per_sample.sum()
        n_per_sample[np.argmax(ratios)] += remainder

        for i, sample in enumerate(X_cls):
            dists = np.sqrt(((X_cls - sample) ** 2).sum(axis=1))
            nn_indices = np.argsort(dists)[1:k+1]

            for _ in range(n_per_sample[i]):
                if len(nn_indices) == 0:
                    X_res.append(sample)
                else:
                    nn_idx = rng.choice(nn_indices)
                    neighbor = X_cls[nn_idx]
                    alpha = rng.random()
                    synthetic = sample + alpha * (neighbor - sample)
                    X_res.append(synthetic)
                y_res.append(cls)

    return np.array(X_res), np.array(y_res)


def _random_undersample(X, y, random_state=42):
    """Random majority class undersampling."""
    rng = np.random.RandomState(random_state)
    classes, counts = np.unique(y, return_counts=True)
    minority_count = counts.min()

    X_res = []
    y_res = []

    for cls in classes:
        X_cls = X[y == cls]
        if len(X_cls) > minority_count:
            indices = rng.choice(len(X_cls), minority_count, replace=False)
            X_res.append(X_cls[indices])
        else:
            X_res.append(X_cls)
        y_res.append(np.full(min(len(X_cls), minority_count), cls))

    return np.vstack(X_res), np.concatenate(y_res)


def _compute_class_weights(y):
    """Compute balanced class weights (sklearn-style)."""
    classes, counts = np.unique(y, return_counts=True)
    n_samples = len(y)
    n_classes = len(classes)
    weights = {}
    for cls, cnt in zip(classes, counts):
        weights[int(cls)] = n_samples / (n_classes * cnt)
    return weights