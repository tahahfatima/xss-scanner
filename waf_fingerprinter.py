#!/usr/bin/env python3
import requests
import argparse
import warnings
from time import sleep
from termcolor import colored

warnings.filterwarnings("ignore", category=UserWarning)

SIGNATURES = {
    "cloudflare": ["cf-ray", "cloudflare", "__cfduid"],
    "akamai": ["akamai", "akamai-ghost"],
    "sucuri": ["sucuri", "x-sucuri-id", "x-sucuri-cache"],
    "imperva": ["incapsula", "x-cdn", "x-iinfo"],
    "aws": ["awselb", "x-amzn", "x-amz-cf-id"],
    "f5": ["bigip", "f5-sticky"],
    "fastly": ["fastly", "x-served-by", "x-cache"],
    "barracuda": ["barracuda", "barra-counter", "bn-guid"],
    "azure": ["azure", "x-azure-ref"],
    "dDOS-Guard": ["ddos-guard"]
}

MALICIOUS_PATHS = [
    "/etc/passwd",
    "' OR '1'='1",
    "<script>alert(1337)</script>",
    "../../../../../../etc/shadow",
    "/admin/login.php",
]

def scan_headers(headers):
    detected = []
    for waf, sigs in SIGNATURES.items():
        for sig in sigs:
            for key, value in headers.items():
                if sig.lower() in key.lower() or sig.lower() in str(value).lower():
                    detected.append(waf)
    return list(set(detected))

def provoke_waf(url):
    hits = []
    print(colored("\n[⚔️] Probing with suspicious requests...", "blue"))
    for path in MALICIOUS_PATHS:
        try:
            test_url = f"{url.rstrip('/')}/{path}"
            r = requests.get(test_url, verify=False, timeout=6)
            status = r.status_code
            wafs = scan_headers(r.headers)
            hits.append((path, status, wafs))
            sleep(0.5)
        except:
            continue
    return hits

def main():
    parser = argparse.ArgumentParser(description="🛡️ WAF Fingerprinter")
    parser.add_argument("url", help="Target base URL (e.g., https://site.com)")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    print(colored(f"[🎯] Target: {base_url}", "cyan"))

    try:
        r = requests.get(base_url, verify=False, timeout=6)
        print(colored("\n[🔍] Analyzing base headers...", "blue"))
        wafs = scan_headers(r.headers)
        if wafs:
            print(colored(f"[🛡️] Possible WAF Detected: {', '.join(wafs)}", "green"))
        else:
            print(colored("[❌] No clear WAF detected in base headers", "yellow"))

        # WAF Probing
        results = provoke_waf(base_url)
        print(colored("\n[📊] Analysis of suspicious requests:", "magenta"))
        for path, status, wafs in results:
            print(f"  ↪ Path: {path} | Status: {status} | WAF Hints: {', '.join(wafs) if wafs else 'None'}")
    except Exception as e:
        print(colored(f"[!] Error: {e}", "red"))

if __name__ == "__main__":
    main()
