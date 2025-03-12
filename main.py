import os
import requests
from bs4 import BeautifulSoup

# The URL to track
URL = "https://www.bigw.com.au/toys/board-games-puzzles/trading-cards/pokemon-trading-cards/c/681510201"

# Your Discord Webhook URL (using environment variable)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
# Your Discord user ID for pinging
DISCORD_USER_ID = "<@294034227081773056>"  # Replace with your Discord user ID

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
    """Track item count and notify if the count increases."""
    # Fetch the page content
    page_content = fetch_page(URL)
    if not page_content:
        print("Error: Failed to fetch the page content.")
        return

    # Get the initial item count
    initial_item_count = extract_item_count(page_content)
    print(f"Initial item count: {initial_item_count}")
    
    # Send the initial count to Discord (no ping)
    send_discord_notification(f"Initial item count: {initial_item_count} results found on the page.")

    # Track changes in item count
    previous_item_count = initial_item_count

    # You can adjust the check interval (e.g., every 60 seconds or based on your needs)
    import time
    while True:
        time.sleep(60)  # Sleep for 1 minute before checking again

        # Fetch the page content again
        page_content = fetch_page(URL)
        if not page_content:
            print("Error: Failed to fetch the page content.")
            continue

        # Extract current item count
        current_item_count = extract_item_count(page_content)
        print(f"Current item count: {current_item_count}")

        # If the item count increased, send a ping
        if current_item_count > previous_item_count:
            send_discord_notification(f"{DISCORD_USER_ID} The item count has increased! New count: {current_item_count} results.")
            previous_item_count = current_item_count  # Update previous count
        else:
            print("Item count has not increased.")
        
if __name__ == "__main__":
    track_item_count()
