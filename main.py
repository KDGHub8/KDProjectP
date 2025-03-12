import os
import requests
from bs4 import BeautifulSoup
import time

# The URL you want to track
URL = "https://www.bigw.com.au/toys/board-games-puzzles/trading-cards/pokemon-trading-cards/c/681510201"

# The interval between checks (in seconds)
CHECK_INTERVAL = 10  # Check every 10 seconds

# How long the script will run (in seconds)
RUN_TIME = 10 * 60  # 10 minutes in seconds

# Your Discord Webhook URL (using environment variable)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Your Discord user ID
DISCORD_USER_ID = "294034227081773056"  # Your personal Discord User ID

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

    # Include your Discord user ID to mention yourself
    message_with_ping = f"<@{DISCORD_USER_ID}> {message}"

    data = {
        "content": message_with_ping
    }
    
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


def track_item_count():
    """Track the item count and send notifications if it changes."""
    page_content = fetch_page(URL)
    if page_content:
        initial_item_count = extract_item_count(page_content)
        print(f"Initial item count: {initial_item_count}")
        send_discord_notification(f"Initial item count: {initial_item_count}")

        start_time = time.time()
        while time.time() - start_time < RUN_TIME:
            time.sleep(CHECK_INTERVAL)  # Wait before checking again

            page_content = fetch_page(URL)
            if page_content:
                new_item_count = extract_item_count(page_content)
                print(f"Checked item count: {new_item_count}")

                # Send notification only if item count has increased from the initial count
                if new_item_count > initial_item_count:
                    print(f"Item count increased to: {new_item_count}")
                    send_discord_notification(f"Item count increased to: {new_item_count} items on the page!")
                    initial_item_count = new_item_count  # Update the count

if __name__ == "__main__":
    track_item_count()
