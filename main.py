import os
import requests
from bs4 import BeautifulSoup
import time
import json

# The URL to track
URL = "https://www.bigw.com.au/toys/board-games-puzzles/trading-cards/pokemon-trading-cards/c/681510201"

# Your Discord Webhook URL (using environment variable)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
# Your Discord user ID for pinging
DISCORD_USER_ID = "<@294034227081773056>"  # Replace with your Discord user ID

# Path to store the last known item count between runs (persistent storage)
LAST_ITEM_COUNT_FILE = "/tmp/last_item_count.json"

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

def send_discord_notification(message, ping=False):
    """Send a notification to Discord, with optional ping."""
    if DISCORD_WEBHOOK_URL is None:
        print("Error: Discord Webhook URL not set!")
        return

    if ping:
        message = f"{DISCORD_USER_ID} {message}"  # Ping user only if specified

    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification: {response.status_code}")

def extract_item_count(page_content):
    """Extract the item count from the page."""
    soup = BeautifulSoup(page_content, "html.parser")
    item_count_element = soup.find("div", {"id": "search-results-count"})
    if item_count_element:
        item_count = item_count_element.get_text(strip=True).split()[0]  # Extract number only
        # Clean the string to remove any non-numeric characters
        item_count = ''.join(filter(str.isdigit, item_count))
        if item_count:
            return int(item_count)
    return 0

def load_last_item_count():
    """Load the last known item count from a file (if it exists)."""
    if os.path.exists(LAST_ITEM_COUNT_FILE):
        with open(LAST_ITEM_COUNT_FILE, 'r') as f:
            return json.load(f)
    return {"item_count": 0}  # Default to 0 if file doesn't exist

def save_last_item_count(item_count):
    """Save the current item count to a file."""
    with open(LAST_ITEM_COUNT_FILE, 'w') as f:
        json.dump({"item_count": item_count}, f)

def track_item_count():
    """Track item count and notify if the count increases."""
    # Record the start time for timeout
    start_time = time.time()

    # Fetch the page content
    page_content = fetch_page(URL)
    if not page_content:
        print("Error: Failed to fetch the page content.")
        return

    # Extract the initial item count
    initial_item_count = extract_item_count(page_content)
    print(f"Initial item count: {initial_item_count}")

    # Load the last known item count
    last_item_count_data = load_last_item_count()
    last_item_count = last_item_count_data.get("item_count", 0)

    # Send initial item count message (NO ping)
    send_discord_notification(f"Initial item count: {initial_item_count}")

    # Loop with timeout check (10 minutes = 600 seconds)
    while time.time() - start_time <= 600:
        # Fetch updated page content
        page_content = fetch_page(URL)
        if not page_content:
            print("Error: Failed to fetch the page content.")
            return

        # Extract the current item count
        current_item_count = extract_item_count(page_content)
        print(f"Updated item count: {current_item_count}")

        # If the item count increased, send a ping
        if current_item_count > last_item_count:
            send_discord_notification(f"The item count has increased! New count: {current_item_count} results.", ping=True)
            last_item_count = current_item_count  # Update last known item count
            save_last_item_count(current_item_count)  # Persist the new count

        # Sleep for 30 seconds to avoid spamming requests
        time.sleep(30)

    # Send final item count message (NO ping)
    send_discord_notification(f"Final item count: {last_item_count}")
    print(f"Final item count: {last_item_count}")

if __name__ == "__main__":
    track_item_count()
