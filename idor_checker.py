import requests
import argparse
import time
from difflib import SequenceMatcher

def send_request(url, headers):
    try:
        res = requests.get(url, headers=headers, timeout=10, verify=False)
        return res.status_code, res.text
    except requests.exceptions.RequestException as e:
        print(f"[⚠️] Error: {e}")
        return None, None

def is_different(reference_text, test_text):
    ratio = SequenceMatcher(None, reference_text, test_text).ratio()
    return ratio < 0.95  # adjustable threshold

def fuzz_idor(base_url, start, end, header):
    print(f"\n[🔍] Starting IDOR scan from ID {start} to {end}")
    headers = {}
    if header:
        k, v = header.split(":", 1)
        headers[k.strip()] = v.strip()

    # Get reference response
    ref_url = base_url.replace("ID", str(start))
    print(f"[📌] Reference URL: {ref_url}")
    ref_status, ref_body = send_request(ref_url, headers)
    if ref_status != 200:
        print(f"[⚠️] Reference ID returned status {ref_status}. Scan may be inaccurate.")

    time.sleep(1)

    for i in range(start + 1, end + 1):
        target_url = base_url.replace("ID", str(i))
        status, body = send_request(target_url, headers)
        if status == 200 and is_different(ref_body, body):
            print(f"[💥] Potential IDOR at ID {i} → {target_url}")
        else:
            print(f"[❌] ID {i} → Not different or inaccessible")

        time.sleep(0.5)  # avoid rate limits

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🛡️ Advanced IDOR fuzzing tool")
    parser.add_argument("url", help="Target URL with 'ID' as placeholder (e.g., https://site.com/api/user/ID)")
    parser.add_argument("--start", type=int, default=1, help="Start of ID range")
    parser.add_argument("--end", type=int, default=20, help="End of ID range")
    parser.add_argument("--header", help="Custom header (e.g., 'Authorization: Bearer token')")

    args = parser.parse_args()
    fuzz_idor(args.url, args.start, args.end, args.header)
