import requests
from bs4 import BeautifulSoup
import time
import os

# The URL you want to track
URL = "https://www.bigw.com.au/toys/board-games-puzzles/trading-cards/pokemon-trading-cards/c/681510201"

# Interval between checks (in seconds)
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

def extract_item_count(page_content):
    """Extract the item count from the search results."""
    soup = BeautifulSoup(page_content, "html.parser")
    
    # Find the element containing the result count (e.g., '61 results')
    result_count_element = soup.find("div", {"id": "search-results-count"})
    
    if result_count_element:
        result_text = result_count_element.get_text(strip=True)
        # Extract the numeric value from the text
        item_count = result_text.split()[0]  # Take the first part of the text (before 'results')
        return int(item_count)
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

def track_item_count():
    """Track the number of items on the page."""
    previous_item_count = None
    start_time = time.time()

    # Initial item count at the start
    page_content = fetch_page(URL)
    if page_content:
        initial_item_count = extract_item_count(page_content)
        if initial_item_count is not None:
            print(f"Initial item count: {initial_item_count}")
        else:
            print("Item count not found at the start.")
            return  # Exit if the initial count can't be fetched
    else:
        print("Failed to fetch page content at the start.")
        return  # Exit if the page couldn't be fetched
    
    while time.time() - start_time < RUN_TIME:
        page_content = fetch_page(URL)
        if page_content:
            item_count = extract_item_count(page_content)
            if item_count:
                print(f"Current item count: {item_count}")
                
                # Send a notification only if the item count has increased
                if previous_item_count is None:
                    previous_item_count = item_count
                elif item_count > previous_item_count:
                    message = f"The number of items has increased to {item_count} on {URL}!"
                    print(message)
                    send_discord_notification(message)
                    previous_item_count = item_count
            else:
                print("Item count not found.")
        
        time.sleep(CHECK_INTERVAL)  # Wait before checking again
    
    # Final item count at the end
    if page_content:
        final_item_count = extract_item_count(page_content)
        if final_item_count is not None:
            print(f"Final item count: {final_item_count}")
        else:
            print("Item count not found at the end.")
    else:
        print("Failed to fetch page content at the end.")

if __name__ == "__main__":
    track_item_count()
