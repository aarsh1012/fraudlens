import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report

model = joblib.load("fraud_model.pkl")
df_full = pd.read_csv("dataset_full.csv")

X_full = df_full.drop("phishing", axis=1)
y_full = df_full["phishing"]

y_pred_full = model.predict(X_full)
print("Accuracy on full dataset:", accuracy_score(y_full, y_pred_full))
print(classification_report(y_full, y_pred_full))