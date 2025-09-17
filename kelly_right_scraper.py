#!/usr/bin/env python3
"""
Kelly Right Real Estate Scraper

This script scrapes realtor contact information from Kelly Right Real Estate website.
It extracts agent names, phone numbers, email addresses, and other contact details.
"""

import requests
import json
import time
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import logging
from typing import Dict, List, Optional


class KellyRightScraper:
    """
    A comprehensive scraper for Kelly Right Real Estate agent contact information.
    """
    
    def __init__(self, base_url: str = "https://www.kellyright.com", delay: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            base_url: Base URL of the Kelly Right website
            delay: Delay between requests in seconds to be respectful
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Pattern for extracting contact information
        self.phone_pattern = re.compile(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a webpage and return BeautifulSoup object.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_contact_info(self, soup: BeautifulSoup, agent_url: str = "") -> Dict:
        """
        Extract contact information from agent page or section.
        
        Args:
            soup: BeautifulSoup object of the page
            agent_url: URL of the agent page
            
        Returns:
            Dictionary containing contact information
        """
        contact_info = {
            'name': '',
            'title': '',
            'phone': '',
            'email': '',
            'office_phone': '',
            'mobile_phone': '',
            'bio': '',
            'specialties': [],
            'url': agent_url,
            'image_url': ''
        }
        
        # Extract name (common selectors for real estate sites)
        name_selectors = [
            '.agent-name', '.realtor-name', '.name', '.agent-title',
            'h1', 'h2', '.profile-name', '.contact-name'
        ]
        
        for selector in name_selectors:
            name_element = soup.select_one(selector)
            if name_element:
                contact_info['name'] = name_element.get_text().strip()
                break
        
        # Extract title/position
        title_selectors = [
            '.agent-title', '.title', '.position', '.job-title',
            '.realtor-title', '.agent-position'
        ]
        
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                contact_info['title'] = title_element.get_text().strip()
                break
        
        # Extract all text content for phone/email extraction
        page_text = soup.get_text()
        
        # Extract phone numbers
        phones = self.phone_pattern.findall(page_text)
        if phones:
            # First phone is usually primary
            contact_info['phone'] = phones[0]
            # Look for mobile/office keywords
            for phone in phones:
                if 'mobile' in page_text.lower() or 'cell' in page_text.lower():
                    contact_info['mobile_phone'] = phone
                elif 'office' in page_text.lower():
                    contact_info['office_phone'] = phone
        
        # Extract email addresses
        emails = self.email_pattern.findall(page_text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract bio/description
        bio_selectors = [
            '.bio', '.description', '.about', '.agent-bio',
            '.profile-description', '.agent-description'
        ]
        
        for selector in bio_selectors:
            bio_element = soup.select_one(selector)
            if bio_element:
                contact_info['bio'] = bio_element.get_text().strip()
                break
        
        # Extract specialties
        specialty_selectors = [
            '.specialties', '.expertise', '.areas', '.services'
        ]
        
        for selector in specialty_selectors:
            specialty_elements = soup.select(selector)
            for element in specialty_elements:
                specialties = [item.strip() for item in element.get_text().split(',')]
                contact_info['specialties'].extend(specialties)
        
        # Extract image URL
        img_selectors = [
            '.agent-photo img', '.profile-image img', '.headshot img',
            '.agent-image img', '.realtor-photo img'
        ]
        
        for selector in img_selectors:
            img_element = soup.select_one(selector)
            if img_element and img_element.get('src'):
                img_url = img_element['src']
                # Convert relative URLs to absolute
                contact_info['image_url'] = urljoin(self.base_url, img_url)
                break
        
        return contact_info
    
    def find_agent_pages(self, soup: BeautifulSoup) -> List[str]:
        """
        Find URLs to individual agent pages.
        
        Args:
            soup: BeautifulSoup object of the main page
            
        Returns:
            List of agent page URLs
        """
        agent_urls = []
        
        # Common patterns for agent page links
        agent_selectors = [
            'a[href*="agent"]', 'a[href*="realtor"]', 'a[href*="team"]',
            'a[href*="professional"]', '.agent-link a', '.realtor-link a',
            '.team-member a', '.agent-card a'
        ]
        
        for selector in agent_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(self.base_url, href)
                    if full_url not in agent_urls:
                        agent_urls.append(full_url)
        
        return agent_urls
    
    def scrape_agents(self, start_urls: List[str] = None) -> List[Dict]:
        """
        Scrape all agent contact information.
        
        Args:
            start_urls: List of URLs to start scraping from
            
        Returns:
            List of dictionaries containing agent information
        """
        if start_urls is None:
            start_urls = [
                f"{self.base_url}/agents",
                f"{self.base_url}/team",
                f"{self.base_url}/realtors",
                f"{self.base_url}/professionals",
                f"{self.base_url}/about/team",
                f"{self.base_url}/our-team"
            ]
        
        all_agents = []
        processed_urls = set()
        
        # Try to find agent directory pages first
        for start_url in start_urls:
            if start_url in processed_urls:
                continue
                
            processed_urls.add(start_url)
            soup = self.get_page(start_url)
            
            if soup is None:
                continue
            
            # Look for individual agent pages
            agent_urls = self.find_agent_pages(soup)
            
            if not agent_urls:
                # If no individual pages found, try to extract from current page
                agents_on_page = self.extract_agents_from_listing(soup)
                all_agents.extend(agents_on_page)
            else:
                # Process individual agent pages
                for agent_url in agent_urls:
                    if agent_url in processed_urls:
                        continue
                        
                    processed_urls.add(agent_url)
                    agent_soup = self.get_page(agent_url)
                    
                    if agent_soup:
                        agent_info = self.extract_contact_info(agent_soup, agent_url)
                        if agent_info['name']:  # Only add if we found a name
                            all_agents.append(agent_info)
        
        self.logger.info(f"Scraped {len(all_agents)} agents")
        return all_agents
    
    def extract_agents_from_listing(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract agent information from a listing page (multiple agents on one page).
        
        Args:
            soup: BeautifulSoup object of the listing page
            
        Returns:
            List of agent information dictionaries
        """
        agents = []
        
        # Common selectors for agent cards/sections
        agent_card_selectors = [
            '.agent-card', '.team-member', '.realtor-card',
            '.staff-member', '.professional', '.agent-profile'
        ]
        
        for selector in agent_card_selectors:
            agent_cards = soup.select(selector)
            if agent_cards:
                for card in agent_cards:
                    agent_info = self.extract_contact_info(card)
                    if agent_info['name']:
                        agents.append(agent_info)
                break  # Found agent cards, no need to try other selectors
        
        return agents
    
    def save_to_csv(self, agents: List[Dict], filename: str = "kelly_right_agents.csv"):
        """
        Save agent information to CSV file.
        
        Args:
            agents: List of agent information dictionaries
            filename: Output CSV filename
        """
        if not agents:
            self.logger.warning("No agents to save")
            return
        
        fieldnames = [
            'name', 'title', 'phone', 'email', 'office_phone', 'mobile_phone',
            'bio', 'specialties', 'url', 'image_url'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for agent in agents:
                # Convert specialties list to string
                agent_copy = agent.copy()
                agent_copy['specialties'] = ', '.join(agent['specialties'])
                writer.writerow(agent_copy)
        
        self.logger.info(f"Saved {len(agents)} agents to {filename}")
    
    def save_to_json(self, agents: List[Dict], filename: str = "kelly_right_agents.json"):
        """
        Save agent information to JSON file.
        
        Args:
            agents: List of agent information dictionaries
            filename: Output JSON filename
        """
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(agents, jsonfile, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved {len(agents)} agents to {filename}")


def main():
    """
    Main function to run the scraper.
    """
    # Initialize scraper
    # Note: Update the base_url with the correct Kelly Right domain
    scraper = KellyRightScraper(base_url="https://www.kellyright.com")
    
    try:
        # Scrape agents
        agents = scraper.scrape_agents()
        
        if agents:
            # Save results
            scraper.save_to_csv(agents)
            scraper.save_to_json(agents)
            
            print(f"Successfully scraped {len(agents)} agents")
            print("Files saved:")
            print("- kelly_right_agents.csv")
            print("- kelly_right_agents.json")
        else:
            print("No agents found. Please verify the website URL and structure.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")


if __name__ == "__main__":
    main()