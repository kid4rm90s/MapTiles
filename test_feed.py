import os
os.environ['DISCORD_WEBHOOK_URL'] = 'http://localhost:9999/webhook'

from waze_feed import get_latest_waze_update

try:
    get_latest_waze_update()
except Exception as e:
    print(f'Exception: {type(e).__name__}: {e}')
