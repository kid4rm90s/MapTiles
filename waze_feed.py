import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
import requests

FEED_URL = "https://storage.googleapis.com/waze-tile-build-public/release-history/intl-feed.xml"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Nepali calendar data (days per month for each BS year 2000-2099)
# Source: NepaliBStoAD.js library (https://kid4rm90s.github.io/NepaliBStoAD/NepaliBStoAD.js)
# Reference: AD 1944-01-01 = BS 2000-09-17
BS_MONTHS = [
    [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2000
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2001
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2002
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2003
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30], # 2004
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2005
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2006
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2007
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30], # 2008
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2009
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2010
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2011
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30], # 2012
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2013
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2014
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2015
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30], # 2016
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2017
    [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2018
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2019
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2020
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2021
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30], # 2022
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2023
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2024
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2025
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2026
    [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2027
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2028
    [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30], # 2029
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2030
    [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2031
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2032
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2033
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2034
    [30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31], # 2035
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2036
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2037
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2038
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30], # 2039
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2040
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2041
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2042
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2043
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2044
    [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2045
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2046
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2047
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2048
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30], # 2049
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2050
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2051
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2052
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30], # 2053
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2054
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2055
    [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30], # 2056
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2057
    [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2058
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2059
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2060
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2061
    [30, 32, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31], # 2062
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2063
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2064
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2065
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31], # 2066
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2067
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2068
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2069
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30], # 2070
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2071
    [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2072
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2073
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2074
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2075
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30], # 2076
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2077
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2078
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2079
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30], # 2080
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31], # 2081
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2082
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2083
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2084
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 30, 29, 31], # 2085
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2086
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2087
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2088
    [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30], # 2089
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2090
    [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2091
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2092
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2093
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2094
    [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30], # 2095
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31], # 2096
    [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30], # 2097
    [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30], # 2098
    [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30], # 2099
]


def gregorian_to_nepali(ad_year, ad_month, ad_day):
    """Convert AD date to BS date using NepaliBStoAD algorithm."""
    try:
        # Reference point: AD 1944-01-01 = BS 2000-09-17
        ref_ad = datetime(1944, 1, 1)
        ad_date = datetime(ad_year, ad_month, ad_day)
        
        # Calculate days difference
        days_diff = (ad_date - ref_ad).days
        
        # Start from reference BS date
        bs_year, bs_month, bs_day = 2000, 9, 17
        
        # Add days to BS date
        while days_diff > 0:
            if bs_year < 2000 or bs_year > 2099:
                print(f"Warning: Year {bs_year} out of supported range (2000-2099)")
                break
            
            year_idx = bs_year - 2000
            if year_idx >= len(BS_MONTHS):
                print(f"Warning: Year index {year_idx} out of range")
                break
            
            if bs_month < 1 or bs_month > 12:
                print(f"Error: Invalid month {bs_month}")
                return None
            
            days_in_month = BS_MONTHS[year_idx][bs_month - 1]
            days_left = days_in_month - bs_day + 1
            
            if days_diff >= days_left:
                days_diff -= days_left
                bs_day = 1
                bs_month += 1
                if bs_month > 12:
                    bs_month = 1
                    bs_year += 1
            else:
                bs_day += days_diff
                days_diff = 0
        
        return bs_year, bs_month, bs_day
    except Exception as e:
        print(f"Conversion error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None


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
            print(f"[LOG] Extracted AD date: {ad_date_str}", flush=True)
            
            try:
                ad_year, ad_month, ad_day = map(int, ad_date_str.split("-"))
                print(f"[LOG] Parsed values - Year: {ad_year}, Month: {ad_month}, Day: {ad_day}", flush=True)
            except Exception as e:
                print(f"[ERROR] Failed to parse date: {e}", flush=True)
                nepali_bs_date = ad_date_str
            else:
                # Convert Gregorian (AD) to Nepali (BS)
                print(f"[LOG] Calling gregorian_to_nepali({ad_year}, {ad_month}, {ad_day})", flush=True)
                result = gregorian_to_nepali(ad_year, ad_month, ad_day)
                print(f"[LOG] Conversion result: {result}", flush=True)
                
                if result:
                    bs_year, bs_month, bs_day = result
                    nepali_bs_date = f"{bs_year}-{bs_month:02d}-{bs_day:02d}"
                    print(f"[LOG] Nepali date: {nepali_bs_date}", flush=True)
                else:
                    print(f"[ERROR] Conversion returned None for date {ad_date_str}", flush=True)
                    nepali_bs_date = f"[ERROR: Conversion failed]"

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
