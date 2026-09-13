import time
from predict import extract_all_features

test_url = "https://www.wikipedia.org"

start = time.time()
extract_all_features(test_url)
end = time.time()

print(f"Total time (sequential): {round(end - start, 2)} seconds")