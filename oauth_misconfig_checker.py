import sys
import re
import requests
from urllib.parse import urlparse, parse_qs
from termcolor import colored

VULN_SCOPES = ["admin", "write", "offline_access", "full", "root"]
REDIRECT_MISCONFIG_PATTERNS = [
    r"\*",  # wildcards
    r"http://",  # non-https
    r"localhost", r"127\.0\.0\.1"
]

def analyze_oauth_url(oauth_url):
    print(colored(f"[+] Analyzing OAuth URL: {oauth_url}", "cyan"))

    parsed = urlparse(oauth_url)
    qs = parse_qs(parsed.query)

    # 1. Check for missing state param
    if "state" not in qs:
        print(colored("⚠️ Missing 'state' param — CSRF risk", "yellow"))

    # 2. Check redirect_uri
    redirect = qs.get("redirect_uri", [""])[0]
    for pattern in REDIRECT_MISCONFIG_PATTERNS:
        if re.search(pattern, redirect, re.I):
            print(colored(f"🚨 redirect_uri misconfig: {redirect} matches pattern: {pattern}", "red"))

    # 3. Check for dangerous scopes
    scopes = qs.get("scope", [""])[0].split()
    for s in scopes:
        if s in VULN_SCOPES:
            print(colored(f"🔑 Sensitive scope: {s}", "magenta"))

    # 4. Check for implicit flow
    if "#access_token" in oauth_url or "response_type=token" in oauth_url:
        print(colored("❗ Uses Implicit Flow (response_type=token) — not recommended", "yellow"))

    # 5. Optionally test live response
    try:
        r = requests.get(oauth_url, allow_redirects=False, timeout=5)
        if r.status_code in [302, 301]:
            location = r.headers.get("Location", "")
            if "code=" in location:
                print(colored(f"✅ Redirects with auth code: {location}", "green"))
                if "Referer" in r.request.headers:
                    print(colored("🔎 Referer header may leak code!", "red"))
    except Exception as e:
        print(colored(f"[x] Error testing live OAuth URL: {e}", "grey"))

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 oauth_misconfig_checker.py '<OAuth URL>'")
        sys.exit(1)
    
    oauth_url = sys.argv[1]
    analyze_oauth_url(oauth_url)

if __name__ == "__main__":
    main()
