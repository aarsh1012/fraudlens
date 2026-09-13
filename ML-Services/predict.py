import joblib
import pandas as pd
from urllib.parse import urlparse
from feature_extractor import extract_url_features
from network_features import get_domain_age_features, check_ssl_certificate, count_redirects, get_response_time, extract_extra_features


def extract_all_features(url):
    parsed = urlparse(url)
    domain = parsed.netloc

    features = extract_url_features(url)

    domain_age_features = get_domain_age_features(domain)
    features.update(domain_age_features)

    features['tls_ssl_certificate'] = check_ssl_certificate(domain)
    features['qty_redirects'] = count_redirects(url)
    features['time_response'] = get_response_time(url)

    # NEW - add the extra features
    extra_features = extract_extra_features(url, domain)
    features.update(extra_features)

    return features


TRUSTED_DOMAINS = [
    "google.com", "paypal.com", "microsoft.com", "amazon.com",
    "apple.com", "facebook.com", "netflix.com", "github.com"
]


def predict_url(url):
    parsed_domain = urlparse(url).netloc.replace("www.", "")

    if any(parsed_domain == trusted or parsed_domain.endswith("." + trusted) for trusted in TRUSTED_DOMAINS):
        return {"url": url, "prediction": "LEGITIMATE", "confidence": 99.0, "note": "Trusted domain whitelist"}

    model = joblib.load("fraud_model_v2.pkl")
    expected_columns = joblib.load("selected_features.pkl")

    features = extract_all_features(url)

    # Build a row matching only the selected features, in the right order
    row = {col: features.get(col, 0) for col in expected_columns}
    input_df = pd.DataFrame([row])

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0]

    result = {
        "url": url,
        "prediction": "PHISHING" if prediction == 1 else "LEGITIMATE",
        "confidence": round(max(probability) * 100, 2)
    }
    return result


if __name__ == "__main__":
    test_url = "https://www.google.com"
    print(predict_url(test_url))