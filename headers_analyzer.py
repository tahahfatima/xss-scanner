import requests
import argparse
from colorama import Fore, Style, init

init(autoreset=True)

RISKY_CSP_KEYWORDS = ["unsafe-inline", "unsafe-eval", "*", "data:", "blob:"]

def analyze_csp(csp_value):
    issues = []
    for keyword in RISKY_CSP_KEYWORDS:
        if keyword in csp_value:
            issues.append(f"{Fore.RED}[!] Risky CSP keyword found: {keyword}")
    return issues

def check_header(name, value):
    lower_name = name.lower()
    result = f"{Fore.GREEN}[+] {name}: {value}"

    if lower_name == "x-frame-options":
        if "DENY" not in value.upper() and "SAMEORIGIN" not in value.upper():
            result = f"{Fore.YELLOW}[!] X-Frame-Options might allow clickjacking: {value}"

    elif lower_name == "x-xss-protection":
        if "1" not in value or "mode=block" not in value:
            result = f"{Fore.YELLOW}[!] X-XSS-Protection is weak: {value}"

    elif lower_name == "content-security-policy":
        csp_issues = analyze_csp(value)
        if csp_issues:
            result = f"{Fore.RED}[!] CSP Weaknesses Detected:\n" + "\n".join(csp_issues)

    elif lower_name == "strict-transport-security":
        if "max-age" not in value:
            result = f"{Fore.YELLOW}[!] HSTS missing max-age: {value}"

    return result

def analyze_headers(url):
    try:
        r = requests.get(url, timeout=10, verify=False)
        print(f"\n{Fore.CYAN}[i] Analyzing headers for {url}\n")
        headers = r.headers

        important = [
            "Content-Security-Policy", "X-Frame-Options", "X-XSS-Protection",
            "Strict-Transport-Security", "Referrer-Policy", "Permissions-Policy"
        ]

        found = []
        for h in important:
            if h in headers:
                found.append(check_header(h, headers[h]))
            else:
                found.append(f"{Fore.RED}[!] Missing Header: {h}")

        print("\n".join(found))
        print(f"\n{Fore.BLUE}[i] Status Code: {r.status_code}")
    except Exception as e:
        print(f"{Fore.RED}[!] Error fetching headers: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🛡️ CSP & Security Headers Analyzer")
    parser.add_argument("url", help="Target URL")
    args = parser.parse_args()
    analyze_headers(args.url)
