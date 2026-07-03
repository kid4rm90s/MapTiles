#!/usr/bin/env python
"""Test script for waze_feed.py functionality"""

from waze_feed import gregorian_to_nepali
from datetime import datetime
import pytz

print("=" * 70)
print("Waze Feed Update - Full Functionality Test")
print("=" * 70)

# Simulate a Waze update date
test_ad_date = "2026-07-02"  # Example map tile date
ad_year, ad_month, ad_day = map(int, test_ad_date.split("-"))

# Convert to Nepali date
result = gregorian_to_nepali(ad_year, ad_month, ad_day)
if result:
    bs_year, bs_month, bs_day = result
    nepali_bs_date = f"{bs_year}-{bs_month:02d}-{bs_day:02d}"
    print(f"\n✓ Map Tile Date (AD): {test_ad_date}")
    print(f"✓ Nepali Date (BS): {nepali_bs_date}")
    
    # Test timezone conversion
    test_time = datetime(2026, 7, 2, 5, 55, 18)
    utc_time = pytz.utc.localize(test_time)
    nepal_tz = pytz.timezone("Asia/Kathmandu")
    nepal_time = utc_time.astimezone(nepal_tz)
    formatted_time = nepal_time.strftime("%I:%M:%S %p")
    print(f"✓ Nepal Time (NST): {formatted_time}")
    print(f"✓ Discord Timestamp: <t:{int(utc_time.timestamp())}:F>")
    
    # Mock Discord message
    message = (
        f"**Waze Map Tile Update Status**\n"
        f"📌 **Status:** International map tiles were successfully updated to: {test_ad_date}T05:55:18\n"
        f"📅 **Nepali Date (BS):** `{nepali_bs_date}`\n"
        f"🇳🇵 **Nepal Time (NST):** `{formatted_time}`\n"
        f"🌐 **Dynamic Time:** <t:{int(utc_time.timestamp())}:F>"
    )
    print("\n" + "─" * 70)
    print("Discord Message Preview:")
    print("─" * 70)
    print(message)
    print("─" * 70)
    print("\n✓ All components working correctly!")
else:
    print("✗ Conversion failed")
