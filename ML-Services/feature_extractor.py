from urllib.parse import urlparse

def count_char(text, char):
    return text.count(char)

def extract_url_features(url):
    features = {}

    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    query = parsed.query

    # --- Full URL level features ---
    features['qty_dot_url'] = count_char(url, '.')
    features['qty_hyphen_url'] = count_char(url, '-')
    features['qty_underline_url'] = count_char(url, '_')
    features['qty_slash_url'] = count_char(url, '/')
    features['qty_questionmark_url'] = count_char(url, '?')
    features['qty_equal_url'] = count_char(url, '=')
    features['qty_at_url'] = count_char(url, '@')
    features['qty_and_url'] = count_char(url, '&')
    features['qty_exclamation_url'] = count_char(url, '!')
    features['qty_space_url'] = count_char(url, ' ')
    features['qty_tilde_url'] = count_char(url, '~')
    features['qty_comma_url'] = count_char(url, ',')
    features['qty_plus_url'] = count_char(url, '+')
    features['qty_asterisk_url'] = count_char(url, '*')
    features['qty_hashtag_url'] = count_char(url, '#')
    features['qty_dollar_url'] = count_char(url, '$')
    features['qty_percent_url'] = count_char(url, '%')
    features['length_url'] = len(url)

    # --- Domain level features ---
    features['qty_dot_domain'] = count_char(domain, '.')
    features['qty_hyphen_domain'] = count_char(domain, '-')
    features['qty_underline_domain'] = count_char(domain, '_')
    features['domain_length'] = len(domain)

    # --- Directory level features (the path before the filename) ---
    directory = "/".join(path.split("/")[:-1]) if "/" in path else ""
    features['qty_dot_directory'] = count_char(directory, '.')
    features['qty_hyphen_directory'] = count_char(directory, '-')
    features['qty_underline_directory'] = count_char(directory, '_')
    features['qty_slash_directory'] = count_char(directory, '/')
    features['qty_questionmark_directory'] = count_char(directory, '?')
    features['qty_equal_directory'] = count_char(directory, '=')
    features['qty_at_directory'] = count_char(directory, '@')
    features['qty_and_directory'] = count_char(directory, '&')
    features['directory_length'] = len(directory)

    # --- File level features (just the filename part, e.g. "login") ---
    file_part = path.split("/")[-1] if "/" in path else path
    features['qty_dot_file'] = count_char(file_part, '.')
    features['qty_hyphen_file'] = count_char(file_part, '-')
    features['qty_underline_file'] = count_char(file_part, '_')
    features['file_length'] = len(file_part)

    # --- Params level features (everything after the "?") ---
    features['qty_dot_params'] = count_char(query, '.')
    features['qty_hyphen_params'] = count_char(query, '-')
    features['qty_underline_params'] = count_char(query, '_')
    features['qty_equal_params'] = count_char(query, '=')
    features['qty_and_params'] = count_char(query, '&')
    features['params_length'] = len(query)
    features['qty_params'] = len(query.split("&")) if query else 0

    # --- A few extra simple but important ones ---
    features['email_in_url'] = 1 if '@' in url else 0
    shortener_domains = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'is.gd', 'ow.ly']
    features['url_shortened'] = 1 if any(domain.endswith(s) for s in shortener_domains) else 0

    return features


# Quick test
if __name__ == "__main__":
    test_url = "http://paypal-secure-login.xyz.verify-account.com/login?id=123"
    result = extract_url_features(test_url)
    for k, v in result.items():
        print(k, ":", v)