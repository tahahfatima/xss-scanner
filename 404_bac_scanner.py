#!/usr/bin/env python3
import requests
import sys
import argparse
from difflib import SequenceMatcher
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

WORDLIST = [
    "admin", "dashboard", "config", "backup", "old", "test", "staging",
    "debug", "api", "server-status", ".git", "hidden", "secret"
]

def get_baseline_404(url):
    fake_path = "/this_path_should_not_exist_1337"
    r = requests.get(url + fake_path, timeout=6, verify=False)
    return r.status_code, r.text

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def scan_paths(url, baseline_status, baseline_body):
    print(f"\n[🔍] Scanning {len(WORDLIST)} paths against baseline...")
    for path in WORDLIST:
        test_url = f"{url}/{path}"
        try:
            r = requests.get(test_url, timeout=6, verify=False)
            status_match = r.status_code == baseline_status
            body_match = similar(r.text, baseline_body) > 0.95

            if not (status_match and body_match):
                print(f"[🚨] Possible BAC: {test_url} | Status: {r.status_code}")
        except Exception as e:
            continue

def main():
    parser = argparse.ArgumentParser(description="🦴 404-Based Broken Access Control Scanner")
    parser.add_argument("url", help="Target base URL (e.g., https://example.com)")
    args = parser.parse_args()

    base_url = args.url.rstrip('/')
    print(f"[🎯] Target: {base_url}")
    print("[🔎] Getting baseline 404 response...")
    
    status, body = get_baseline_404(base_url)
    print(f"[ℹ️] Baseline 404 → Status: {status}, Body length: {len(body)}")
    
    scan_paths(base_url, status, body)

if __name__ == "__main__":
    main()
