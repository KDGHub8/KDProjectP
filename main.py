import os
import requests
from bs4 import BeautifulSoup
import time

# The URLs you want to track
URLS = [
    "https://www.bigw.com.au/product/powerful-deluxe-hardcover-edition-by-lauren-roberts/p/6019808",
    "https://www.bigw.com.au/product/pok-mon-tcg-scarlet-violet-surging-sparks-blister-pack-assorted-/p/52352",
    "https://www.bigw.com.au/product/pokemon-tcg-blooming-waters-premium-collection/p/6019662",
    "https://www.bigw.com.au/product/pokemon-tcg-legendary-warriors-premium-collection/p/6019661",
    "https://www.bigw.com.au/product/pokemon-tcg-scarlet-violet-prismatic-evolutions-super-premium-collection/p/6019663",
    "https://www.bigw.com.au/product/pokemon-tcg-scarlet-violet-journey-together-three-booster-blister-assorted-/p/6013488",
    "https://www.bigw.com.au/product/pokemon-tcg-scarlet-violet-journey-together-booster-display/p/6013603"
]

# The interval between checks (in seconds)
CHECK_INTERVAL = 10  # Check every 10 seconds

# How long the script will run (in seconds)
RUN_TIME = 10 * 60  # 10 minutes in seconds

# Your Discord Webhook URL (using environment variable)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def fetch_page(url):
    """Fetch the page content."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def send_discord_notification(message):
    """Send a notification to Discord."""
    if DISCORD_WEBHOOK_URL is None:
        print("Error: Discord Webhook URL not set!")
        return

    data = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification: {response.status_code}")

def check_add_to_cart_or_preorder(page_content):
    """Check if the 'Add to Cart' or 'Pre-order' button is available."""
    soup = BeautifulSoup(page_content, "html.parser")
    
    # Check if 'Add to Cart' button is available
    add_to_cart_button = soup.find("button", {"data-di-id": "pdp--add-to-cart"})
    
    # Check if 'Pre-order' button is available
    preorder_button = soup.find("button", {"data-di-id": "pdp--add-to-cart", "class": "Button variant-primary Button_Button__VboAj Button_variantPrimary___5_8N"})
    
    if add_to_cart_button:
        return "Add to Cart"
    elif preorder_button:
        return "Pre-order"
    return None

def track_add_to_cart_or_preorder():
    """Track when 'Add to Cart' or 'Pre-order' button becomes available on the product pages."""
    initial_availability = {url: None for url in URLS}

    # Run the tracking process for 10 minutes
    start_time = time.time()
    while time.time() - start_time < RUN_TIME:
        for url in URLS:
            page_content = fetch_page(url)
            if page_content:
                button_status = check_add_to_cart_or_preorder(page_content)
                if button_status and initial_availability[url] != button_status:
                    print(f"'{button_status}' is now available: {url}")
                    send_discord_notification(f"'{button_status}' is now available on {url}")
                    initial_availability[url] = button_status
                elif not button_status and initial_availability[url]:
                    print(f"'{initial_availability[url]}' is no longer available: {url}")
                    send_discord_notification(f"'{initial_availability[url]}' is no longer available on {url}")
                    initial_availability[url] = None
        time.sleep(CHECK_INTERVAL)  # Wait 10 seconds before checking again

if __name__ == "__main__":
    track_add_to_cart_or_preorder()
