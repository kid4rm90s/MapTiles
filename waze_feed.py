import os
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import requests

FEED_URL = "https://storage.googleapis.com/waze-tile-build-public/release-history/intl-feed.xml"

# Read the webhook from environment variables safely
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def get_latest_waze_update():
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
        return

    response = requests.get(FEED_URL)
    if response.status_code != 200:
        print("Failed to fetch the feed")
        return

    namespaces = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(response.content)

    entry = root.find("atom:entry", namespaces)
    if entry is not None:
        title = entry.find("atom:title", namespaces).text
        updated_raw = entry.find("atom:updated", namespaces).text

        # Parse UTC time
        utc_time = datetime.strptime(updated_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_time = pytz.utc.localize(utc_time)

        # Convert to Nepal Time
        nepal_tz = pytz.timezone("Asia/Kathmandu")
        nepal_time = utc_time.astimezone(nepal_tz)
        formatted_nepal_time = nepal_time.strftime("%Y-%m-%d %I:%M:%S %p")

        # Discord Dynamic Time formatting
        unix_timestamp = int(utc_time.timestamp())
        discord_relative_time = f"<t:{unix_timestamp}:F> (<t:{unix_timestamp}:R>)"

        message = (
            f"**Waze Map Tile Update Status**\n"
            f"📌 **Status:** {title}\n"
            f"🇳🇵 **Nepal Time (NST):** `{formatted_nepal_time}`\n"
            f"🌐 **Your Local Time:** {discord_relative_time}"
        )

        requests.post(WEBHOOK_URL, json={"content": message})
        print("Update sent to Discord successfully!")


if __name__ == "__main__":
    get_latest_waze_update()