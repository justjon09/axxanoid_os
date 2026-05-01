import urllib.request
import urllib.error

def run_api_autid():
    alerts = []

    # Operational endpoints
    operational_endpoints = {
        "Ollama_Inference": "http://127.0.0.1:11434"
        # We can add the React UI port (5173) here later
    }

    for name, url in operational_endpoints.items():
        try:
            # 2-second timeout ping
            req = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(req, timeout=2)
        except urllib.error.URLError:
            alerts.append(f"CRITICAL OPERATIONAL API OFFLINE: {name} at {url} is unreachable. Is the service running?")
        except Exception as e:
            alerts.append(f"API ERROR: {name} returned error: {str(e)}")

    production_endpoints = {
        # Shopify 
        # Google - Full IAM 
        #   calendar
        #   mail
        #   business suite
        #   Cloud
        #   Analytics
        # Meta
        # TikTok
        # Etsy
        # Pinterest
        # Printful
        # Roastify
        # CJ Dropshipping
        # Custom WP for Average Stoner
        # Custom WP for Axxanoid Studios
        # more as needed
    }

    for name, url in production_endpoints.items():
        try:
            # 2-second timeout ping
            req = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(req, timeout=2)
        except urllib.error.URLError:
            alerts.append(f"PRODUCTION API OFFLINE: {name} at {url} is unreachable. Are creditials set up correctly?")
        except Exception as e:
            alerts.append(f"API ERROR: {name} returned error: {str(e)}")
            
    if alerts:
        for alert in alerts:
            print(alert)

if __name__ == "__main__":
    run_api_autid()