# import pandas as pd
# import numpy as np
# import xgboost as xgb
# import pickle

# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# from sklearn.preprocessing import StandardScaler

# # 🧰 1. Load your data
# df = pd.read_csv('output.csv')

# # 👓 2. Define feature and target columns
# target_col = 'class'
# feature_cols = [c for c in df.columns if c != target_col]

# X = df[feature_cols].copy()
# y = df[target_col].copy()

# # 📊 3. Identify categorical and numeric columns
# cat_cols = [
#     'source', 'browser', 'sex',
#     'country_name', 'signup_day_name', 'purchase_day_name'
# ]
# num_cols = [
#     'n_device_occur', 'signup_month', 'signup_day',
#     'purchase_month', 'purchase_day',
#     'purchase_over_time', 'age'
# ]

# # Convert categoricals to category dtype for XGBoost
# for col in cat_cols:
#     X[col] = X[col].astype('category')

# # 🛠 4. Handle infinities by replacing +inf/−inf with the max/min finite values
# for col in num_cols:
#     vals = X[col]
#     finite = vals[np.isfinite(vals)]
#     if not finite.empty:
#         finite_min, finite_max = finite.min(), finite.max()
#         X[col] = vals.replace(np.inf, finite_max).replace(-np.inf, finite_min)
#     else:
#         # if the column is all infinite or empty, just fill with zero
#         X[col] = vals.replace([np.inf, -np.inf], 0)

# # 🔢 5. Optionally clip extreme outliers (uncomment to use)
# # X[num_cols] = X[num_cols].clip(upper=1e6, lower=-1e6)

# # 🔢 6. Scale numeric features
# scaler = StandardScaler()
# X[num_cols] = scaler.fit_transform(X[num_cols])

# # 🚧 7. Train/test split (stratified)
# X_train, X_test, y_train, y_test = train_test_split(
#     X, y,
#     test_size=0.2,
#     random_state=42,
#     stratify=y
# )

# # 🧪 8. XGBoost classifier
# model = xgb.XGBClassifier(
#     objective='binary:logistic',
#     tree_method='hist',
#     enable_categorical=True,
#     use_label_encoder=False,
#     eval_metric='logloss'
# )

# # 🔧 9. Train
# model.fit(
#     X_train, y_train,
#     eval_set=[(X_test, y_test)],
#     verbose=True
# )

# # 💾 10. Save model
# with open('transaction_model.pkl', 'wb') as f:
#     pickle.dump(model, f)

# # 📈 11. Evaluate
# y_pred = model.predict(X_test)
# acc  = accuracy_score(y_test, y_pred)
# prec = precision_score(y_test, y_pred)
# rec  = recall_score(y_test, y_pred)
# f1   = f1_score(y_test, y_pred)

# print("=== Model Evaluation Metrics ===")
# print(f"Accuracy:  {acc:.4f}")
# print(f"Precision: {prec:.4f}")
# print(f"Recall:    {rec:.4f}")
# print(f"F1-score:  {f1:.4f}")

import pandas as pd
import numpy as np
import xgboost as xgb
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

# 🧰 1. Load your data
df = pd.read_csv('data/transaction_data.csv')

# 👓 2. Define feature and target columns
target_col = 'class'
feature_cols = [c for c in df.columns if c != target_col]

X = df[feature_cols].copy()
y = df[target_col].copy()

# 📊 3. Identify categorical and numeric columns
cat_cols = [
    'source', 'browser', 'sex',
    'country_name', 'signup_day_name', 'purchase_day_name'
]
num_cols = [
    'n_device_occur', 'signup_month', 'signup_day',
    'purchase_month', 'purchase_day',
    'purchase_over_time', 'age'
]

# Convert categoricals to category dtype for XGBoost
for col in cat_cols:
    X[col] = X[col].astype('category')

# 🛠 4. Handle infinities by replacing +inf/−inf with the max/min finite values
for col in num_cols:
    vals = X[col]
    finite = vals[np.isfinite(vals)]
    if not finite.empty:
        finite_min, finite_max = finite.min(), finite.max()
        X[col] = vals.replace(np.inf, finite_max).replace(-np.inf, finite_min)
    else:
        # if the column is all infinite or empty, just fill with zero
        X[col] = vals.replace([np.inf, -np.inf], 0)

# 🔢 5. Optionally clip extreme outliers (uncomment to use)
# X[num_cols] = X[num_cols].clip(upper=1e6, lower=-1e6)

# 🔢 6. Scale numeric features
scaler = StandardScaler()
X[num_cols] = scaler.fit_transform(X[num_cols])

# 💾 7. Save the fitted scaler
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# 🚧 8. Train/test split (stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 🧪 9. XGBoost classifier
model = xgb.XGBClassifier(
    objective='binary:logistic',
    tree_method='hist',
    enable_categorical=True,
    use_label_encoder=False,
    eval_metric='logloss'
)

# 🔧 10. Train
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=True
)

# 💾 11. Save model
with open('transaction_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# 📈 12. Evaluate
y_pred = model.predict(X_test)
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec  = recall_score(y_test, y_pred)
f1   = f1_score(y_test, y_pred)

print("=== Model Evaluation Metrics ===")
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall:    {rec:.4f}")
print(f"F1-score:  {f1:.4f}")
