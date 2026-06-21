#!/usr/bin/env python3
import json
import sys
import urllib.request
import urllib.error
import base64

def load_credentials():
    try:
        with open("domeneshop_credentials.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: 'domeneshop_credentials.json' not found. Please create it first.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: 'domeneshop_credentials.json' is not valid JSON.")
        sys.exit(1)

def api_request(url, method="GET", data=None, token=None, secret=None):
    req = urllib.request.Request(url, method=method)
    
    # Basic Authentication
    auth_str = f"{token}:{secret}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    req.add_header("Authorization", f"Basic {auth_b64}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "DomeneshopDNSUpdater/1.0")

    json_data = None
    if data:
        json_data = json.dumps(data).encode("utf-8")

    try:
        with urllib.request.urlopen(req, data=json_data) as response:
            res_data = response.read()
            if res_data:
                return json.loads(res_data.decode("utf-8"))
            return {}
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Connection Error: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update_dns.py <render-service-cname>")
        print("Example: python3 update_dns.py pox-sheet.onrender.com")
        sys.exit(1)

    target_cname = sys.argv[1].strip()
    # Strip protocol if user pasted a full URL
    if "://" in target_cname:
        target_cname = target_cname.split("://")[1]
    if "/" in target_cname:
        target_cname = target_cname.split("/")[0]

    # Ensure CNAME ends with a dot (some systems require this, or we let Domeneshop handle it)
    # Domeneshop API accepts it without the trailing dot. We will add a trailing dot if not present,
    # or keep it as is. Standard CNAME targets can have the dot. Let's use it without trailing dot
    # unless required. Actually, let's keep it clean: e.g. "pox-sheet.onrender.com"
    target_cname = target_cname.rstrip(".")

    config = load_credentials()
    token = config.get("api_token")
    secret = config.get("api_secret")
    domain_name = config.get("domain", "ostreborg.no")
    subdomain = config.get("subdomain", "pox")

    if not token or "YOUR" in token:
        print("Error: Please set your api_token in domeneshop_credentials.json")
        sys.exit(1)
    if not secret or "YOUR" in secret:
        print("Error: Please set your api_secret in domeneshop_credentials.json")
        sys.exit(1)

    base_url = "https://api.domeneshop.no/v0"

    print("Step 1: Connecting to Domeneshop and fetching domains...")
    domains = api_request(f"{base_url}/domains", token=token, secret=secret)
    
    domain_id = None
    for d in domains:
        if d.get("domain") == domain_name:
            domain_id = d.get("id")
            break

    if not domain_id:
        print(f"Error: Domain '{domain_name}' not found in your Domeneshop account.")
        sys.exit(1)
    
    print(f"Found domain '{domain_name}' (ID: {domain_id})")

    print(f"Step 2: Fetching DNS records for {domain_name}...")
    records = api_request(f"{base_url}/domains/{domain_id}/dns", token=token, secret=secret)

    existing_record = None
    for r in records:
        if r.get("host") == subdomain and r.get("type") == "CNAME":
            existing_record = r
            break

    payload = {
        "host": subdomain,
        "type": "CNAME",
        "data": target_cname,
        "ttl": 3600
    }

    if existing_record:
        record_id = existing_record["id"]
        current_value = existing_record["data"].rstrip(".")
        if current_value == target_cname:
            print(f"CNAME record for '{subdomain}.{domain_name}' already points to '{target_cname}'. No update needed.")
        else:
            print(f"Updating CNAME record for '{subdomain}.{domain_name}' from '{current_value}' to '{target_cname}'...")
            api_request(f"{base_url}/domains/{domain_id}/dns/{record_id}", method="PUT", data=payload, token=token, secret=secret)
            print("CNAME record updated successfully!")
    else:
        print(f"Creating new CNAME record for '{subdomain}.{domain_name}' pointing to '{target_cname}'...")
        api_request(f"{base_url}/domains/{domain_id}/dns", method="POST", data=payload, token=token, secret=secret)
        print("CNAME record created successfully!")

if __name__ == "__main__":
    main()
