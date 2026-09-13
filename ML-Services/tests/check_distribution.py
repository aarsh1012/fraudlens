import pandas as pd

df = pd.read_csv("dataset_small.csv")

for col in ['time_domain_activation', 'time_domain_expiration', 'time_response', 'qty_redirects', 'tls_ssl_certificate']:
    print(f"--- {col} ---")
    print(df[col].describe())
    print("Negative/failed values (-1 or less):", (df[col] <= -1).sum(), "out of", len(df))
    print()