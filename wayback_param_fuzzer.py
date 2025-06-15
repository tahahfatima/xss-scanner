#!/usr/bin/env python3
import requests
import re
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

WAYBACK_API = "http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey"
FUZZ_PAYLOAD = "w4yb4ckXSS"

def fetch_wayback_urls(domain):
    print(f"[🌐] Fetching Wayback Machine URLs for {domain}...")
    res = requests.get(WAYBACK_API.format(domain=domain))
    if res.status_code != 200:
        print("[-] Failed to fetch URLs.")
        return []
    data = res.json()[1:]  # Skip header
    return list(set([row[0] for row in data if "?" in row[0]]))

def extract_parameters(urls):
    seen_params = set()
    final_urls = []

    for url in urls:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        for key in qs:
            if key not in seen_params:
                seen_params.add(key)
                new_qs = {k: (FUZZ_PAYLOAD if k == key else v[0]) for k, v in qs.items()}
                new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', urlencode(new_qs), ''))
                final_urls.append((key, new_url))
    return final_urls

def fuzz_reflections(urls):
    print(f"[🔎] Fuzzing {len(urls)} parameters...")
    for key, test_url in urls:
        try:
            r = requests.get(test_url, timeout=7, verify=False)
            if FUZZ_PAYLOAD in r.text:
                print(f"[💥] Reflected Param Found: {key} → {test_url}")
        except Exception as e:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 wayback_param_fuzzer.py <domain.com>")
        sys.exit(1)

    target = sys.argv[1]
    urls = fetch_wayback_urls(target)
    param_urls = extract_parameters(urls)
    fuzz_reflections(param_urls)
