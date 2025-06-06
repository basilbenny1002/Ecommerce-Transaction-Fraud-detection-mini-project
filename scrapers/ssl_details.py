from cryptography import x509
from cryptography.hazmat.backends import default_backend
import ssl
import socket
from urllib.parse import urlparse
import json

ORG_ID_MAP = {
    "Cloudflare": 1,
    "Let's Encrypt": 2,
    "Sectigo": 3,
    "cPanel": 4,
    "GoDaddy": 5,
    "Amazon": 6,
    "DigiCert": 7,
    "GlobalSign": 8,
    "Google Trust Services": 9,
    "ZeroSSL": 10,
}

def find_org_id(cert_org_name, mapping):
    """
    Finds the organization ID by checking if a key from the mapping
    is present within the certificate's organization name.
    """
    for key, org_id in mapping.items():
        if key in cert_org_name:
            return org_id
    return 11 # Return the default 'Other' ID if no match is found

def get_ssl_details(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or url
    port = parsed_url.port or 443

    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=hostname)
    conn.settimeout(5.0)

    try:
        conn.connect((hostname, port))
        der_cert = conn.getpeercert(binary_form=True)
        cert = x509.load_der_x509_certificate(der_cert, default_backend())

        issuer = cert.issuer
        issuer_attributes = {attr.oid._name: attr.value for attr in issuer}
        issuer_org_name = issuer_attributes.get("organizationName", "Unknown")
        expire_date = cert.not_valid_after_utc.strftime("%Y-%m-%d %H:%M:%S")
        org_id = find_org_id(issuer_org_name, ORG_ID_MAP)

        print(f"SSL certificate issuer name: {issuer.rfc4514_string()}")
        print(f"SSL certificate expire date: {expire_date}")
        print(f"SSL certificate issuer organization name: {issuer_org_name}")
        print(f"SSL certificate issuer organization ID: {org_id}")

    except Exception as e:
        print(f"Error retrieving SSL info: {e}")
    finally:
        conn.close()

    
if __name__ == "__main__":
    url_input = "www.amazon.com" # Let's test with Amazon
    if not url_input.startswith("http"):
        url_input = "https://" + url_input
    get_ssl_details(url_input)