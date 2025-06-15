import requests
import sys
import threading
import queue
from termcolor import colored

# Common sensitive files
SENSITIVE_FILES = [
    "config.json", ".env", "db.sql", "backup.zip", "credentials.txt",
    "users.csv", "access.log", "debug.log", "secrets.yml"
]

BUCKET_FORMATS = [
    "http://{bucket}.s3.amazonaws.com",
    "http://s3.amazonaws.com/{bucket}",
    "http://{bucket}.s3-us-west-2.amazonaws.com",
    "https://{bucket}.s3.amazonaws.com",
    "https://s3.amazonaws.com/{bucket}"
]

def test_bucket(bucket_name):
    for fmt in BUCKET_FORMATS:
        url = fmt.format(bucket=bucket_name)
        try:
            r = requests.get(url, timeout=5)
            if "AccessDenied" in r.text or r.status_code == 403:
                print(colored(f"[🔒] {url} - Forbidden (but exists)", "yellow"))
            elif "NoSuchBucket" in r.text or r.status_code == 404:
                continue
            elif "<ListBucketResult" in r.text:
                print(colored(f"[🔥] PUBLIC LISTING: {url}", "green"))
                test_sensitive_files(url)
            else:
                print(colored(f"[❓] {url} - Unexpected response", "cyan"))
        except Exception as e:
            pass

def test_sensitive_files(base_url):
    if not base_url.endswith("/"):
        base_url += "/"
    for filename in SENSITIVE_FILES:
        try:
            r = requests.get(base_url + filename, timeout=4)
            if r.status_code == 200 and len(r.text) > 20:
                print(colored(f"   [+] Found file: {base_url}{filename}", "magenta"))
        except:
            continue

def worker():
    while not q.empty():
        bucket = q.get()
        test_bucket(bucket)
        q.task_done()

def load_buckets_from_file(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 s3_bucket_scanner.py buckets.txt")
        sys.exit(1)

    bucket_list = load_buckets_from_file(sys.argv[1])
    q = queue.Queue()

    for bucket in bucket_list:
        q.put(bucket)

    for _ in range(10):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()
