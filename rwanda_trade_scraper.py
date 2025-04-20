import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RwandaTradePortalScraper:
    def __init__(self):
        self.base_url = "https://rwandatrade.rw"
        self.procedures_base_url = f"{self.base_url}/procedures"
        self.session = requests.Session()
        self.procedures_data = []
        
        # Create headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Setup Selenium
        self._setup_selenium()
    
    def _setup_selenium(self):
        """Set up Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            raise e
    
    def get_page_content(self, url, use_selenium=False):
        """Get page content with error handling and retries"""
        if use_selenium:
            try:
                logger.info(f"Fetching with Selenium: {url}")
                self.driver.get(url)
                # Wait for the page to load
                time.sleep(3)
                return self.driver.page_source
            except Exception as e:
                logger.error(f"Selenium error: {e}")
                return None
        else:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Fetching with requests: {url}")
                    response = self.session.get(url, headers=self.headers, timeout=30)
                    if response.status_code == 200:
                        return response.text
                    else:
                        logger.warning(f"Failed to retrieve {url}, status code: {response.status_code}")
                        time.sleep(2)  # Wait before retrying
                except Exception as e:
                    logger.error(f"Error retrieving {url}: {e}")
                    time.sleep(2)  # Wait before retrying
            
            logger.error(f"Failed to retrieve {url} after {max_retries} attempts")
            return None
    
    def extract_procedures_from_page(self, page_number):
        """Extract procedure links from a specific page"""
        page_url = f"{self.procedures_base_url}?page={page_number}&l=en"
        logger.info(f"Accessing procedures page {page_number}: {page_url}")
        
        # For the procedures listing page, requests is sufficient
        html_content = self.get_page_content(page_url, use_selenium=False)
        if not html_content:
            logger.error(f"Could not retrieve content for page {page_number}")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all procedure links based on the format you provided
        procedure_links = soup.find_all('a', class_='title', href=lambda href: href and '/procedure/' in href)
        
        procedures = []
        for link in procedure_links:
            href = link.get('href')
            # Ensure we have the full URL
            if href.startswith('/'):
                full_url = f"{self.base_url}{href}"
            else:
                full_url = href
                
            title = link.text.strip()
            
            # Extract the procedure ID for reference
            procedure_id = None
            id_match = re.search(r'/procedure/(\d+)', href)
            if id_match:
                procedure_id = id_match.group(1)
            
            procedure = {
                'title': title,
                'url': full_url,
                'procedure_id': procedure_id,
                'page_number': page_number
            }
            procedures.append(procedure)
            logger.info(f"Found procedure: {title}")
        
        return procedures
    
    def extract_procedure_details(self, procedure):
        """Extract detailed information for a single procedure"""
        url = procedure['url']
        logger.info(f"Processing procedure: {procedure['title']}")
        
        # Use Selenium to fetch the procedure page to handle dynamic content
        try:
            # Navigate to the procedure page
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(3)
            
            # Find the context-msg div
            context_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="context-msg"]')
            
            if context_elements:
                description = context_elements[0].text.strip()
                logger.info(f"Extracted description: {description[:100]}...")
            else:
                # Try using JavaScript as a fallback
                description = self.driver.execute_script("""
                    var contextDivs = document.querySelectorAll('div[class*="context-msg"]');
                    if (contextDivs.length > 0) {
                        return contextDivs[0].textContent.trim();
                    }
                    return "";
                """)
                
                if description:
                    logger.info(f"Extracted description using JavaScript: {description[:100]}...")
                else:
                    logger.warning(f"No description found for {procedure['title']}")
                    description = ""
            
            procedure['description'] = description
            
        except Exception as e:
            logger.error(f"Error extracting details for {url}: {e}")
            procedure['description'] = ""
        
        return procedure
    
    def extract_all_procedures(self, max_pages=16, limit=None, test_mode=False):
        """Extract procedures from pages"""
        all_procedures = []
        
        if test_mode:
            max_pages = 1  # Only scrape the first page in test mode
            if not limit:
                limit = 10  # Default to 10 procedures in test mode
        
        for page in range(1, max_pages + 1):
            page_procedures = self.extract_procedures_from_page(page)
            if not page_procedures:
                logger.warning(f"No procedures found on page {page}, stopping pagination")
                break
            
            all_procedures.extend(page_procedures)
            logger.info(f"Completed page {page}, total procedures so far: {len(all_procedures)}")
            
            # Check if we've reached the limit
            if limit and len(all_procedures) >= limit:
                all_procedures = all_procedures[:limit]
                logger.info(f"Reached procedure limit of {limit}")
                break
                
            if not test_mode:
                time.sleep(2)  # Respectful delay between page requests
        
        self.procedures_data = all_procedures
        logger.info(f"Total procedures extracted: {len(all_procedures)}")
        return all_procedures
    
    def process_procedures(self):
        """Process all extracted procedures to get detailed information"""
        logger.info("Beginning extraction of procedure details")
        
        updated_procedures = []
        
        for i, procedure in enumerate(self.procedures_data):
            # Add delay between requests
            if i > 0:
                time.sleep(1)
                
            updated_procedure = self.extract_procedure_details(procedure)
            updated_procedures.append(updated_procedure)
            
            # Log progress
            if (i + 1) % 5 == 0 or (i + 1) == len(self.procedures_data):
                logger.info(f"Processed {i + 1}/{len(self.procedures_data)} procedures")
        
        self.procedures_data = updated_procedures
        logger.info("Completed extraction of procedure details")
    
    def save_data(self, filename_prefix="rwanda_trade"):
        """Save the extracted data to files"""
        if not self.procedures_data:
            logger.warning("No data to save")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs("rwanda_trade_data", exist_ok=True)
        
        # Save as JSON
        json_filename = f"rwanda_trade_data/{filename_prefix}_procedures.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.procedures_data, f, ensure_ascii=False, indent=4)
        
        # Save as CSV
        csv_filename = f"rwanda_trade_data/{filename_prefix}_procedures.csv"
        df = pd.DataFrame(self.procedures_data)
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        logger.info(f"Saved {len(self.procedures_data)} procedures to {json_filename} and {csv_filename}")
        return json_filename
    
    def run(self, test_mode=False, limit=None):
        """Run the full scraping process"""
        logger.info(f"Starting Rwanda Trade Portal scraping process {'(TEST MODE)' if test_mode else ''}")
        
        try:
            # Extract basic procedure information
            if test_mode:
                logger.info("Running in test mode - will only extract a few procedures")
                self.extract_all_procedures(test_mode=True, limit=limit or 10)
                filename_prefix = "test_rwanda_trade"
            else:
                self.extract_all_procedures(limit=limit)
                filename_prefix = "rwanda_trade"
            
            # Extract detailed information for each procedure
            self.process_procedures()
            
            # Save the data
            json_filename = self.save_data(filename_prefix)
            
            logger.info("Scraping process completed")
            return json_filename
            
        finally:
            # Always close the Selenium driver
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver closed")
            except:
                pass


# Test function to verify a single procedure extraction works
def test_single_procedure():
    """Test Selenium extraction on the specific example URL"""
    try:
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test URL
        url = "https://rwandatrade.rw/procedure/177?l=en"
        print(f"\nTesting extraction from: {url}")
        
        # Navigate to the page
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(3)
        
        # Find the context-msg div
        context_elements = driver.find_elements(By.CSS_SELECTOR, 'div[class*="context-msg"]')
        
        if context_elements:
            description = context_elements[0].text.strip()
            print(f"\nSuccessfully extracted description:")
            print(f"{description}")
        else:
            print("No context-msg element found")
            
            # Try JavaScript as a fallback
            description = driver.execute_script("""
                var contextDivs = document.querySelectorAll('div[class*="context-msg"]');
                if (contextDivs.length > 0) {
                    return contextDivs[0].textContent.trim();
                }
                return "";
            """)
            
            if description:
                print(f"\nExtracted description using JavaScript:")
                print(f"{description}")
            else:
                print("No description could be extracted")
        
        driver.quit()
        
    except Exception as e:
        print(f"Error during test: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Rwanda Trade Portal procedures')
    parser.add_argument('--test', action='store_true', help='Run in test mode with only 10 procedures')
    parser.add_argument('--test-single', action='store_true', help='Test extraction of a single procedure')
    parser.add_argument('--limit', type=int, help='Limit the number of procedures to extract')
    
    args = parser.parse_args()
    
    if args.test_single:
        test_single_procedure()
    else:
        scraper = RwandaTradePortalScraper()
        json_filename = scraper.run(test_mode=args.test, limit=args.limit)
        
        print(f"\nScraping completed. Data saved to {json_filename}")
        print("You can now test the chatbot with this data.")