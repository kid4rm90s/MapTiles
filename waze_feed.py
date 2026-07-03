import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import requests
from nepali_datetime import date as nepali_date

FEED_URL = "https://storage.googleapis.com/waze-tile-build-public/release-history/intl-feed.xml"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def get_latest_waze_update():
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing.")
        raise ValueError("DISCORD_WEBHOOK_URL is not set")

    response = requests.get(FEED_URL)
    if response.status_code != 200:
        print("Failed to fetch the feed")
        raise Exception(f"Failed to fetch feed: {response.status_code}")

    namespaces = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(response.content)

    entry = root.find("atom:entry", namespaces)
    if entry is not None:
        title = entry.find("atom:title", namespaces).text
        updated_raw = entry.find("atom:updated", namespaces).text

        # 1. Handle Timezones & Timestamps
        utc_time = datetime.strptime(updated_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_time = pytz.utc.localize(utc_time)

        nepal_tz = pytz.timezone("Asia/Kathmandu")
        nepal_time = utc_time.astimezone(nepal_tz)
        formatted_nepal_time = nepal_time.strftime("%I:%M:%S %p")

        unix_timestamp = int(utc_time.timestamp())
        discord_relative_time = f"<t:{unix_timestamp}:F>"

        # 2. Extract the Map Tile Date from the Title
        # Example string: "International map tiles were successfully updated to: 2026-07-02T05:55:18"
        date_match = re.search(r"\d{4}-\d{2}-\d{2}", title)

        nepali_bs_date = "Conversion Error"
        if date_match:
            ad_date_str = date_match.group(0)  # e.g., "2026-07-02"
            ad_year, ad_month, ad_day = map(int, ad_date_str.split("-"))

            try:
                # Convert Gregorian (AD) to Nepali (BS) using nepali_datetime
                ad_date_obj = datetime(ad_year, ad_month, ad_day)
                nepali_dt = nepali_date.from_gregorian_date(ad_date_obj.date())
                # Formats to something like "2083-03-18"
                nepali_bs_date = f"{nepali_dt.year}-{nepali_dt.month:02d}-{nepali_dt.day:02d}"
            except Exception as e:
                print(f"Conversion failed: {e}")
                nepali_bs_date = ad_date_str

        # 3. Construct the Message Layout
        message = (
            f"**Waze Map Tile Update Status**\n"
            f"📌 **Status:** {title}\n"
            f"📅 **Nepali Date (BS):** `{nepali_bs_date}`\n"
            f"🇳🇵 **Nepal Time (NST):** `{formatted_nepal_time}`\n"
            f"🌐 **Dynamic Time:** {discord_relative_time}"
        )

        requests.post(WEBHOOK_URL, json={"content": message})
        print("Update sent to Discord successfully!")


if __name__ == "__main__":
    try:
        get_latest_waze_update()
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)