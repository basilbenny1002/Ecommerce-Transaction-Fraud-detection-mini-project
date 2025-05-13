import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import numpy as np
df = pd.read_csv('onlinefraud.csv')
#print(df.head())
#Remove unnecessary columns
df = pd.get_dummies(df, columns=['type'], drop_first=True)
df = df.drop(columns=['nameOrig', 'nameDest'])

df = df.drop(columns=['step'],)

# Separate features (X) and target variable (y)
X = df.drop('isFraud', axis=1)
y = df['isFraud']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(type(X_test))
with open('X_test.txt', 'w') as f:
    f.write(df.head().to_string())

# raise NotImplementedError
# Initialize XGBoost classifier
xgb_model = xgb.XGBClassifier(objective='binary:logistic',  # For binary classification
                             use_label_encoder=False, # Suppress the warning about deprecated parameter
                             eval_metric='logloss', tree_method='gpu_hist',  enable_categorical=True)  # Specify evaluation metric for binary classification

# Train the model
xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

#Saving the mdoel in .pkl format
with open('model.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)

# Make predictions
y_pred = xgb_model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

#Printing out the accuracy values
print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-score: {f1}")