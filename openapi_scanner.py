import json
import requests
import sys
import re
from urllib.parse import urljoin
from termcolor import colored

RISKY_METHODS = ["PUT", "DELETE", "PATCH"]
SENSITIVE_KEYWORDS = ["admin", "delete", "password", "token", "secret", "reset"]

def fetch_spec(spec_url):
    try:
        res = requests.get(spec_url, timeout=10, verify=False)
        if res.status_code == 200:
            if "yaml" in spec_url or res.text.strip().startswith("openapi:"):
                print(colored("[!] YAML not supported in this version.", "yellow"))
                return None
            return res.json()
    except Exception as e:
        print(colored(f"[!] Failed to fetch spec: {e}", "red"))
    return None

def analyze_endpoints(openapi, base_url=None):
    paths = openapi.get("paths", {})
    servers = openapi.get("servers", [])
    base = base_url or (servers[0]["url"] if servers else "")

    print(colored(f"[+] Analyzing {len(paths)} endpoints from: {base}", "cyan"))

    for path, methods in paths.items():
        for method, details in methods.items():
            method_upper = method.upper()
            full_url = urljoin(base + "/", path.lstrip("/"))

            issues = []
            if method_upper in RISKY_METHODS:
                issues.append(colored("🚨 Risky Method", "red"))

            if any(keyword in path.lower() for keyword in SENSITIVE_KEYWORDS):
                issues.append(colored("🔑 Sensitive Keyword", "magenta"))

            security = details.get("security", openapi.get("security", []))
            if not security:
                issues.append(colored("🔓 No Auth Required", "yellow"))

            summary = details.get("summary", "")
            print(colored(f"\n[→] {method_upper} {full_url}", "blue"))
            if summary:
                print(f"    📄 {summary}")
            if issues:
                print("    ⚠️  " + " | ".join(issues))

            # Optional: Show a curl command
            print(f"    💡 curl -X {method_upper} '{full_url}'\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 openapi_scanner.py <OpenAPI_JSON_URL>")
        sys.exit(1)

    spec_url = sys.argv[1]
    openapi_spec = fetch_spec(spec_url)
    if openapi_spec:
        analyze_endpoints(openapi_spec)
