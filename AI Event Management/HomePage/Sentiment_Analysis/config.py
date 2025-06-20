import random

# List of free proxies (Update regularly)
PROXIES = [
    "http://23.23.23.23:8080",
    "http://45.45.45.45:8080",
    "http://66.66.66.66:8080"
]

def get_proxies():
    return random.choice(PROXIES) if PROXIES else None
