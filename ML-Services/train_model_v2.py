import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# The exact features we can actually compute for a real URL right now
SELECTED_FEATURES = [
    # URL-level
    'qty_dot_url', 'qty_hyphen_url', 'qty_underline_url', 'qty_slash_url',
    'qty_questionmark_url', 'qty_equal_url', 'qty_at_url', 'qty_and_url',
    'qty_exclamation_url', 'qty_space_url', 'qty_tilde_url', 'qty_comma_url',
    'qty_plus_url', 'qty_asterisk_url', 'qty_hashtag_url', 'qty_dollar_url',
    'qty_percent_url', 'length_url',

    # Domain-level
    'qty_dot_domain', 'qty_hyphen_domain', 'qty_underline_domain', 'domain_length',

    # Directory-level
    'qty_dot_directory', 'qty_hyphen_directory', 'qty_underline_directory',
    'qty_slash_directory', 'qty_questionmark_directory', 'qty_equal_directory',
    'qty_at_directory', 'qty_and_directory', 'directory_length',

    # File-level
    'qty_dot_file', 'qty_hyphen_file', 'qty_underline_file', 'file_length',

    # Params-level
    'qty_dot_params', 'qty_hyphen_params', 'qty_underline_params',
    'qty_equal_params', 'qty_and_params', 'params_length', 'qty_params',

    # Extra
    'email_in_url', 'url_shortened',

    # Network-based
    'time_domain_activation', 'time_domain_expiration',
    'tls_ssl_certificate', 'qty_redirects', 'time_response',
    'domain_in_ip', 'qty_tld_url', 'qty_vowels_domain', 'server_client_domain',

        # DNS-based
    'qty_nameservers', 'qty_mx_servers', 'domain_spf', 'ttl_hostname', 'qty_ip_resolved',
]

# Load data
df = pd.read_csv("dataset_small.csv")

X = df[SELECTED_FEATURES]
y = df["phishing"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

joblib.dump(model, "fraud_model_v2.pkl")
joblib.dump(SELECTED_FEATURES, "selected_features.pkl")
print("Model saved as fraud_model_v2.pkl")