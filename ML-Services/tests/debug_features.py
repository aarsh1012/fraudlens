from predict import extract_all_features
import json

test_url = "https://www.paypal.com"
features = extract_all_features(test_url)

for k, v in features.items():
    print(k, ":", v)