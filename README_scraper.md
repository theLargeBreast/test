# Kelly Right Real Estate Scraper

This is a comprehensive web scraper designed to extract realtor contact information from Kelly Right Real Estate's website. The scraper can collect agent names, phone numbers, email addresses, titles, biographies, and specialties.

## Features

- **Comprehensive Contact Extraction**: Extracts names, titles, phone numbers (office/mobile), email addresses, biographies, and specialties
- **Flexible URL Discovery**: Automatically finds agent pages from directory listings
- **Multiple Output Formats**: Saves data to both CSV and JSON formats
- **Respectful Scraping**: Includes delays between requests and proper user agent headers
- **Error Handling**: Robust error handling and logging
- **Configurable**: Easy to customize for different website structures

## Files

- `kelly_right_scraper.py` - Main scraper class and functionality
- `scraper_config.py` - Configuration file with website URLs and settings
- `test_scraper.py` - Test suite with sample data and usage examples
- `README_scraper.md` - This documentation file

## Installation

1. Ensure you have Python 3.6+ installed
2. Install required dependencies:
```bash
pip install requests beautifulsoup4 lxml
```

## Configuration

Before running the scraper, update the `scraper_config.py` file with the correct Kelly Right Real Estate website URL:

```python
BASE_URL = "https://www.kellyright.com"  # Update with actual URL
```

## Usage

### Basic Usage

```python
from kelly_right_scraper import KellyRightScraper

# Initialize scraper
scraper = KellyRightScraper(base_url="https://www.kellyright.com")

# Scrape all agents
agents = scraper.scrape_agents()

# Save results
scraper.save_to_csv(agents, "kelly_right_agents.csv")
scraper.save_to_json(agents, "kelly_right_agents.json")

print(f"Found {len(agents)} agents")
```

### Command Line Usage

```bash
python kelly_right_scraper.py
```

### Custom Configuration

```python
# Custom delay and URL
scraper = KellyRightScraper(
    base_url="https://custom-url.com", 
    delay=2.0  # 2 second delay between requests
)
```

### Specific Pages

```python
# Scrape from specific starting URLs
start_urls = [
    "https://www.kellyright.com/agents",
    "https://www.kellyright.com/team"
]
agents = scraper.scrape_agents(start_urls=start_urls)
```

## Output Format

### CSV Output
The scraper generates a CSV file with the following columns:
- name
- title  
- phone
- email
- office_phone
- mobile_phone
- bio
- specialties
- url
- image_url

### JSON Output
The JSON output contains the same information in a structured format with specialties as an array.

## Testing

Run the test suite to verify functionality:

```bash
python test_scraper.py
```

The test suite includes:
- Contact information extraction testing
- URL discovery testing  
- Usage demonstrations

## Customization

### Adding New Selectors

To adapt the scraper for different website structures, modify the selector lists in the `extract_contact_info` method:

```python
# Add new selectors for agent names
name_selectors = [
    '.agent-name', '.realtor-name', '.name', 
    '.your-custom-selector'  # Add your selector here
]
```

### Adding New Fields

To extract additional information, add new fields to the `contact_info` dictionary in `extract_contact_info`:

```python
contact_info = {
    'name': '',
    'title': '',
    # ... existing fields ...
    'license_number': '',  # New field
    'years_experience': ''  # New field
}
```

## Best Practices

1. **Respect robots.txt**: Check the website's robots.txt file before scraping
2. **Use delays**: The scraper includes delays between requests to avoid overwhelming the server
3. **Handle errors**: Always handle network errors and missing data gracefully
4. **Update User-Agent**: Use a realistic user agent string
5. **Monitor for changes**: Website structures can change, requiring scraper updates

## Troubleshooting

### No agents found
- Verify the base URL is correct
- Check if the website structure has changed
- Review the console logs for specific errors
- Test with `test_scraper.py` to verify extraction logic

### Connection errors
- Verify internet connectivity
- Check if the website is accessible
- Ensure the URL format is correct (http/https)

### Missing contact information
- The website might use different HTML selectors
- Update the selector lists in the scraper
- Check if information is loaded via JavaScript (may need Selenium)

## Legal Considerations

- Always respect the website's Terms of Service
- Check robots.txt file for scraping permissions
- Consider rate limiting to avoid overloading servers
- Be mindful of copyright and data protection laws
- Use scraped data responsibly and ethically

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify the website URL and structure
3. Run the test suite to isolate the problem
4. Update selectors if the website structure has changed

## Example Output

```json
[
  {
    "name": "John Smith",
    "title": "Senior Real Estate Agent", 
    "phone": "(555) 123-4567",
    "email": "john.smith@kellyright.com",
    "office_phone": "(555) 987-6543",
    "mobile_phone": "(555) 555-1234",
    "bio": "John has been helping families find their dream homes...",
    "specialties": ["Luxury Homes", "First-Time Buyers"],
    "url": "https://www.kellyright.com/agent/john-smith",
    "image_url": "https://www.kellyright.com/images/john-smith.jpg"
  }
]
```