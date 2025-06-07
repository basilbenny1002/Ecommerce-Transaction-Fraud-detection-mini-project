import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('Fraudulent_online_shops_dataset.csv')

# Fill only TrustPilot score NaNs with -1
if 'TrustPilot score' in df.columns:
    df['TrustPilot score'] = df['TrustPilot score'].fillna(-1)

# Drop rows with other missing values (excluding TrustPilot score)
df = df.dropna()

# Drop unnecessary string-based columns
df = df.drop(columns=[
    "Online shop URL",
    "SSL certificate expire date",
    "Issuer organization",
    "SSL certificate issuer"
])

# Convert 'Label' to numeric: 'fraudulent' = 1, 'legitimate' = 0
df['Label'] = df['Label'].map({'fraudulent': 1, 'legitimate': 0})

# Convert date column to UNIX timestamp
if 'Domain registration date' in df.columns:
    df['Domain registration date'] = pd.to_datetime(df['Domain registration date'], errors='coerce')
    df['Domain registration date'] = df['Domain registration date'].astype(np.int64) // 10**9
    df['Domain registration date'] = df['Domain registration date'].fillna(-1)

# Separate features and labels
X = df.drop('Label', axis=1)
y = df['Label']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# XGBoost setup
xgb_model = xgb.XGBClassifier(
    objective='binary:logistic',
    use_label_encoder=False,
    eval_metric='logloss',
    tree_method='hist',
    enable_categorical=True,
    device='cuda'  # Use 'cpu' if no GPU
)

# Train
xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)

# Evaluate
y_pred = xgb_model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall: {recall_score(y_test, y_pred):.4f}")
print(f"F1-score: {f1_score(y_test, y_pred):.4f}")
