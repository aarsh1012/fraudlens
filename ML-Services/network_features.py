import whois
from datetime import datetime, timezone
import ssl
import socket
import requests
import time
import re
import dns.resolver
import os
from dotenv import load_dotenv

load_dotenv()

# tells - How long has this domain existed?
def make_naive(dt):
    """Remove timezone info if present, so we can safely compare dates."""
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

def get_domain_age_features(domain):
    features = {}
    try:
        w = whois.whois(domain)

        creation_date = w.creation_date
        expiration_date = w.expiration_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        creation_date = make_naive(creation_date)
        expiration_date = make_naive(expiration_date)

        if creation_date:
            days_active = (datetime.now() - creation_date).days
            features['time_domain_activation'] = days_active
        else:
            features['time_domain_activation'] = -1

        if expiration_date:
            days_to_expiry = (expiration_date - datetime.now()).days
            features['time_domain_expiration'] = days_to_expiry
        else:
            features['time_domain_expiration'] = -1

    except Exception as e:
        print("WHOIS lookup failed:", e)
        features['time_domain_activation'] = -1
        features['time_domain_expiration'] = -1

    return features


# checks: does the site have a valid HTTPS/SSL certificate?
def check_ssl_certificate(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                if cert:
                    return 1  # valid SSL certificate found
                else:
                    return 0
    except Exception as e:
        print("SSL check failed:", e)
        return 0  # no valid SSL / connection failed


# list of every "hop" the request went through before landing on the final page
def count_redirects(url):
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        return len(response.history)
    except Exception as e:
        print("Redirect check failed:", e)
        return -1


def get_response_time(url):
    try:
        start = time.time()
        requests.get(url, timeout=5)
        end = time.time()
        return round(end - start, 3)
    except Exception as e:
        print("Response time check failed:", e)
        return -1


def extract_extra_features(url, domain):
    features = {}

    # Is the domain literally an IP address instead of a name? (major red flag)
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    features['domain_in_ip'] = 1 if re.match(ip_pattern, domain) else 0

    # How many times does a TLD-like word (.com, .net, .org etc) appear in the full URL
    common_tlds = ['.com', '.net', '.org', '.info', '.biz', '.xyz', '.top']
    features['qty_tld_url'] = sum(url.lower().count(tld) for tld in common_tlds)

    # Vowel count in domain (phishing domains sometimes look "gibberish")
    features['qty_vowels_domain'] = sum(1 for ch in domain.lower() if ch in 'aeiou')

    # Does domain contain suspicious words like "server" or "client"
    features['server_client_domain'] = 1 if ('server' in domain.lower() or 'client' in domain.lower()) else 0

    return features


# NEW - DNS-based features (nameservers, mail servers, SPF, TTL, resolved IPs)
def get_dns_features(domain):
    # DNS records live on the root domain, not the www subdomain
    root_domain = domain[4:] if domain.startswith("www.") else domain

    features = {}
    try:
        ns_records = dns.resolver.resolve(root_domain, 'NS')
        features['qty_nameservers'] = len(ns_records)
    except Exception as e:
        print("NS lookup failed:", e)
        features['qty_nameservers'] = 0

    try:
        mx_records = dns.resolver.resolve(root_domain, 'MX')
        features['qty_mx_servers'] = len(mx_records)
    except Exception as e:
        print("MX lookup failed:", e)
        features['qty_mx_servers'] = 0

    try:
        txt_records = dns.resolver.resolve(root_domain, 'TXT')
        has_spf = any('v=spf1' in str(record) for record in txt_records)
        features['domain_spf'] = 1 if has_spf else 0
    except Exception as e:
        print("TXT/SPF lookup failed:", e)
        features['domain_spf'] = 0

    try:
        answer = dns.resolver.resolve(domain, 'A')
        features['ttl_hostname'] = answer.rrset.ttl
    except Exception as e:
        print("TTL lookup failed:", e)
        features['ttl_hostname'] = -1

    try:
        _, _, ip_list = socket.gethostbyname_ex(domain)
        features['qty_ip_resolved'] = len(ip_list)
    except Exception as e:
        print("IP resolution failed:", e)
        features['qty_ip_resolved'] = 0

    return features
def check_safe_browsing(url):
    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"

    payload = {
        "client": {"clientId": "fraudlens", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        data = response.json()
        return 1 if "matches" in data else 0
    except Exception as e:
        print("Safe Browsing check failed:", e)
        return 0  # fail open - don't block a prediction just because this one check errored

if __name__ == "__main__":
    result = get_domain_age_features("google.com")
    print(result)

    ssl_result = check_ssl_certificate("google.com")
    print("SSL valid:", ssl_result)

    redirects = count_redirects("https://google.com")
    print("Redirects:", redirects)

    response_time = get_response_time("https://google.com")
    print("Response time (seconds):", response_time)

    dns_result = get_dns_features("google.com")
    print("DNS features:", dns_result)

    safe_browsing_result = check_safe_browsing("https://www.google.com")
    print("Safe Browsing flagged (google.com):", safe_browsing_result)