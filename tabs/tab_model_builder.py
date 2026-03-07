"""
Tab: Model Builder
Train, evaluate, and deploy ML models directly in the browser
Real-world algorithms with production-ready exports
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import datetime
import joblib
from io import BytesIO

# Scikit-learn imports
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve,
    mean_squared_error, mean_absolute_error, r2_score
)

# Algorithms - complete coverage from basic to advanced
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor
)
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor


# ============================================================
# ENHANCED CSS
# ============================================================
MODEL_BUILDER_CSS = """
<style>
/* Algorithm card styling */
.algo-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.algo-card:hover {
    border-color: rgba(99, 102, 241, 0.6);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);
}

.algo-card.selected {
    border-color: rgba(99, 102, 241, 0.8);
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
}

.algo-card.beginner { border-left: 3px solid #6ee7b7; }
.algo-card.intermediate { border-left: 3px solid #818cf8; }
.algo-card.advanced { border-left: 3px solid #f472b6; }

/* Step header styling */
.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
    border-radius: 12px;
    border: 1px solid rgba(99, 102, 241, 0.2);
    margin-bottom: 1.2rem;
}

.step-number {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    flex-shrink: 0;
}

/* Metric card */
.metric-highlight {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}

/* Speed badge */
.speed-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.speed-vfast { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
.speed-fast { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); }
.speed-medium { background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
.speed-slow { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }

/* Level badge */
.level-beginner { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 20px; padding: 0.15rem 0.5rem; font-size: 0.65rem; font-weight: 600; }
.level-intermediate { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 20px; padding: 0.15rem 0.5rem; font-size: 0.65rem; font-weight: 600; }
.level-advanced { background: rgba(244, 114, 182, 0.15); color: #f9a8d4; border: 1px solid rgba(244, 114, 182, 0.3); border-radius: 20px; padding: 0.15rem 0.5rem; font-size: 0.65rem; font-weight: 600; }

/* Training animation */
@keyframes pulse-train {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.training-pulse {
    animation: pulse-train 1.5s ease-in-out infinite;
}

/* Result card */
.result-excellent { border-left: 4px solid #6ee7b7; }
.result-good { border-left: 4px solid #818cf8; }
.result-poor { border-left: 4px solid #f87171; }
</style>
"""


def render_model_builder_tab(df, col_types):
    """Render the Model Builder tab"""
    
    # Inject CSS
    st.markdown(MODEL_BUILDER_CSS, unsafe_allow_html=True)
    
    st.subheader("🤖 Model Builder")
    st.caption("Train, evaluate, and deploy machine learning models — no code required")
    
    # ============================================================
    # SMART DATA SOURCE BANNER
    # ============================================================
    model_df = _get_best_data_source(df)
    data_source = _get_data_source_name()
    
    # Color-coded banner based on data source quality    
    # Check if user came back after balancing data
    # Check if user came back after balancing data
    if 'balanced_df' in st.session_state and st.session_state.balanced_df is not None:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
                    border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 1rem 1.5rem;
                    display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">✅</span>
            <div>
                <p style="color: #6ee7b7; font-weight: 600; margin: 0; font-size: 0.95rem;">Using Balanced Data</p>
                <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">
                    Great! Your data was balanced in the Imbalanced Data tab. Train again to see improved results.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif data_source == "Anomaly-Cleaned":
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
                    border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 1rem 1.5rem;
                    display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">🧹</span>
            <div>
                <p style="color: #6ee7b7; font-weight: 600; margin: 0; font-size: 0.95rem;">Using Anomaly-Cleaned Data</p>
                <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">
                    AI-detected anomalies removed. Ready for training!
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif data_source == "Feature Engineered":
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
                    border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 1rem 1.5rem;
                    display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">🎯</span>
            <div>
                <p style="color: #6ee7b7; font-weight: 600; margin: 0; font-size: 0.95rem;">Using Feature Engineered Data</p>
                <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">Optimal! Scaled & encoded features ready for ML</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif data_source in ["Skewness Corrected", "Cleaned"]:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
                    border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 1rem 1.5rem;
                    display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">✅</span>
            <div>
                <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 0.95rem;">Using {data_source} Data</p>
                <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">Good! Visit Feature Engineering tab for even better results</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(251, 191, 36, 0.05));
                    border: 1px solid rgba(251, 191, 36, 0.4); border-radius: 12px; padding: 1rem 1.5rem;
                    display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">💡</span>
            <div>
                <p style="color: #fbbf24; font-weight: 600; margin: 0; font-size: 0.95rem;">Using Original Data</p>
                <p style="color: rgba(203,213,224,0.7); margin: 0; font-size: 0.8rem;">
                    For best results: Fix Data → Skewness → Feature Engineering → Model Builder
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Block if missing values
    missing_total = model_df.isna().sum().sum()
    if missing_total > 0:
        st.error(
            f"❌ **{missing_total} missing values detected!** "
            "Please clean your data in the **Fix Data** tab first.",
            icon="⚠️"
        )
        return

    # Initialize session state
    for key in ['trained_model', 'model_metrics', 'feature_importance',
                'X_train', 'X_test', 'y_train', 'y_test',
                'label_encoders', 'feature_names', 'target_name',
                'problem_type', 'algorithm_name']:
        if key not in st.session_state:
            st.session_state[key] = None

    st.markdown("---")
    
    # ============================================================
    # STEP 1: PROBLEM TYPE & TARGET
    # ============================================================
    st.markdown("""
    <div class="step-header">
        <div class="step-number">1</div>
        <div>
            <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 1rem;">Define Your Problem</p>
            <p style="color: rgba(203,213,224,0.6); margin: 0; font-size: 0.8rem;">What are you trying to predict?</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_config1, col_config2 = st.columns([1, 1])
    
    numeric_cols = model_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = model_df.select_dtypes(include=['object', 'category']).columns.tolist()
    all_columns = model_df.columns.tolist()
    
    with col_config1:
        problem_type = st.radio(
            "Problem type:",
            ["Classification", "Regression"],
            help="**Classification:** Predict categories (spam/not spam)\n**Regression:** Predict numbers (price, temperature)",
            horizontal=True
        )
    
    with col_config2:
        if problem_type == "Classification":
            suggested = [c for c in categorical_cols if model_df[c].nunique() < 20]
            if not suggested:
                suggested = [c for c in numeric_cols if model_df[c].nunique() < 10]
        else:
            suggested = numeric_cols
        
        default_idx = all_columns.index(suggested[0]) if suggested else 0
        target_column = st.selectbox(
            "Target column (what to predict):",
            all_columns,
            index=default_idx
        )
    
    # Target analysis
    if target_column:
        n_unique = model_df[target_column].nunique()
        missing_target = model_df[target_column].isna().sum()
        
        if missing_target > 0:
            st.error(f"❌ Target column has {missing_target} missing values! Clean data first.")
            return
        
        # Target info cards
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            st.metric("Unique Values", n_unique)
        with t_col2:
            st.metric("Missing Values", missing_target)
        with t_col3:
            if problem_type == "Classification":
                vc = model_df[target_column].value_counts()
                ratio = vc.min() / vc.max()
                label = "✅ Balanced" if ratio > 0.3 else "⚠️ Imbalanced"
                st.metric("Class Balance", label)
            else:
                rng = f"{model_df[target_column].min():.1f} – {model_df[target_column].max():.1f}"
                st.metric("Value Range", rng)
        
        # Target distribution chart
        with st.expander("📊 Target Distribution", expanded=False):
            if problem_type == "Classification":
                vc_df = model_df[target_column].value_counts().reset_index()
                vc_df.columns = ['Class', 'Count']
                fig = px.bar(
                    vc_df, x='Class', y='Count',
                    title="Class Distribution",
                    color='Count',
                    color_continuous_scale='Viridis'
                )
            else:
                fig = px.histogram(
                    model_df, x=target_column,
                    title="Value Distribution", nbins=50,
                    color_discrete_sequence=['#6366f1']
                )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=280,
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, width='content')
        
        # Warnings
        if problem_type == "Classification" and n_unique > 50:
            st.warning(f"⚠️ {n_unique} classes detected. Consider grouping some categories.", icon="💡")
        if problem_type == "Regression" and n_unique < 10:
            st.warning(f"⚠️ Only {n_unique} unique values. Maybe use Classification instead?", icon="💡")
    
    st.markdown("---")
    
    # ============================================================
    # STEP 2: FEATURE SELECTION
    # ============================================================
    st.markdown("""
    <div class="step-header">
        <div class="step-number">2</div>
        <div>
            <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 1rem;">Select Features</p>
            <p style="color: rgba(203,213,224,0.6); margin: 0; font-size: 0.8rem;">Which columns should the model learn from?</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    available_features = [c for c in all_columns if c != target_column]
    default_features = [
        c for c in available_features
        if c in numeric_cols or (c in categorical_cols and model_df[c].nunique() < 10)
    ]
    
    col_feat1, col_feat2 = st.columns([3, 1])
    
    with col_feat1:
        selected_features = st.multiselect(
            "Select features (predictors):",
            available_features,
            default=default_features[:20] if len(default_features) > 20 else default_features,
            help="Categorical columns with <10 categories will be auto-encoded"
        )
    
    with col_feat2:
        if selected_features:
            n_num = len([f for f in selected_features if f in numeric_cols])
            n_cat = len([f for f in selected_features if f in categorical_cols])
            st.metric("Numeric", n_num)
            st.metric("Categorical", n_cat)
            if n_cat > 0:
                st.caption("🔄 Auto-encoded")
    
    if not selected_features:
        st.warning("⚠️ Select at least one feature to continue.")
        return
    
    # Feature correlation preview
    num_feats = [f for f in selected_features if f in numeric_cols]
    if num_feats and target_column in numeric_cols:
        with st.expander("📊 Feature Correlation with Target", expanded=False):
            corr_data = [
                {'Feature': f, 'Correlation': model_df[f].corr(model_df[target_column])}
                for f in num_feats
            ]
            corr_df = pd.DataFrame(corr_data).sort_values('Correlation', key=abs, ascending=False)
            
            fig = px.bar(
                corr_df, x='Correlation', y='Feature', orientation='h',
                color='Correlation', color_continuous_scale='RdBu_r',
                title="Pearson Correlation with Target"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'), height=max(280, len(num_feats) * 22),
                coloraxis_showscale=False, showlegend=False
            )
            st.plotly_chart(fig, width='content')
    
    st.markdown("---")
    
    # ============================================================
    # STEP 3: ALGORITHM SELECTION
    # ============================================================
    st.markdown("""
    <div class="step-header">
        <div class="step-number">3</div>
        <div>
            <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 1rem;">Choose Algorithm</p>
            <p style="color: rgba(203,213,224,0.6); margin: 0; font-size: 0.8rem;">From simple baselines to competition-winning models</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if problem_type == "Classification":
        algorithms = {
            "Random Forest 🏆": {
                "model": RandomForestClassifier,
                "params": {"n_estimators": 100, "random_state": 42, "n_jobs": -1},
                "desc": "Ensemble of decision trees. Robust, accurate, handles any data.",
                "best_for": "General purpose — your go-to algorithm",
                "speed": "Medium", "level": "Intermediate"
            },
            "Gradient Boosting ⚡": {
                "model": GradientBoostingClassifier,
                "params": {"n_estimators": 100, "random_state": 42},
                "desc": "Sequentially corrects errors. Competition-winning accuracy.",
                "best_for": "Maximum accuracy on tabular data",
                "speed": "Slow", "level": "Advanced"
            },
            "Logistic Regression 📏": {
                "model": LogisticRegression,
                "params": {"max_iter": 1000, "random_state": 42, "n_jobs": -1},
                "desc": "Simple, fast, interpretable linear model. Great baseline.",
                "best_for": "Quick baseline + when you need to explain the model",
                "speed": "Very Fast", "level": "Beginner"
            },
            "Decision Tree 🌳": {
                "model": DecisionTreeClassifier,
                "params": {"max_depth": 10, "random_state": 42},
                "desc": "Visual decision rules. You can literally see how it decides.",
                "best_for": "Interpretability, teaching, simple rules",
                "speed": "Very Fast", "level": "Beginner"
            },
            "SVM 🎯": {
                "model": SVC,
                "params": {"probability": True, "random_state": 42},
                "desc": "Finds optimal decision boundary. Great for complex patterns. ⚠️ Very slow on >5k rows.",
                "best_for": "Small datasets (<5,000 rows) with complex patterns",
                "speed": "Slow", "level": "Advanced"
            },
            "KNN 📍": {
                "model": KNeighborsClassifier,
                "params": {"n_neighbors": 5, "n_jobs": -1},
                "desc": "Classifies by similarity to neighbors. Intuitive and simple.",
                "best_for": "Small datasets, quick experiments",
                "speed": "Fast", "level": "Beginner"
            }
        }
    else:
        algorithms = {
            "Random Forest 🏆": {
                "model": RandomForestRegressor,
                "params": {"n_estimators": 100, "random_state": 42, "n_jobs": -1},
                "desc": "Ensemble of trees. Robust, accurate, handles any data.",
                "best_for": "General purpose — your go-to algorithm",
                "speed": "Medium", "level": "Intermediate"
            },
            "Gradient Boosting ⚡": {
                "model": GradientBoostingRegressor,
                "params": {"n_estimators": 100, "random_state": 42},
                "desc": "Sequentially corrects errors. Best accuracy on tabular data.",
                "best_for": "Maximum accuracy on important predictions",
                "speed": "Slow", "level": "Advanced"
            },
            "Linear Regression 📏": {
                "model": LinearRegression,
                "params": {},
                "desc": "The classic. Fits a straight line. Fast, interpretable, foundational.",
                "best_for": "Quick baseline, linear relationships",
                "speed": "Very Fast", "level": "Beginner"
            },
            "Ridge Regression 🛡️": {
                "model": Ridge,
                "params": {"alpha": 1.0},
                "desc": "Linear regression with regularization. Prevents overfitting.",
                "best_for": "Many correlated features, prevents overfitting",
                "speed": "Very Fast", "level": "Intermediate"
            },
            "Lasso Regression ✂️": {
                "model": Lasso,
                "params": {"alpha": 1.0},
                "desc": "Shrinks unimportant features to zero. Built-in feature selection.",
                "best_for": "Many features, automatic feature selection",
                "speed": "Very Fast", "level": "Intermediate"
            },
            "Decision Tree 🌳": {
                "model": DecisionTreeRegressor,
                "params": {"max_depth": 10, "random_state": 42},
                "desc": "Non-linear rules. Captures complex patterns, easy to explain.",
                "best_for": "Non-linear data, interpretability needed",
                "speed": "Very Fast", "level": "Beginner"
            }
        }
    
    # Initialize selected algorithm
    if 'selected_algorithm' not in st.session_state:
        st.session_state.selected_algorithm = list(algorithms.keys())[0]
    
    # Make sure selected algo is valid for current problem type
    if st.session_state.selected_algorithm not in algorithms:
        st.session_state.selected_algorithm = list(algorithms.keys())[0]
    
    cols = st.columns(3)
    for idx, (algo_name, info) in enumerate(algorithms.items()):
        with cols[idx % 3]:
            is_selected = st.session_state.selected_algorithm == algo_name

            level_icon = {"Beginner": "🟢", "Intermediate": "🔵", "Advanced": "🔴"}.get(info['level'], "🔵")
            speed_icon = {"Very Fast": "⚡⚡", "Fast": "⚡", "Medium": "🕐", "Slow": "🐢"}.get(info['speed'], "⚡")

            with st.container(border=True):
                prefix = "✓ " if is_selected else ""
                st.markdown(f"**{prefix}{algo_name}**")
                st.caption(info["desc"])
                st.markdown(f"{speed_icon} `{info['speed']}`&nbsp;&nbsp;{level_icon} `{info['level']}`")

            if st.button(
                "✓ Selected" if is_selected else "Select",
                key=f"algo_btn_{idx}",
                width='stretch',
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_algorithm = algo_name
                st.rerun()
    
    # Selected algo info bar
    selected_algo = st.session_state.selected_algorithm
    info = algorithms[selected_algo]

    st.info(
        f"🎯 **{selected_algo}** — Best for: {info['best_for']}  |  Speed: {info['speed']}",
        icon=None
    )
    
    st.markdown("---")
    
    # ============================================================
    # STEP 4: TRAIN / TEST SPLIT
    # ============================================================
    st.markdown("""
    <div class="step-header">
        <div class="step-number">4</div>
        <div>
            <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 1rem;">Train / Test Split</p>
            <p style="color: rgba(203,213,224,0.6); margin: 0; font-size: 0.8rem;">
                Divide your data into training and evaluation sets
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    split_col1, split_col2, split_col3 = st.columns(3)

    with split_col1:
        test_size = st.slider(
            "Test set size (%)",
            min_value=10, max_value=40, value=20, step=5,
            help="Percentage of rows held back for final evaluation. 20% is the standard."
        )

    with split_col2:
        random_seed = st.number_input(
            "Random Seed",
            min_value=0, max_value=999, value=42,
            help="Same seed = same split every run. Great for reproducibility."
        )

    with split_col3:
        use_stratify = st.checkbox(
            "Stratified Split",
            value=(problem_type == "Classification"),
            help="Keeps class ratios equal in train & test. Recommended for classification."
        )
        if use_stratify and problem_type == "Regression":
            st.caption("⚠️ Stratify only applies to classification")
            use_stratify = False

    n_total  = len(model_df.dropna(subset=selected_features + [target_column]))
    n_test   = int(n_total * test_size / 100)
    n_train  = n_total - n_test
    train_pct = 100 - test_size

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(99,102,241,.08),rgba(99,102,241,.03));
                border:1px solid rgba(99,102,241,.25);border-radius:12px;
                padding:.9rem 1.4rem;margin:.6rem 0 1rem 0;">
        <div style="display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap">
            <div style="flex:1;min-width:120px">
                <div style="color:rgba(203,213,224,.5);font-size:.72rem;letter-spacing:1px;text-transform:uppercase">Total Samples</div>
                <div style="color:#e2e8f0;font-size:1.4rem;font-weight:700">{n_total:,}</div>
            </div>
            <div style="flex:1;min-width:120px">
                <div style="color:rgba(203,213,224,.5);font-size:.72rem;letter-spacing:1px;text-transform:uppercase">🟢 Train</div>
                <div style="color:#6ee7b7;font-size:1.4rem;font-weight:700">{n_train:,} <span style="font-size:.9rem;font-weight:400">({train_pct}%)</span></div>
            </div>
            <div style="flex:1;min-width:120px">
                <div style="color:rgba(203,213,224,.5);font-size:.72rem;letter-spacing:1px;text-transform:uppercase">🔵 Test</div>
                <div style="color:#818cf8;font-size:1.4rem;font-weight:700">{n_test:,} <span style="font-size:.9rem;font-weight:400">({test_size}%)</span></div>
            </div>
            <div style="flex:2;min-width:200px">
                <div style="color:rgba(203,213,224,.5);font-size:.72rem;margin-bottom:.4rem">Split Preview</div>
                <div style="height:12px;border-radius:6px;overflow:hidden;display:flex">
                    <div style="background:#6ee7b7;width:{train_pct}%;height:100%"></div>
                    <div style="background:#818cf8;width:{test_size}%;height:100%"></div>
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:.3rem">
                    <span style="color:#6ee7b7;font-size:.7rem">Train {train_pct}%</span>
                    <span style="color:#818cf8;font-size:.7rem">Test {test_size}%</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if problem_type == "Classification" and use_stratify and target_column in model_df.columns:
        with st.expander("🔍 Class Balance Preview", expanded=False):
            vc = model_df[target_column].value_counts()
            balance_df = pd.DataFrame({
                "Class":       vc.index.astype(str),
                "Total":       vc.values,
                "≈ Train":     (vc.values * train_pct / 100).astype(int),
                "≈ Test":      (vc.values * test_size / 100).astype(int),
                "% of data":   (vc.values / len(model_df) * 100).round(1).astype(str) + "%",
            })
            st.dataframe(balance_df, width='content', hide_index=True)
            majority = vc.iloc[0] / len(model_df) * 100
            if majority > 80:
                st.warning(
                    f"⚠️ Imbalanced dataset! Majority class = {majority:.1f}%. "
                    "Consider SMOTE or class_weight='balanced'."
                )
            else:
                st.success("✅ Classes are reasonably balanced.")

    use_cv = True   # default — overridden by widget below
    with st.expander("⚙️ Advanced: Cross-Validation", expanded=False):
        use_cv = st.checkbox(
            "5-Fold Cross Validation",
            value=True,
            help="Trains 5 models on different splits. More reliable metrics, but ~5× slower."
        )
        if use_cv:
            st.info("✅ CV enabled — metrics will be mean ± std across 5 folds.")
        else:
            st.caption("⚡ Single train/test split — faster but less reliable.")

    st.markdown("---")
    
    # ============================================================
    # STEP 5: TRAIN
    # ============================================================
    st.markdown("""
    <div class="step-header">
        <div class="step-number">5</div>
        <div>
            <p style="color: #a5b4fc; font-weight: 600; margin: 0; font-size: 1rem;">Train Your Model</p>
            <p style="color: rgba(203,213,224,0.6); margin: 0; font-size: 0.8rem;">Ready to launch!</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    train_col1, train_col2, train_col3 = st.columns([2, 1, 1])
    
    with train_col1:
        train_button = st.button(
            f"🚀 TRAIN {selected_algo.upper()}",
            type="primary",
            width='stretch'
        )
    
    with train_col2:
        st.metric("Features", len(selected_features))
    
    with train_col3:
        st.metric("Samples", len(model_df))
    
    # ============================================================
    # TRAINING EXECUTION
    # ============================================================
    if train_button:
        algo_info = algorithms[selected_algo]

        # ── Guard: SVM with probability=True is O(n³) — block on large data
        if "SVM" in selected_algo and len(model_df) > 5000:
            st.error(
                f"❌ SVM is too slow for {len(model_df):,} rows (it would freeze the app). "
                "Please use Random Forest or Gradient Boosting for large datasets.",
                icon="⚠️"
            )
            st.stop()
        
        with st.status("🔄 Training your model...", expanded=True) as status:
            
            st.write("📊 Preparing data...")
            X, y, label_encoders = _prepare_data(
                model_df, selected_features, target_column,
                problem_type, categorical_cols
            )
            st.write(f"   ✓ {X.shape[0]} samples × {X.shape[1]} features")

            # ── Minimum sample guard
            if len(X) < 20:
                status.update(label="❌ Not enough data", state="error", expanded=False)
                st.error("❌ Need at least 20 rows to train a model.")
                st.stop()
            if problem_type == "Classification":
                min_class = pd.Series(y).value_counts().min()
                if min_class < 5:
                    st.warning(
                        f"⚠️ One class has only {min_class} sample(s). "
                        "Cross-validation and stratified split may fail. "
                        "Use the Imbalanced Data tab first.",
                        icon="⚠️"
                    )
                    # Disable CV and stratify automatically
                    use_cv = False
                    use_stratify = False
            
            st.write("✂️ Splitting data...")
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y,
                    test_size=test_size / 100,
                    random_state=random_seed,
                    stratify=y if use_stratify else None
                )
            except ValueError:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y,
                    test_size=test_size / 100,
                    random_state=random_seed
                )
            
            st.write(f"   ✓ Train: {len(X_train)} | Test: {len(X_test)}")
            
            st.write(f"🤖 Training {selected_algo}...")
            model = algo_info['model'](**algo_info['params'])
            try:
                model.fit(X_train, y_train)
                st.write("   ✓ Training complete!")
            except Exception as e:
                status.update(label="❌ Training failed", state="error", expanded=False)
                st.error(f"❌ Training failed: {type(e).__name__}: {str(e)}")
                st.stop()
            
            st.write("📈 Evaluating performance...")
            metrics = _evaluate_model(
                model, X_train, X_test, y_train, y_test,
                problem_type, use_cv, X, y
            )
            st.write("   ✓ Metrics calculated!")
            
            st.write("🎯 Analyzing feature importance...")
            feature_importance = _get_feature_importance(model, X.columns)
            
            st.session_state.trained_model = model
            st.session_state.model_metrics = metrics
            st.session_state.feature_importance = feature_importance
            st.session_state.X_train = X_train
            st.session_state.X_test = X_test
            st.session_state.y_train = y_train
            st.session_state.y_test = y_test
            st.session_state.label_encoders = label_encoders
            st.session_state.feature_names = X.columns.tolist()
            st.session_state.target_name = target_column
            st.session_state.problem_type = problem_type
            st.session_state.algorithm_name = selected_algo
            
            status.update(label="✅ Model trained successfully!", state="complete", expanded=False)
        
        st.balloons()
        st.rerun()
    
    # ============================================================
    # RESULTS
    # ============================================================
    if st.session_state.trained_model and st.session_state.model_metrics:
        
        st.markdown("---")

        # ── Staleness check: warn if current settings differ from trained model
        trained_target  = st.session_state.target_name
        trained_problem = st.session_state.problem_type
        trained_algo    = st.session_state.algorithm_name
        trained_feats   = set(st.session_state.feature_names or [])
        current_feats   = set(selected_features)

        is_stale = (
            trained_target  != target_column or
            trained_problem != problem_type  or
            trained_algo    != selected_algo or
            trained_feats   != current_feats
        )
        if is_stale:
            st.warning(
                "⚠️ **Settings changed since last training.** "
                "The results below are from your previous run. "
                "Click **🚀 TRAIN** again to update.",
                icon="🔄"
            )
        
        algo_display = st.session_state.algorithm_name
        prob_display = st.session_state.problem_type
        n_features = len(st.session_state.feature_names)
        target = st.session_state.target_name

        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; margin-bottom: 1.5rem;
                    background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));
                    border-radius: 16px; border: 1px solid rgba(99,102,241,0.3);">
            <p style="color: #a5b4fc; font-size: 1.4rem; font-weight: 700; margin: 0;">
                📊 Results
            </p>
            <p style="color: rgba(203,213,224,0.6); font-size: 0.85rem; margin: 0.3rem 0 0 0;">
                {prob_display} • {n_features} features
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Show algo and target safely outside HTML
        st.caption(f"**Algorithm:** {algo_display}  •  **Target:** {target}")
        
        metrics = st.session_state.model_metrics
        
        if st.session_state.problem_type == "Classification":
            _render_classification_results(metrics)
        else:
            _render_regression_results(metrics)
        
        if st.session_state.feature_importance is not None:
            st.markdown("---")
            st.markdown("### 🎯 Feature Importance")
            st.caption("Which features matter most for predictions?")
            _render_feature_importance(st.session_state.feature_importance)
        
        st.markdown("---")
        st.markdown("### 📥 Export & Deploy")
        st.caption("Take your model to production")
        
        _render_export_section(
            st.session_state.trained_model,
            st.session_state.label_encoders,
            st.session_state.feature_names,
            st.session_state.target_name,
            st.session_state.problem_type,
            st.session_state.algorithm_name,
            metrics,
            st.session_state.feature_importance
        )
        
        st.markdown("---")
        st.info(
            "💡 **Next Steps:** Download the trained model → Load it in production → "
            "Use the prediction code to score new data automatically!",
            icon="🚀"
        )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _get_best_data_source(df):
    # ✅ PRIORITY: balanced_df → engineered_df → skew_fixed_df → global_cleaned_df → anomaly_cleaned_df → df
    for key in ['balanced_df', 'engineered_df', 'skew_fixed_df', 'global_cleaned_df', 'anomaly_cleaned_df']:
        val = st.session_state.get(key)
        # Guard against empty DataFrames stored in session state
        if val is not None and isinstance(val, pd.DataFrame) and len(val) > 0:
            return val
    return df


def _get_data_source_name():
    for key, name in [
        ('balanced_df',        "Balanced (Imbalanced Handler)"),
        ('engineered_df',      "Feature Engineered"),
        ('skew_fixed_df',      "Skewness Corrected"),
        ('anomaly_cleaned_df', "Anomaly-Cleaned"),
        ('global_cleaned_df',  "Cleaned"),
    ]:
        val = st.session_state.get(key)
        if val is not None and isinstance(val, pd.DataFrame) and len(val) > 0:
            return name
    return "Original"


def _prepare_data(df, features, target, problem_type, categorical_cols):
    # Drop NaN on exactly the columns being used — guards against partial
    # missing values that slipped past the global check
    working = df[features + [target]].dropna().copy()
    X = working[features].copy()
    y = working[target].copy()
    label_encoders = {}
    
    cat_feats = [f for f in features if f in categorical_cols]
    for col in cat_feats:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le
    
    if problem_type == "Classification":
        # Encode target whether it's object OR numeric — ensures le_target.classes_
        # is always available for the confusion matrix axis labels
        le_target = LabelEncoder()
        y = le_target.fit_transform(y.astype(str))
        label_encoders['target'] = le_target
    
    return X, y, label_encoders


def _evaluate_model(model, X_train, X_test, y_train, y_test,
                    problem_type, use_cv, X_full, y_full):
    metrics = {}
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    if problem_type == "Classification":
        metrics['train_accuracy'] = accuracy_score(y_train, y_train_pred)
        metrics['test_accuracy'] = accuracy_score(y_test, y_test_pred)
        metrics['precision'] = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
        metrics['recall'] = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
        metrics['f1'] = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
        metrics['confusion_matrix'] = confusion_matrix(y_test, y_test_pred)
        metrics['classification_report'] = classification_report(
            y_test, y_test_pred, output_dict=True, zero_division=0
        )
        
        if len(np.unique(y_test)) == 2 and hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)[:, 1]
            metrics['roc_auc'] = roc_auc_score(y_test, y_proba)
            metrics['fpr'], metrics['tpr'], _ = roc_curve(y_test, y_proba)
    
    else:
        metrics['train_r2'] = r2_score(y_train, y_train_pred)
        metrics['test_r2'] = r2_score(y_test, y_test_pred)
        metrics['mse'] = mean_squared_error(y_test, y_test_pred)
        metrics['rmse'] = np.sqrt(metrics['mse'])
        metrics['mae'] = mean_absolute_error(y_test, y_test_pred)
        # Convert to numpy so plotly scatter always gets a clean array
        metrics['y_test'] = np.array(y_test)
        metrics['y_test_pred'] = np.array(y_test_pred)
    
    if use_cv:
        from sklearn.base import clone
        scoring = 'accuracy' if problem_type == "Classification" else 'r2'
        cv_kwargs = dict(scoring=scoring, n_jobs=-1)
        
        if problem_type == "Classification":
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        else:
            cv = 5
        
        try:
            # Clone gives a fresh unfitted estimator — correct practice
            cv_scores = cross_val_score(clone(model), X_full, y_full, cv=cv, **cv_kwargs)
            metrics['cv_mean'] = cv_scores.mean()
            metrics['cv_std'] = cv_scores.std()
            metrics['cv_scores'] = cv_scores
        except Exception:
            pass
    
    return metrics


def _get_feature_importance(model, feature_names):
    if hasattr(model, 'feature_importances_'):
        return pd.DataFrame({
            'Feature': feature_names,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False).reset_index(drop=True)
    
    elif hasattr(model, 'coef_'):
        coef = model.coef_
        if len(coef.shape) > 1:
            coef = np.abs(coef).mean(axis=0)
        else:
            coef = np.abs(coef)
        
        return pd.DataFrame({
            'Feature': feature_names,
            'Importance': coef
        }).sort_values('Importance', ascending=False).reset_index(drop=True)
    
    return None


def _render_classification_results(metrics):
    acc = metrics['test_accuracy']
    quality = "🟢 Excellent" if acc >= 0.9 else ("🟡 Good" if acc >= 0.75 else "🔴 Needs Work")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 0.6rem; margin-bottom: 1rem;
                background: rgba(99,102,241,0.08); border-radius: 8px;">
        <span style="color: rgba(203,213,224,0.6); font-size: 0.85rem;">Model Quality: </span>
        <span style="color: #e2e8f0; font-weight: 600;">{quality}</span>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4, m5 = st.columns(5)
    
    overfitting = metrics['test_accuracy'] - metrics['train_accuracy']
    with m1:
        st.metric("Accuracy", f"{acc:.1%}",
                 delta=f"{overfitting:+.1%} vs train",
                 delta_color="inverse" if overfitting < -0.1 else "normal")
    with m2:
        st.metric("Precision", f"{metrics['precision']:.1%}")
    with m3:
        st.metric("Recall", f"{metrics['recall']:.1%}")
    with m4:
        st.metric("F1-Score", f"{metrics['f1']:.1%}")
    with m5:
        if 'cv_mean' in metrics:
            st.metric("CV Score", f"{metrics['cv_mean']:.1%}",
                     delta=f"±{metrics['cv_std']:.1%}")
        elif 'roc_auc' in metrics:
            st.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
    
    if overfitting < -0.15:
        st.warning("⚠️ **Overfitting detected!** Train accuracy much higher than test. Try reducing model complexity.", icon="🔍")
    # Check for poor performance + possible class imbalance
    if acc < 0.55:  # Less than 55% accuracy
        st.info(
            "💡 **Low accuracy detected!** This might be due to class imbalance. "
            "Visit the **⚖️ Imbalanced Data** tab to balance your classes with SMOTE/ADASYN, "
            "then retrain your model here.",
            icon="🎯"
        )

    # Check for poor performance + possible class imbalance
    if acc < 0.55:  # Less than 55% accuracy
        st.info(
            "💡 **Low accuracy detected!** This might be due to class imbalance. "
            "Visit the **⚖️ Imbalanced Data** tab to balance your classes with SMOTE/ADASYN, "
            "then retrain your model here.",
            icon="🎯"
        )
    
    viz_t1, viz_t2, viz_t3 = st.tabs(["🟦 Confusion Matrix", "📈 ROC Curve", "📋 Full Report"])
    
    with viz_t1:
        cm = metrics['confusion_matrix']
        cm_norm = cm.astype(float) / cm.sum(axis=1)[:, np.newaxis]

        # Use real class names if target was label-encoded
        le_target = (st.session_state.get('label_encoders') or {}).get('target')
        if le_target is not None:
            class_labels = [str(c) for c in le_target.classes_]
        else:
            class_labels = [str(i) for i in range(len(cm))]
        
        fig = go.Figure(data=go.Heatmap(
            z=cm_norm,
            x=[f"Pred: {c}" for c in class_labels],
            y=[f"Actual: {c}" for c in class_labels],
            colorscale=[[0, 'rgba(99,102,241,0.1)'], [1, 'rgba(99,102,241,0.9)']],
            text=cm,
            texttemplate='<b>%{text}</b>',
            textfont={"size": 18, "color": "white"},
            showscale=False
        ))
        fig.update_layout(
            title=dict(text="Confusion Matrix", font=dict(color='#a5b4fc')),
            xaxis=dict(title="Predicted", color='#cbd5e1'),
            yaxis=dict(title="Actual", color='#cbd5e1'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'), height=450
        )
        st.plotly_chart(fig, width='content')
    
    with viz_t2:
        if 'roc_auc' in metrics:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=metrics['fpr'], y=metrics['tpr'], mode='lines',
                name=f'ROC (AUC = {metrics["roc_auc"]:.3f})',
                line=dict(color='#6366f1', width=3),
                fill='tozeroy', fillcolor='rgba(99,102,241,0.1)'
            ))
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode='lines', name='Random (AUC = 0.5)',
                line=dict(color='#64748b', width=2, dash='dash')
            ))
            fig.update_layout(
                title=dict(text="ROC Curve", font=dict(color='#a5b4fc')),
                xaxis=dict(title="False Positive Rate", color='#cbd5e1', range=[0, 1]),
                yaxis=dict(title="True Positive Rate", color='#cbd5e1', range=[0, 1]),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'), height=450
            )
            st.plotly_chart(fig, width='content')
        else:
            st.info("ℹ️ ROC Curve is only available for binary classification problems.")
    
    with viz_t3:
        report = metrics['classification_report']
        report_df = pd.DataFrame(report).transpose()
        st.dataframe(
            report_df.style.format(precision=3)
            .background_gradient(subset=['precision', 'recall', 'f1-score'], cmap='RdYlGn'),
            width='stretch'
        )


def _render_regression_results(metrics):
    r2 = metrics['test_r2']
    quality = "🟢 Excellent" if r2 >= 0.85 else ("🟡 Good" if r2 >= 0.65 else "🔴 Needs Work")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 0.6rem; margin-bottom: 1rem;
                background: rgba(99,102,241,0.08); border-radius: 8px;">
        <span style="color: rgba(203,213,224,0.6); font-size: 0.85rem;">Model Quality: </span>
        <span style="color: #e2e8f0; font-weight: 600;">{quality}</span>
    </div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4, m5 = st.columns(5)
    
    overfitting = metrics['test_r2'] - metrics['train_r2']
    with m1:
        st.metric("R² Score", f"{r2:.3f}",
                 delta=f"{overfitting:+.3f} vs train",
                 delta_color="inverse" if overfitting < -0.15 else "normal")
    with m2:
        st.metric("RMSE", f"{metrics['rmse']:.3f}")
    with m3:
        st.metric("MAE", f"{metrics['mae']:.3f}")
    with m4:
        st.metric("MSE", f"{metrics['mse']:.3f}")
    with m5:
        if 'cv_mean' in metrics:
            st.metric("CV R²", f"{metrics['cv_mean']:.3f}",
                     delta=f"±{metrics['cv_std']:.3f}")
    
    if overfitting < -0.15:
        st.warning("⚠️ **Overfitting detected!** Train R² much higher than test. Try simpler model.", icon="🔍")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=metrics['y_test'], y=metrics['y_test_pred'],
        mode='markers', name='Predictions',
        marker=dict(size=7, opacity=0.7, color=metrics['y_test_pred'],
                    colorscale='Viridis', showscale=False)
    ))
    
    min_v = min(metrics['y_test'].min(), metrics['y_test_pred'].min())
    max_v = max(metrics['y_test'].max(), metrics['y_test_pred'].max())
    
    fig.add_trace(go.Scatter(
        x=[min_v, max_v], y=[min_v, max_v],
        mode='lines', name='Perfect Prediction',
        line=dict(color='#f87171', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=dict(text="Predicted vs Actual", font=dict(color='#a5b4fc')),
        xaxis=dict(title="Actual Values", color='#cbd5e1'),
        yaxis=dict(title="Predicted Values", color='#cbd5e1'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'), height=450,
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1, font=dict(color='#e2e8f0'),
                    bgcolor='rgba(0,0,0,0)'),
        showlegend=True
    )
    st.plotly_chart(fig, width='content')
    
    residuals = metrics['y_test'] - metrics['y_test_pred']
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=metrics['y_test_pred'], y=residuals, mode='markers',
        marker=dict(size=6, color='#6366f1', opacity=0.5), name='Residuals'
    ))
    fig2.add_hline(y=0, line_dash="dash", line_color="#f87171", line_width=2)
    fig2.update_layout(
        title=dict(text="Residuals Plot (should scatter randomly around 0)", font=dict(color='#a5b4fc')),
        xaxis=dict(title="Predicted Values", color='#cbd5e1'),
        yaxis=dict(title="Residuals", color='#cbd5e1'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'), height=350
    )
    st.plotly_chart(fig2, width='content')


def _render_feature_importance(importance_df):
    top = importance_df.head(20)
    
    fig = px.bar(
        top, y='Feature', x='Importance', orientation='h',
        color='Importance', color_continuous_scale='Viridis',
        title="Top Feature Importances"
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'), height=max(350, len(top) * 25),
        showlegend=False, coloraxis_showscale=False,
        title=dict(font=dict(color='#a5b4fc'))
    )
    st.plotly_chart(fig, width='content')
    
    with st.expander("📋 Full Feature Importance Table"):
        st.dataframe(
            importance_df.style.background_gradient(subset=['Importance'], cmap='Greens'),
            width='stretch', height=350
        )


def _render_export_section(model, label_encoders, feature_names, target_name,
                           problem_type, algorithm_name, metrics, feature_importance=None):
    
    d1, d2, d3 = st.columns(3)
    
    with d1:
        buf = BytesIO()
        joblib.dump(model, buf)
        buf.seek(0)
        clean_name = (algorithm_name
                      .replace(' ', '_')
                      .replace('🏆','').replace('⚡','').replace('📏','')
                      .replace('🌳','').replace('🎯','').replace('📍','')
                      .replace('🛡️','').replace('✂️','').strip('_'))
        st.download_button(
            "📦 Download Trained Model (.pkl)",
            data=buf,
            file_name=f"model_{clean_name}.pkl",
            mime="application/octet-stream",
            width='stretch',
            type="primary"
        )
        st.caption("Load with: `joblib.load('model.pkl')`")
    
    with d2:
        pred_code = _generate_prediction_code(
            feature_names, target_name, problem_type, algorithm_name
        )
        st.download_button(
            "💻 Download Prediction Code",
            data=pred_code,
            file_name="make_predictions.py",
            mime="text/plain",
            width='stretch'
        )
        st.caption("Ready-to-run Python script")
    
    with d3:
        # ── PDF report instead of plain-text ──
        pdf_bytes = _build_model_pdf_report(
            metrics, problem_type, algorithm_name,
            feature_names, target_name, feature_importance
        )
        st.download_button(
            "📑 Download PDF Report",
            data=pdf_bytes,
            file_name=f"model_report_{clean_name}.pdf",
            mime="application/pdf",
            width='stretch'
        )
        st.caption("Full performance report as PDF")
    
    with st.expander("👁️ Preview Prediction Code"):
        st.code(pred_code, language='python')
        st.markdown("**Usage:** `python make_predictions.py new_data.csv`")


# ============================================================
# PDF REPORT — same dark theme as EDA report
# ============================================================

def _build_model_pdf_report(metrics, problem_type, algorithm_name,
                             feature_names, target_name, feature_importance=None):
    """Build a professional dark-themed PDF model performance report."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buf = BytesIO()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title="Model Performance Report",
        author="DataForge Studio"
    )
    W = A4[0] - 36*mm

    # ── Palette (matches EDA report) ────────────────────────────────
    C_BG     = colors.HexColor("#0f172a")
    C_CARD   = colors.HexColor("#1e293b")
    C_CARD2  = colors.HexColor("#1a2840")
    C_INDIGO = colors.HexColor("#6366f1")
    C_IND_L  = colors.HexColor("#a5b4fc")
    C_GREEN  = colors.HexColor("#6ee7b7")
    C_YELLOW = colors.HexColor("#fbbf24")
    C_RED    = colors.HexColor("#f87171")
    C_TEXT   = colors.HexColor("#e2e8f0")
    C_MUTED  = colors.HexColor("#94a3b8")
    C_BORDER = colors.HexColor("#334155")

    # ── Style helpers ────────────────────────────────────────────────
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    sTitle  = S("T",  fontSize=26, textColor=colors.white,
                fontName="Helvetica-Bold", alignment=TA_CENTER)
    sSub    = S("Su", fontSize=10, textColor=C_IND_L,
                fontName="Helvetica", alignment=TA_CENTER)
    sH1     = S("H1", fontSize=13, textColor=C_IND_L,
                fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=5)
    sH2     = S("H2", fontSize=10, textColor=C_TEXT,
                fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
    sBody   = S("Bo", fontSize=9,  textColor=C_MUTED,
                fontName="Helvetica", spaceAfter=2, leading=13)
    sMono   = S("Mo", fontSize=8,  textColor=C_TEXT,
                fontName="Courier", spaceAfter=1)

    def divider():
        return HRFlowable(width="100%", thickness=1,
                          color=C_INDIGO, spaceAfter=8, spaceBefore=2)

    # ── Determine quality label & color ─────────────────────────────
    if problem_type == "Classification":
        main_score = metrics['test_accuracy']
        quality = "Excellent" if main_score >= 0.9 else ("Good" if main_score >= 0.75 else "Needs Work")
        score_color = C_GREEN if main_score >= 0.9 else (C_YELLOW if main_score >= 0.75 else C_RED)
        main_label = f"Test Accuracy: {main_score:.1%}"
    else:
        main_score = metrics['test_r2']
        quality = "Excellent" if main_score >= 0.85 else ("Good" if main_score >= 0.65 else "Needs Work")
        score_color = C_GREEN if main_score >= 0.85 else (C_YELLOW if main_score >= 0.65 else C_RED)
        main_label = f"Test R2: {main_score:.4f}"

    # ── kv table helper ─────────────────────────────────────────────
    def kv_table(pairs, col_widths=None):
        if col_widths is None:
            col_widths = [W * 0.38, W * 0.62]
        data = [
            [
                Paragraph(f"<b>{k}</b>", S("kk", fontSize=8, textColor=C_MUTED,
                                            fontName="Helvetica-Bold")),
                Paragraph(str(v), S("kv", fontSize=8, textColor=C_TEXT, fontName="Courier"))
            ]
            for k, v in pairs
        ]
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, C_CARD2]),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
        ]))
        return t

    # ════════════════════════════════════════════════════════════════
    # STORY
    # ════════════════════════════════════════════════════════════════
    story = []

    # ── COVER ───────────────────────────────────────────────────────
    cover = Table([[Paragraph("Model Performance Report", sTitle)]], colWidths=[W])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 22),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
        ("BOX",           (0, 0), (-1, -1), 2, C_INDIGO),
    ]))
    story.append(cover)
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Generated: {now}  •  DataForge Studio", sSub))
    story.append(Spacer(1, 12))

    # ── SCORE BADGE + OVERVIEW ───────────────────────────────────────
    score_para = Paragraph(
        f'<b><font size="20" color="{score_color.hexval()}">{main_score:.1%}</font></b>'
        f'<br/><font size="8" color="{C_MUTED.hexval()}">{quality}</font>',
        S("sc", fontName="Helvetica-Bold", alignment=TA_CENTER, leading=24)
    )
    score_box = Table([[score_para]], colWidths=[W * 0.20])
    score_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_CARD),
        ("BOX",           (0, 0), (-1, -1), 2, score_color),
        ("TOPPADDING",    (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))

    overview_pairs = [
        ("Algorithm",    algorithm_name),
        ("Problem Type", problem_type),
        ("Target",       target_name),
        ("Features",     str(len(feature_names))),
    ]
    ov_rows = [
        [
            Paragraph(f"<b>{k}</b>", S("ok", fontSize=8, textColor=C_MUTED,
                                        fontName="Helvetica-Bold")),
            Paragraph(v, S("ov", fontSize=8, textColor=C_TEXT, fontName="Courier")),
        ]
        for k, v in overview_pairs
    ]
    ov_tbl = Table(ov_rows, colWidths=[W * 0.28, W * 0.52])
    ov_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, C_CARD2]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
    ]))

    header_row = Table([[score_box, Spacer(6, 1), ov_tbl]],
                       colWidths=[W * 0.20, 6, W * 0.80 - 6])
    header_row.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    story.append(header_row)
    story.append(Spacer(1, 14))

    # ── SECTION 1: PERFORMANCE METRICS ──────────────────────────────
    story.append(Paragraph("1. Performance Metrics", sH1))
    story.append(divider())

    if problem_type == "Classification":
        overfitting = metrics['test_accuracy'] - metrics['train_accuracy']
        of_color = C_RED if overfitting < -0.15 else C_GREEN
        pairs = [
            ("Train Accuracy",  f"{metrics['train_accuracy']:.4f}  ({metrics['train_accuracy']:.1%})"),
            ("Test Accuracy",   f"{metrics['test_accuracy']:.4f}  ({metrics['test_accuracy']:.1%})"),
            ("Overfitting Gap", f"{overfitting:+.4f}"),
            ("Precision",       f"{metrics['precision']:.4f}"),
            ("Recall",          f"{metrics['recall']:.4f}"),
            ("F1-Score",        f"{metrics['f1']:.4f}"),
        ]
        if 'roc_auc' in metrics:
            pairs.append(("ROC-AUC", f"{metrics['roc_auc']:.4f}"))
    else:
        overfitting = metrics['test_r2'] - metrics['train_r2']
        of_color = C_RED if overfitting < -0.15 else C_GREEN
        pairs = [
            ("Train R2",        f"{metrics['train_r2']:.4f}"),
            ("Test R2",         f"{metrics['test_r2']:.4f}"),
            ("Overfitting Gap", f"{overfitting:+.4f}"),
            ("RMSE",            f"{metrics['rmse']:.4f}"),
            ("MAE",             f"{metrics['mae']:.4f}"),
            ("MSE",             f"{metrics['mse']:.4f}"),
        ]

    story.append(kv_table(pairs))
    story.append(Spacer(1, 8))

    # Overfitting note
    if overfitting < -0.15:
        warn_data = [[Paragraph(
            "<b>Overfitting Warning:</b> Train score is significantly higher than test. "
            "Consider reducing model complexity or adding regularization.",
            S("wn", fontSize=8, textColor=C_YELLOW, fontName="Helvetica")
        )]]
        warn_tbl = Table(warn_data, colWidths=[W])
        warn_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#2d2000")),
            ("BOX",           (0, 0), (-1, -1), 1.5, C_YELLOW),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(warn_tbl)
        story.append(Spacer(1, 8))

    # ── SECTION 2: CROSS-VALIDATION ──────────────────────────────────
    if 'cv_mean' in metrics:
        story.append(Paragraph("2. Cross-Validation (5-Fold)", sH1))
        story.append(divider())

        metric_name = "Accuracy" if problem_type == "Classification" else "R2"
        cv_color = C_GREEN if metrics['cv_mean'] >= 0.8 else (C_YELLOW if metrics['cv_mean'] >= 0.65 else C_RED)
        fold_str = "  |  ".join(f"Fold {i+1}: {s:.4f}" for i, s in enumerate(metrics['cv_scores']))

        cv_pairs = [
            (f"Mean {metric_name}", f"{metrics['cv_mean']:.4f}"),
            ("Std Deviation",       f"{metrics['cv_std']:.4f}  (±{metrics['cv_std']:.4f})"),
            ("All Folds",           fold_str),
        ]
        story.append(kv_table(cv_pairs))
        story.append(Spacer(1, 8))

    # ── SECTION 3: CONFUSION MATRIX (classification) ─────────────────
    if problem_type == "Classification" and 'confusion_matrix' in metrics:
        story.append(Paragraph("3. Confusion Matrix", sH1))
        story.append(divider())

        cm = metrics['confusion_matrix']
        n = len(cm)

        # Header row
        hdr = [Paragraph("", sMono)] + [
            Paragraph(f"<b>Pred {i}</b>",
                      S(f"ch{i}", fontSize=8, textColor=colors.white,
                        fontName="Helvetica-Bold", alignment=TA_CENTER))
            for i in range(n)
        ]
        cm_data = [hdr]
        for i, row in enumerate(cm):
            cm_data.append(
                [Paragraph(f"<b>Actual {i}</b>",
                           S(f"cr{i}", fontSize=8, textColor=C_IND_L,
                             fontName="Helvetica-Bold"))]
                + [
                    Paragraph(
                        f'<font color="{"#6ee7b7" if i == j else "#f87171"}"><b>{val}</b></font>',
                        S(f"cv{i}{j}", fontSize=9, fontName="Helvetica-Bold",
                          alignment=TA_CENTER)
                    )
                    for j, val in enumerate(row)
                ]
            )

        col_w = [W * 0.18] + [(W * 0.82 / n)] * n
        cm_tbl = Table(cm_data, colWidths=col_w)
        cm_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_INDIGO),
            ("BACKGROUND",    (0, 0), (0, -1), C_CARD),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_CARD, C_CARD2]),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("GRID",          (0, 0), (-1, -1), 0.3, C_BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(cm_tbl)
        story.append(Spacer(1, 8))

    # ── SECTION 4: FEATURE IMPORTANCE ────────────────────────────────
    if feature_importance is not None and len(feature_importance) > 0:
        sec_num = "4" if problem_type == "Classification" else "3"
        story.append(PageBreak())
        story.append(Paragraph(f"{sec_num}. Feature Importance", sH1))
        story.append(divider())

        top_fi = feature_importance.head(20)
        max_imp = top_fi['Importance'].max()

        fi_hdr = [
            Paragraph("<b>Rank</b>", S("fh0", fontSize=8, textColor=colors.white,
                                        fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>Feature</b>", S("fh1", fontSize=8, textColor=colors.white,
                                           fontName="Helvetica-Bold")),
            Paragraph("<b>Importance</b>", S("fh2", fontSize=8, textColor=colors.white,
                                              fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>Relative Bar</b>", S("fh3", fontSize=8, textColor=colors.white,
                                                fontName="Helvetica-Bold")),
        ]
        fi_data = [fi_hdr]

        for rank, (_, row) in enumerate(top_fi.iterrows(), 1):
            imp = row['Importance']
            rel = imp / max_imp if max_imp > 0 else 0
            bar_w_pt = int(rel * 100)
            # Color: top 3 green, rest indigo
            bar_color = C_GREEN if rank <= 3 else C_INDIGO

            fi_data.append([
                Paragraph(f"#{rank}", S(f"fr{rank}", fontSize=8, textColor=C_MUTED,
                                         fontName="Helvetica", alignment=TA_CENTER)),
                Paragraph(row['Feature'], S(f"fn{rank}", fontSize=8, textColor=C_IND_L,
                                             fontName="Courier")),
                Paragraph(f"{imp:.4f}", S(f"fi{rank}", fontSize=8, textColor=C_TEXT,
                                           fontName="Courier", alignment=TA_CENTER)),
                Paragraph(
                    f'<font color="{bar_color.hexval()}">{"█" * max(1, bar_w_pt // 8)}</font>',
                    S(f"fb{rank}", fontSize=9, fontName="Helvetica")
                ),
            ])

        fi_col_w = [W*0.08, W*0.35, W*0.17, W*0.40]
        fi_tbl = Table(fi_data, colWidths=fi_col_w, repeatRows=1)
        fi_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_INDIGO),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_CARD, C_CARD2]),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("GRID",          (0, 0), (-1, -1), 0.25, C_BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(fi_tbl)

    # ── SECTION 5: FEATURE LIST ───────────────────────────────────────
    last_sec = "5" if problem_type == "Classification" else "4"
    story.append(Spacer(1, 14))
    story.append(Paragraph(f"{last_sec}. Feature List", sH1))
    story.append(divider())

    # Render in 3 columns
    cols_per_row = 3
    feat_rows = []
    chunk = [feature_names[i:i+cols_per_row] for i in range(0, len(feature_names), cols_per_row)]
    for group in chunk:
        while len(group) < cols_per_row:
            group.append("")
        feat_rows.append([
            Paragraph(f'<font color="{C_IND_L.hexval()}">{f}</font>' if f else "",
                      S("fl", fontSize=8, fontName="Courier"))
            for f in group
        ])

    if feat_rows:
        feat_tbl = Table(feat_rows, colWidths=[W / cols_per_row] * cols_per_row)
        feat_tbl.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_CARD, C_CARD2]),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("GRID",          (0, 0), (-1, -1), 0.2, C_BORDER),
        ]))
        story.append(feat_tbl)

    # ── FOOTER ────────────────────────────────────────────────────────
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_INDIGO))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated by DataForge Studio  •  {now}",
        S("ft", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()


# ============================================================
# PREDICTION CODE GENERATOR (unchanged)
# ============================================================

def _generate_prediction_code(features, target, problem_type, algo_name):
    clean_name = algo_name.replace(' ', '_').replace('🏆','').replace('⚡','').strip('_')
    is_clf = problem_type == "Classification"
    
    prob_lines = (
        "\n    probabilities = model.predict_proba(X)\n"
        "    results_df['confidence'] = probabilities.max(axis=1)\n"
    ) if is_clf else ""
    
    return f"""# Prediction Script — {algo_name}
# Auto-generated by Smart CSV AI Studio
# Problem: {problem_type} | Target: {target}

import pandas as pd
import numpy as np
import joblib
import sys


def load_model(model_path='model_{clean_name}.pkl'):
    return joblib.load(model_path)


def prepare_data(df):
    features = {features}
    
    # Validate columns exist
    missing = [f for f in features if f not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {{missing}}")
    
    return df[features].copy()


def predict(model, df):
    X = prepare_data(df)
    predictions = model.predict(X)
    results_df = df.copy()
    results_df['prediction'] = predictions
    {prob_lines}
    return results_df


def main():
    if len(sys.argv) < 2:
        print("Usage: python make_predictions.py <input.csv>")
        sys.exit(1)
    
    print(f"Loading model...")
    model = load_model()
    
    print(f"Loading data from {{sys.argv[1]}}...")
    df = pd.read_csv(sys.argv[1])
    
    print(f"Making predictions...")
    results = predict(model, df)
    
    output = sys.argv[1].replace('.csv', '_predictions.csv')
    results.to_csv(output, index=False)
    
    print(f"✅ {{len(results)}} predictions saved to {{output}}")


if __name__ == "__main__":
    main()
"""