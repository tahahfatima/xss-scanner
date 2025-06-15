import requests
import socket
import argparse
import dns.resolver

# Common 3rd-party takeover fingerprints
FINGERPRINTS = {
    "GitHub Pages": "There isn't a GitHub Pages site here.",
    "Heroku": "No such app",
    "AWS S3": "NoSuchBucket",
    "Cloudfront": "Bad request",
    "Bitbucket": "Repository not found",
    "Shopify": "Sorry, this shop is currently unavailable",
    "Unbounce": "The requested URL was not found on this server",
    "Tumblr": "There's nothing here.",
}

def resolve_cname(subdomain):
    try:
        answers = dns.resolver.resolve(subdomain, 'CNAME')
        for rdata in answers:
            return str(rdata.target).rstrip('.')
    except:
        return None

def check_takeover(subdomain):
    cname = resolve_cname(subdomain)
    try:
        r = requests.get(f"http://{subdomain}", timeout=7)
        body = r.text
    except:
        body = ""
    
    for service, fingerprint in FINGERPRINTS.items():
        if fingerprint in body:
            print(f"[⚠️] Possible takeover on {subdomain} ({service})")
            return

    if "not found" in body.lower() or "no such" in body.lower():
        print(f"[❓] Unusual error on {subdomain}: might be vulnerable")
    elif cname:
        print(f"[-] {subdomain} → CNAME: {cname} (No obvious vuln)")
    else:
        print(f"[-] {subdomain} resolved OK (No CNAME or issue detected)")

def main(file_path):
    with open(file_path) as f:
        subdomains = [line.strip() for line in f if line.strip()]
    print(f"[📡] Scanning {len(subdomains)} subdomains...\n")
    for sub in subdomains:
        check_takeover(sub)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧟 Broken Link Hijack Scanner")
    parser.add_argument("file", help="File with list of subdomains")
    a
