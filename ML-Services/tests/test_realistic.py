from predict import predict_url

test_urls = [
    "http://paypal-secure-verify.account-update.xyz/login",
    "http://192.168.1.1/bank-login",
    "http://amaz0n-security-check.tk/verify?id=283910",
    "http://bit.ly/3xK9L2p",
]

for url in test_urls:
    result = predict_url(url)
    print(result)