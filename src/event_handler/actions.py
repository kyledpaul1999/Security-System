
import requests

def send_webhook(url, payload):
    """
    Sends a POST request to the specified URL with the given payload.
    """
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status() # Raise an exception for non-2xx status codes
        print(f"Successfully sent webhook to {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook to {url}: {e}")
