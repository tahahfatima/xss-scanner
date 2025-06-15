#!/usr/bin/env python3
import requests
import argparse
import urllib3
import json
import re
from termcolor import colored

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAYLOADS = [
    "{{7*7}}",         # Jinja2
    "${7*7}",          # Velocity / Java
    "#{7*7}",          # Ruby ERB
    "<%= 7*7 %>",      # JSP
    "${{7*7}}",        # Freemarker
]

ENGINES = {
    "{{7*7}}": 49,
    "${7*7}": 49,
    "#{7*7}": 49,
    "<%= 7*7 %>": 49,
    "${{7*7}}": 49,
}

def test_get(url):
    print(colored(f"[GET] Testing URL: {url}", "cyan"))
    for payload in PAYLOADS:
        injected_url = url.replace("§", payload)
        print(f"  ↪ Trying: {payload}")
        r = requests.get(injected_url, verify=False)
        if str(ENGINES[payload]) in r.text:
            print(colored(f"  ✅ SSTI Detected: {payload} → Evaluated to {ENGINES[payload]}", "green"))
        elif payload in r.text:
            print(colored(f"  ⚠️ Payload reflected but not executed: {payload}", "yellow"))
        else:
            print(colored(f"  ❌ Not reflected: {payload}", "red"))

def test_post(url, param):
    print(colored(f"[POST] Testing param: {param}", "cyan"))
    for payload in PAYLOADS:
        data = {param: payload}
        r = requests.post(url, data=data, verify=False)
        if str(ENGINES[payload]) in r.text:
            print(colored(f"  ✅ SSTI Detected: {payload} → Evaluated to {ENGINES[payload]}", "green"))
        elif payload in r.text:
            print(colored(f"  ⚠️ Payload reflected: {payload}", "yellow"))
        else:
            print(colored(f"  ❌ No injection for: {payload}", "red"))

def test_json(url, param):
    print(colored(f"[JSON] Testing JSON param: {param}", "cyan"))
    for payload in PAYLOADS:
        data = {param: payload}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
        if str(ENGINES[payload]) in r.text:
            print(colored(f"  ✅ SSTI Detected: {payload} → Evaluated to {ENGINES[payload]}", "green"))
        elif payload in r.text:
            print(colored(f"  ⚠️ Reflected: {payload}", "yellow"))
        else:
            print(colored(f"  ❌ Not reflected: {payload}", "red"))

def main():
    parser = argparse.ArgumentParser(description="🧪 SSTI Hunter - Pro template injection scanner")
    parser.add_argument("url", help="Target URL (use § for injection point)")
    parser.add_argument("--method", choices=["GET", "POST", "JSON"], default="GET", help="HTTP method")
    parser.add_argument("--param", help="Parameter name for POST/JSON")
    args = parser.parse_args()

    if args.method == "GET":
        if "§" not in args.url:
            print(colored("❌ You must use § in the URL to mark injection point for GET.", "red"))
            return
        test_get(args.url)
    elif args.method == "POST":
        if not args.param:
            print(colored("❌ You must specify a --param for POST.", "red"))
            return
        test_post(args.url, args.param)
    elif args.method == "JSON":
        if not args.param:
            print(colored("❌ You must specify a --param for JSON.", "red"))
            return
        test_json(args.url, args.param)

if __name__ == "__main__":
    main()
