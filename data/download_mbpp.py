import os
import urllib.request

DATA_URL = "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/sanitized-mbpp.json"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "sanitized-mbpp.json")

def download_dataset():
    """Downloads sanitized-mbpp.json if not already present."""
    if os.path.exists(OUTPUT_PATH):
        print(f"[Dataset] Already exists at {OUTPUT_PATH}")
        return OUTPUT_PATH
    
    print(f"[Dataset] Downloading MBPP sanitized dataset from {DATA_URL} ...")
    urllib.request.urlretrieve(DATA_URL, OUTPUT_PATH)
    print(f"[Dataset] Saved to {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    download_dataset()
