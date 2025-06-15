import requests
import argparse
import urllib3
from urllib.parse import urlparse, urlencode, parse_qs
from difflib import SequenceMatcher

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_reflected(base, test, payload):
    return payload in test and SequenceMatcher(None, base, test).ratio() < 0.95

def discover_params(base_url, wordlist, payload="1337", grep=None, cookies=None):
    print(f"\n🔎 Scanning {base_url} for hidden parameters...\n")
    
    headers = {}
    if cookies:
        headers['Cookie'] = cookies

    parsed = urlparse(base_url)
    base_params = parse_qs(parsed.query)
    base_clean = parsed._replace(query="").geturl()

    original = requests.get(base_url, headers=headers, verify=False).text

    with open(wordlist, 'r') as f:
        param_list = [line.strip() for line in f if line.strip() and '=' not in line]

    found = []

    for param in param_list:
        query = base_params.copy()
        query[param] = payload
        full_url = f"{base_clean}?{urlencode(query, doseq=True)}"

        try:
            r = requests.get(full_url, headers=headers, verify=False, timeout=8)
            content = r.text

            if grep and grep in content:
                print(f"[🎯] Keyword '{grep}' detected with parameter: {param}")
                found.append((param, "GREP"))

            elif is_reflected(original, content, payload):
                print(f"[💥] Reflected param found: {param}")
                found.append((param, "Reflected"))

            elif len(content) != len(original):
                print(f"[⚠️] Length changed: {param} (Status: {r.status_code})")
                found.append((param, "LengthDiff"))

        except Exception as e:
            print(f"[⚠️] Error testing param '{param}': {e}")

    if not found:
        print("\n[❌] No interesting parameters found.")
    else:
        print(f"\n✅ Discovery complete. Found {len(found)} potentially useful parameters.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🕵️ Advanced Parameter Discovery Tool")
    parser.add_argument("url", help="Target URL to test (e.g. https://site.com/page)")
    parser.add_argument("wordlist", help="Path to parameter wordlist")
    parser.add_argument("--payload", default="1337", help="Payload to inject (default: 1337)")
    parser.add_argument("--grep", help="String to grep for in responses (e.g. admin)")
    parser.add_argument("--cookie", help="Optional cookies")

    args = parser.parse_args()
    discover_params(args.url, args.wordlist, args.payload, args.grep, args.cookie)
