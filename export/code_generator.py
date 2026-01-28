"""
Code Generation Utilities
Generate Python scripts for cleaning and AI training
"""


def generate_cleaning_code(cleaning_ops):
    """
    Generate Python code for data cleaning operations
    
    Args:
        cleaning_ops: Dictionary with cleaning operations
            - drop_duplicates: bool
            - drop_cols: list
            - impute_mean: list
            - impute_mode: list
    
    Returns:
        String containing Python code
    """
    code = """import pandas as pd
import numpy as np

df = pd.read_csv('your_data.csv')

"""
    
    if cleaning_ops.get('drop_duplicates'):
        code += "df = df.drop_duplicates()\n"
    
    if cleaning_ops.get('drop_cols'):
        code += f"df = df.drop(columns={cleaning_ops['drop_cols']})\n"
    
    for col in cleaning_ops.get('impute_mean', []):
        code += f"df['{col}'] = df['{col}'].fillna(df['{col}'].mean())\n"
    
    for col in cleaning_ops.get('impute_mode', []):
        code += f"if len(df['{col}'].mode()) > 0:\n"
        code += f"    df['{col}'] = df['{col}'].fillna(df['{col}'].mode()[0])\n"
    
    code += "\ndf.to_csv('cleaned_data.csv', index=False)\n"
    code += "print('✅ Cleaned!')"
    
    return code


def generate_ai_training_code(numeric_cols, contamination):
    """
    Generate Python code for AI model training
    
    Args:
        numeric_cols: List of numeric column names
        contamination: Contamination parameter for Isolation Forest
    
    Returns:
        String containing Python training code
    """
    return f"""import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pickle

# 1. Load Data
df = pd.read_csv('your_data.csv')
numeric_cols = {numeric_cols}

# Fill missing values for AI
X = df[numeric_cols].fillna(df[numeric_cols].mean())

# 2. Train Isolation Forest (Anomaly Detection)
print("🧠 Training AI Model...")
iso_forest = IsolationForest(
    contamination={contamination},
    random_state=42,
    n_estimators=100
)
predictions = iso_forest.fit_predict(X)

# 3. Export Model
with open('anomaly_model.pkl', 'wb') as f:
    pickle.dump(iso_forest, f)
print("✅ Model saved to anomaly_model.pkl")

# 4. Dimensionality Reduction (PCA) for Viz
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
pca = PCA(n_components=2)
coords = pca.fit_transform(X_scaled)

print(f"Detected {{list(predictions).count(-1)}} anomalies")
"""


def generate_pipeline_code(pipeline_steps):
    """
    Generate code from pipeline builder steps
    
    Args:
        pipeline_steps: List of step dictionaries with 'type' and parameters
    
    Returns:
        Python code string
    """
    code = "import pandas as pd\n\ndf = pd.read_csv('your_data.csv')\n\n"
    
    for step in pipeline_steps:
        if step['type'] == 'dedup':
            code += "df = df.drop_duplicates()\n"
        
        elif step['type'] == 'fill':
            method = step.get('method', 'mean')
            code += f"df.fillna(df.{method}(), inplace=True)\n"
        
        elif step['type'] == 'drop':
            code += f"df = df.drop(columns=['{step.get('col')}'])\n"
    
    code += "\ndf.to_csv('cleaned.csv', index=False)\n"
    return code