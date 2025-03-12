import os
import requests
import time

# The URLs you want to track
URLS = [
    "https://www.bbc.com/news",
    "https://www.bigw.com.au/toys/board-games-puzzles/trading-cards/pokemon-trading-cards/c/681510201"
]

# The interval between checks (in seconds)
CHECK_INTERVAL = 10  # Check every 10 seconds

# How long the script will run (in seconds)
RUN_TIME = 10 * 60  # 10 minutes in seconds

# This will hold the previous page content to detect updates
LAST_PAGE_CONTENT = {}

# Your Discord Webhook URL (using environment variable)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def fetch_page(url):
    """Fetch the content of the page and return it if status is OK."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def send_discord_notification(url, message):
    """Send a notification to Discord when page is updated."""
    if DISCORD_WEBHOOK_URL is None:
        print("Error: Discord Webhook URL not set!")
        return

    data = {
        "content": f"{message} {url}"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Notification sent successfully.")
    else:
        print(f"Failed to send notification: {response.status_code}")

def track_updates():
    """Track updates for the URLs and notify if content changes."""
    # Set up the initial content check for each URL
    for url in URLS:
        LAST_PAGE_CONTENT[url] = fetch_page(url)

    # Run the tracking process for 10 minutes
    start_time = time.time()
    while time.time() - start_time < RUN_TIME:
        for url in URLS:
            current_page = fetch_page(url)
            if current_page and current_page != LAST_PAGE_CONTENT[url]:
                print(f"Page updated: {url}")
                send_discord_notification(url, "The tracked page has been updated!")
                LAST_PAGE_CONTENT[url] = current_page
        time.sleep(CHECK_INTERVAL)  # Wait 10 seconds before checking again

if __name__ == "__main__":
    track_updates()
