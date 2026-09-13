from predict import predict_url

test_urls = [
    "https://www.google.com",
    "https://www.paypal.com",
    "https://www.microsoft.com",
    "https://www.amazon.com",
]

for url in test_urls:
    result = predict_url(url)
    print(result)