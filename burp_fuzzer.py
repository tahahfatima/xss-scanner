import requests
import sys
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_burp_request(file_path):
    with open(file_path, 'r') as f:
        raw = f.read()

    lines = raw.splitlines()
    method, path, _ = lines[0].split()
    headers = {}
    body = ''
    is_body = False

    for line in lines[1:]:
        if line == '':
            is_body = True
            continue
        if is_body:
            body += line + '\n'
        else:
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip()] = v.strip()

    scheme = 'https' if '443' in headers.get('Host', '') else 'http'
    url = f"{scheme}://{headers['Host']}{path}"

    return method, url, headers, body.strip()

def fuzz_request(method, url, headers, body, payloads, keyword):
    if '§' not in url and '§' not in body:
        print("[❌] No § markers found in request. Add § to your injection point.")
        return

    for payload in payloads:
        cur_url = url.replace('§', payload)
        cur_body = body.replace('§', payload)

        try:
            if method.upper() == 'GET':
                r = requests.get(cur_url, headers=headers, verify=False)
            elif method.upper() == 'POST':
                r = requests.post(cur_url, headers=headers, data=cur_body, verify=False)
            else:
                print(f"[⚠️] Unsupported HTTP method: {method}")
                continue

            print(f"[📡] Payload: {payload} → Status: {r.status_code}, Length: {len(r.text)}", end='')

            if keyword and keyword in r.text:
                print(f"  [🎯] Keyword found!")
            else:
                print()
        except Exception as e:
            print(f"[⚠️] Error with payload {payload}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔥 Burp-style automated fuzzer with raw HTTP input")
    parser.add_argument("request_file", help="Raw HTTP request exported from Burp (with § markers)")
    parser.add_argument("wordlist", help="File containing payloads, one per line")
    parser.add_argument("--match", help="Optional string to match in response (e.g. 'admin')")
    args = parser.parse_args()

    method, url, headers, body = parse_burp_request(args.request_file)
    
    with open(args.wordlist, 'r') as f:
        payloads = [line.strip()]()
