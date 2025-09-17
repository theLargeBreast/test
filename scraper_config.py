"""
Configuration file for Kelly Right Real Estate Scraper.

Update the BASE_URL with the correct Kelly Right domain once identified.
You can also customize other scraping parameters here.
"""

# Website Configuration
BASE_URL = "https://www.kellyright.com"  # Update with correct URL
ALTERNATIVE_URLS = [
    "https://kellyright.com",
    "https://www.kellyrightrealestate.com", 
    "https://kellyrightrealty.com"
]

# Scraping Configuration
DELAY_BETWEEN_REQUESTS = 1.0  # Seconds
REQUEST_TIMEOUT = 30  # Seconds
MAX_RETRIES = 3

# Output Configuration
DEFAULT_CSV_FILENAME = "kelly_right_agents.csv"
DEFAULT_JSON_FILENAME = "kelly_right_agents.json"

# Common agent page paths to try
AGENT_PATHS = [
    "/agents",
    "/team", 
    "/realtors",
    "/professionals",
    "/about/team",
    "/our-team",
    "/staff",
    "/meet-the-team"
]

# User Agent for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"