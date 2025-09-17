#!/usr/bin/env python3
"""
Example usage of the Kelly Right Real Estate Scraper.

This script shows how to use the scraper in a real scenario.
"""

from kelly_right_scraper import KellyRightScraper
import scraper_config


def main():
    """Example of how to use the Kelly Right scraper."""
    
    print("Kelly Right Real Estate Scraper - Example Usage")
    print("=" * 50)
    
    # Initialize scraper with configuration
    scraper = KellyRightScraper(
        base_url=scraper_config.BASE_URL,
        delay=scraper_config.DELAY_BETWEEN_REQUESTS
    )
    
    print(f"Scraping from: {scraper.base_url}")
    print(f"Request delay: {scraper.delay} seconds")
    print()
    
    try:
        # Method 1: Auto-discover agent pages
        print("Method 1: Auto-discovering agent pages...")
        agents = scraper.scrape_agents()
        
        if agents:
            print(f"✅ Found {len(agents)} agents")
            
            # Save results
            scraper.save_to_csv(agents, scraper_config.DEFAULT_CSV_FILENAME)
            scraper.save_to_json(agents, scraper_config.DEFAULT_JSON_FILENAME)
            
            # Display sample results
            print("\nSample agents found:")
            for i, agent in enumerate(agents[:3], 1):  # Show first 3
                print(f"{i}. {agent['name']} - {agent['title']}")
                if agent['phone']:
                    print(f"   Phone: {agent['phone']}")
                if agent['email']:
                    print(f"   Email: {agent['email']}")
                print()
            
            if len(agents) > 3:
                print(f"... and {len(agents) - 3} more agents")
                
        else:
            print("❌ No agents found")
            
            # Try alternative approach with specific URLs
            print("\nTrying alternative approach with specific URLs...")
            
            # Method 2: Try specific known paths
            specific_urls = []
            for path in scraper_config.AGENT_PATHS:
                specific_urls.append(scraper.base_url + path)
            
            agents = scraper.scrape_agents(start_urls=specific_urls)
            
            if agents:
                print(f"✅ Found {len(agents)} agents using specific URLs")
                scraper.save_to_csv(agents)
                scraper.save_to_json(agents)
            else:
                print("❌ No agents found with specific URLs either")
                print("\nPossible reasons:")
                print("1. The website URL might be incorrect")
                print("2. The website structure might be different than expected")
                print("3. The website might require JavaScript rendering")
                print("4. The website might be blocking automated requests")
                
                print(f"\nPlease verify the website URL: {scraper.base_url}")
                print("Update scraper_config.py with the correct URL if needed.")
    
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the website URL is correct")
        print("3. Check if the website is accessible in a browser")
        print("4. Review the scraper logs for more details")


if __name__ == "__main__":
    main()