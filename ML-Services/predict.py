import joblib
import pandas as pd
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from feature_extractor import extract_url_features
from network_features import get_domain_age_features, check_ssl_certificate, count_redirects, get_response_time, extract_extra_features, get_dns_features, check_safe_browsing


def extract_all_features(url):
    parsed = urlparse(url)
    domain = parsed.netloc

    # Fast, local, string-based - no need to parallelize these
    features = extract_url_features(url)
    features.update(extract_extra_features(url, domain))

    # Run all network-dependent checks AT THE SAME TIME instead of one after another
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_domain_age = executor.submit(get_domain_age_features, domain)
        future_ssl = executor.submit(check_ssl_certificate, domain)
        future_redirects = executor.submit(count_redirects, url)
        future_response_time = executor.submit(get_response_time, url)
        future_dns = executor.submit(get_dns_features, domain)
        future_safe_browsing = executor.submit(check_safe_browsing, url)

        # .result() waits for each one to finish and grabs its return value
        features.update(future_domain_age.result())
        features['tls_ssl_certificate'] = future_ssl.result()
        features['qty_redirects'] = future_redirects.result()
        features['time_response'] = future_response_time.result()
        features.update(future_dns.result())
        features['safe_browsing_flagged'] = future_safe_browsing.result()

    return features


TRUSTED_DOMAINS = [
    "google.com", "paypal.com", "microsoft.com", "amazon.com",
    "apple.com", "facebook.com", "netflix.com", "github.com"
]


def predict_url(url):
    parsed_domain = urlparse(url).netloc.replace("www.", "")

    # 1. Trusted domain whitelist - skip everything else
    if any(parsed_domain == trusted or parsed_domain.endswith("." + trusted) for trusted in TRUSTED_DOMAINS):
        return {"url": url, "prediction": "LEGITIMATE", "confidence": 99.0, "note": "Trusted domain whitelist"}

    # 2. Google Safe Browsing - if already confirmed malicious, skip the ML model entirely
    if check_safe_browsing(url) == 1:
        return {"url": url, "prediction": "PHISHING", "confidence": 99.0, "note": "Flagged by Google Safe Browsing"}

    # 3. Otherwise, fall through to the trained ML model
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