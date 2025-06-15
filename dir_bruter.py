#!/usr/bin/env python3
import requests
import argparse
from urllib.parse import urljoin
import urllib3
from termcolor import colored
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_wordlist(path):
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_title(content):
    title = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    return title.group(1).strip() if title else ""

def scan_path(base_url, path, headers, keyword_filter, status_filter, waf_bypass):
    test_paths = [path]
    if waf_bypass:
        test_paths.extend([path + "/", path + "/.", path + "??", path + "%20"])

    for p in test_paths:
        url = urljoin(base_url, p)
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=5, allow_redirects=True)
            status = r.status_code
            title = get_title(r.text)
            if (not status_filter or status in status_filter):
                line = f"[{status}] {url}"
                if title:
                    line += f" | 🏷️ Title: {title}"
                if keyword_filter:
                    for kw in keyword_filter:
                        if kw.lower() in r.text.lower():
                            line += colored(f" | 🔑 Found keyword: {kw}", "green")
                print(line)
        except Exception as e:
            print(colored(f"[!] Error with {url}: {e}", "red"))

def main():
    parser = argparse.ArgumentParser(description="📁 Advanced Directory & File Bruteforcer")
    parser.add_argument("url", help="Base URL to scan (e.g., https://target.com/)")
    parser.add_argument("wordlist", help="Path to wordlist file")
    parser.add_argument("--status", nargs="+", type=int, help="Filter status codes (e.g., 200 403 401)")
    parser.add_argument("--keyword", nargs="+", help="Highlight keywords in response")
    parser.add_argument("--cookie", help="Add Cookie header")
    parser.add_argument("--waf", action="store_true", help="Use WAF bypass path tricks")
    args = parser.parse_args()

    headers = {
        "User-Agent": "Mozilla/5.0 (dirBruter)",
    }
    if args.cookie:
        headers["Cookie"] = args.cookie

    paths = load_wordlist(args.wordlist)
