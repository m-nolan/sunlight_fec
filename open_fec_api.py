import requests as req

from ratelimit import limits, sleep_and_retry

# 1000 calls per hour, or 50 in 3 minutes. Makes pauses less intrusive.
# Day-to-day donations should not be massive for each committee, and each API
# call returns up to 100 receipts.
MAX_CALLS = 5
PERIOD = 16 # seconds

@sleep_and_retry
@limits(MAX_CALLS,PERIOD)
def api_get(url):
    r = req.get(url)
    if r.status_code != 200:
        print(f'ERROR: Status Code {r.status_code} ({r.reason})')
        r.raise_for_status()
    else:
        return r
    
#TODO: add method to check if you're already at the limit!