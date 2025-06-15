# 🔥 DOM XSS Analyzer (Pro Version)
import requests
import re
import sys
from termcolor import colored

def find_dom_xss(js_url):
    print(colored(f"[🔍] Analyzing JavaScript for DOM XSS: {js_url}", "cyan"))
    try:
        r = requests.get(js_url, timeout=10)
        js_code = r.text

        sinks = [
            "innerHTML", "outerHTML", "document.write", "document.writeln",
            "eval", "setTimeout", "setInterval", "Function", "location"
        ]
        sources = [
            "document.URL", "document.documentURI", "document.URLUnencoded",
            "document.baseURI", "location", "location.href",
            "location.search", "location.hash", "document.referrer"
        ]

        found = False
        for sink in sinks:
            for source in sources:
                pattern = re.compile(rf"{sink}\s*\(.*{source}.*\)", re.IGNORECASE)
                if pattern.search(js_code):
                    print(colored(f"[💥] DOM XSS Sink Detected: {sink} ← {source}", "red"))
                    found = True
        if not found:
            print(colored("[✔️] No direct DOM XSS patterns found.", "green"))
    except Exception as e:
        print(colored(f"[!] Error fetching/analyzing: {e}", "red"))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 dom_xss_analyzer.py http://target.com/app.js")
        sys.exit(1)
    find_dom_xss(sys.argv[1])
