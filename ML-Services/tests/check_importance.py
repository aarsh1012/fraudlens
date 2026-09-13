import joblib
import pandas as pd

model = joblib.load("fraud_model_v2.pkl")
features = joblib.load("selected_features.pkl")

importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(importance.head(15))
