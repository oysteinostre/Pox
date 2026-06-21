# Domeneshop DNS Setup for Pox

Please enter your Domeneshop API credentials and documentation link below.

1. Go to your **Domeneshop Admin Panel** -> **API** and generate a token and secret.
2. Paste them into the [domeneshop_credentials.json](file:///Users/oysteinostre/%C3%98streborg/Pox/domeneshop_credentials.json) file.
3. Keep the token and secret confidential (they are ignored by Git in `.gitignore`).

### API Configuration
- **Domeneshop API Documentation**: https://api.domeneshop.no/docs/
- **API Token (Client ID)**: Fill in `domeneshop_credentials.json`
- **API Secret**: Fill in `domeneshop_credentials.json`

Once filled in, we can run `update_dns.py` to automatically create/update the CNAME record `pox.ostreborg.no` pointing to the Render static site.
