import requests
import re

# Fetch the library
url = 'https://kid4rm90s.github.io/NepaliBStoAD/NepaliBStoAD.js'
response = requests.get(url)
text = response.text

# Find the BSMonths array
start_idx = text.find('var BSMonths = [')
end_idx = text.find('];', start_idx) + 2

bsmonths_str = text[start_idx:end_idx]

# Extract individual year data
year_pattern = r'\[([^\]]+)\](?:,\s*//\s*(\d+)|$)'
matches = re.findall(year_pattern, bsmonths_str)

# Print years 2082 and 2083
print("Extracted calendar data from library:")
print("-" * 60)

for i, (data, year) in enumerate(matches):
    year_num = 2000 + i
    if year_num >= 2082 and year_num <= 2083:
        # Parse the month data
        months = [int(x.strip()) for x in data.split(',')]
        total_days = sum(months)
        print(f"\n2082" if year_num == 2082 else f"2083" if year_num == 2083 else f"\n{year_num}")
        print(f"Year {year_num}: {months}")
        print(f"Total days: {total_days}")
