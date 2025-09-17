#!/usr/bin/env python3
"""
Test script for Kelly Right Real Estate Scraper.

This script demonstrates how to use the scraper and includes sample HTML
for testing the extraction logic.
"""

from kelly_right_scraper import KellyRightScraper
from bs4 import BeautifulSoup
import json


def create_sample_agent_html():
    """Create sample HTML that mimics a real estate agent page for testing."""
    return """
    <html>
    <body>
        <div class="agent-profile">
            <h1 class="agent-name">John Smith</h1>
            <p class="agent-title">Senior Real Estate Agent</p>
            <div class="contact-info">
                <p>Phone: (555) 123-4567</p>
                <p>Email: john.smith@kellyright.com</p>
                <p>Office: (555) 987-6543</p>
                <p>Mobile: (555) 555-1234</p>
            </div>
            <div class="agent-bio">
                <p>John has been helping families find their dream homes for over 10 years. 
                He specializes in luxury homes and first-time buyers.</p>
            </div>
            <div class="specialties">
                <p>Luxury Homes, First-Time Buyers, Investment Properties</p>
            </div>
            <img class="agent-photo" src="/images/john-smith.jpg" alt="John Smith">
        </div>
        
        <div class="agent-profile">
            <h2 class="agent-name">Sarah Johnson</h2>
            <p class="agent-title">Real Estate Consultant</p>
            <div class="contact-info">
                <p>Contact Sarah at (555) 234-5678 or sarah.johnson@kellyright.com</p>
            </div>
            <div class="agent-bio">
                <p>Sarah focuses on residential sales and has excellent knowledge of local markets.</p>
            </div>
        </div>
    </body>
    </html>
    """


def test_contact_extraction():
    """Test the contact information extraction on sample HTML."""
    print("Testing contact information extraction...")
    
    # Create scraper instance
    scraper = KellyRightScraper()
    
    # Parse sample HTML
    sample_html = create_sample_agent_html()
    soup = BeautifulSoup(sample_html, 'html.parser')
    
    # Test extraction from first agent
    first_agent = soup.select_one('.agent-profile')
    contact_info = scraper.extract_contact_info(first_agent)
    
    print("\nExtracted information:")
    print(json.dumps(contact_info, indent=2))
    
    # Test extraction from listing page (multiple agents)
    agents = scraper.extract_agents_from_listing(soup)
    print(f"\nFound {len(agents)} agents from listing page:")
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent['name']} - {agent['phone']}")
    
    return agents


def test_url_discovery():
    """Test URL discovery patterns."""
    print("\nTesting URL discovery...")
    
    listing_html = """
    <html>
    <body>
        <div class="agents-list">
            <a href="/agent/john-smith" class="agent-link">John Smith</a>
            <a href="/agent/sarah-johnson" class="agent-link">Sarah Johnson</a>
            <a href="/team/mike-davis" class="team-member">Mike Davis</a>
        </div>
    </body>
    </html>
    """
    
    scraper = KellyRightScraper(base_url="https://example.com")
    soup = BeautifulSoup(listing_html, 'html.parser')
    
    agent_urls = scraper.find_agent_pages(soup)
    print(f"Discovered URLs: {agent_urls}")


def demonstrate_usage():
    """Demonstrate how to use the scraper with different configurations."""
    print("\nDemonstrating scraper usage...")
    
    # Example 1: Basic usage
    print("1. Basic scraper initialization:")
    scraper = KellyRightScraper()
    print(f"   Base URL: {scraper.base_url}")
    print(f"   Request delay: {scraper.delay}s")
    
    # Example 2: Custom configuration
    print("\n2. Custom configuration:")
    custom_scraper = KellyRightScraper(
        base_url="https://custom-kelly-right-url.com",
        delay=2.0
    )
    print(f"   Custom URL: {custom_scraper.base_url}")
    print(f"   Custom delay: {custom_scraper.delay}s")
    
    # Example 3: How to run the scraper (when website is available)
    print("\n3. How to run scraper (example - requires valid URL):")
    print("""
    # Initialize scraper with correct Kelly Right URL
    scraper = KellyRightScraper(base_url="https://www.kellyright.com")
    
    # Scrape all agents
    agents = scraper.scrape_agents()
    
    # Save results
    scraper.save_to_csv(agents, "my_agents.csv")
    scraper.save_to_json(agents, "my_agents.json")
    """)


def main():
    """Run all tests."""
    print("Kelly Right Real Estate Scraper - Test Suite")
    print("=" * 50)
    
    try:
        # Test contact extraction
        agents = test_contact_extraction()
        
        # Test URL discovery
        test_url_discovery()
        
        # Demonstrate usage
        demonstrate_usage()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("\nTo use the scraper:")
        print("1. Update the BASE_URL in scraper_config.py with the correct Kelly Right website")
        print("2. Run: python kelly_right_scraper.py")
        print("3. Check the generated CSV and JSON files for results")
        
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    main()