"""
General Purpose Website Crawler
Crawls any website and generates professional PDF reports
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import json
import re
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebsiteCrawler:
    """General purpose website crawler with multi-page support"""
    
    def __init__(self, base_url: str, output_dir: str = "crawled_data", max_depth: int = 2, max_pages: int = 50):
        """
        Initialize the crawler
        
        Args:
            base_url: Website URL to crawl
            output_dir: Directory to save crawled data
            max_depth: Maximum depth of crawling (1 = only base page)
            max_pages: Maximum number of pages to crawl
        """
        # Validate and normalize URL
        self.base_url = self._normalize_url(base_url)
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.max_pages = max_pages
        
        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Tracking
        self.crawled_urls = set()
        self.failed_urls = set()
        self.all_images = []
        self.all_links = []
        self.all_emails = set()
        self.all_phones = set()
        self.all_tables = []
        self.crawled_data = {}
        
        # Domain for filtering same-domain links
        self.domain = urlparse(self.base_url).netloc
        
        # Setup directories
        self._setup_directories()
        
        logger.info(f"Initialized crawler for: {self.base_url}")
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL - add https if not present"""
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate basic URL structure
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError(f"Invalid URL: {url}")
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            sys.exit(1)
        
        return url.rstrip('/')
    
    def _setup_directories(self):
        """Create necessary directories for storing data"""
        Path(self.output_dir).mkdir(exist_ok=True)
        Path(f"{self.output_dir}/images").mkdir(exist_ok=True)
        Path(f"{self.output_dir}/sections").mkdir(exist_ok=True)
        logger.info(f"Output directory ready: {self.output_dir}")
    
    def _is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain"""
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.domain
        except:
            return False
    
    def _is_valid_page(self, url: str) -> bool:
        """Check if URL should be crawled (HTML page)"""
        # Skip certain file types
        skip_extensions = ['.pdf', '.zip', '.exe', '.gif', '.jpg', '.jpeg', '.png', '.webp']
        for ext in skip_extensions:
            if url.lower().endswith(ext):
                return False
        
        # Skip mailto, tel, javascript
        if url.lower().startswith(('mailto:', 'tel:', 'javascript:', '#')):
            return False
        
        return True
    
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch webpage content"""
        try:
            logger.debug(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while fetching {url}")
            self.failed_urls.add(url)
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error fetching {url}")
            self.failed_urls.add(url)
            return None
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error {e.response.status_code} for {url}")
            self.failed_urls.add(url)
            return None
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            self.failed_urls.add(url)
            return None
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all links from page"""
        links = []
        seen = set()
        
        for link in soup.find_all('a', href=True):
            href = urljoin(base_url, link['href'])
            text = link.get_text(strip=True)
            
            # Clean up URL (remove fragments)
            href = href.split('#')[0]
            
            if text and self._is_valid_page(href) and href not in seen:
                links.append({
                    'text': text[:100],  # Limit text length
                    'url': href,
                    'title': link.get('title', '')
                })
                seen.add(href)
        
        return links
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract images from page"""
        images = []
        seen = set()
        
        for img in soup.find_all('img'):
            img_url = img.get('src', '')
            if img_url:
                img_url = urljoin(base_url, img_url)
                if img_url not in seen:
                    images.append({
                        'url': img_url,
                        'alt': img.get('alt', 'Image'),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', '')
                    })
                    seen.add(img_url)
        
        return images
    
    def _download_image(self, img_url: str, idx: int) -> Optional[str]:
        """Download and save image locally"""
        try:
            response = self.session.get(img_url, timeout=5)
            response.raise_for_status()
            
            # Generate filename
            parsed_url = urlparse(img_url)
            filename = parsed_url.path.split('/')[-1]
            if not filename or '.' not in filename:
                # Determine extension from content-type
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                else:
                    ext = '.jpg'
                filename = f"image_{idx}{ext}"
            
            filepath = f"{self.output_dir}/images/{filename}"
            
            # Avoid duplicates
            if os.path.exists(filepath):
                filepath = f"{self.output_dir}/images/{idx}_{filename}"
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
        except Exception as e:
            logger.debug(f"Failed to download image {img_url}: {e}")
            return None
    
    def extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information"""
        contact_info = {
            'emails': [],
            'phones': [],
            'addresses': []
        }
        
        # Email pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Phone patterns (various formats)
        phone_patterns = [
            r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US/Canada
            r'\+?[0-9]{1,3}\s?[0-9]{6,14}',  # International
            r'\+\d+[-.\s]?\d+[-.\s]?\d+',  # Generic international
        ]
        
        page_text = soup.get_text()
        
        # Extract emails
        emails = re.findall(email_pattern, page_text)
        contact_info['emails'] = list(set(emails))[:10]  # Limit to 10
        
        # Extract phones
        phones = set()
        for pattern in phone_patterns:
            found = re.findall(pattern, page_text)
            phones.update(found)
        contact_info['phones'] = list(phones)[:10]  # Limit to 10
        
        # Look for addresses
        for tag in soup.find_all(['address', 'p', 'span', 'div']):
            text = tag.get_text(strip=True)
            if any(keyword in text.lower() for keyword in ['address', 'location', 'street', 'city', 'state', 'zip', 'postal']):
                if len(text) > 10 and len(text) < 200:
                    contact_info['addresses'].append(text)
        
        contact_info['addresses'] = list(set(contact_info['addresses']))[:5]  # Limit to 5
        
        return contact_info
    
    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract page metadata"""
        metadata = {
            'url': url,
            'title': soup.title.string if soup.title else 'No title',
            'description': '',
            'keywords': '',
            'author': ''
        }
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content[:200]
            elif name == 'keywords':
                metadata['keywords'] = content[:200]
            elif name == 'author':
                metadata['author'] = content
        
        return metadata
    
    def extract_text_sections(self, soup: BeautifulSoup) -> Dict:
        """Extract text content organized by sections"""
        sections = {}
        
        # Look for semantic sections
        section_selectors = ['section', 'article', 'main', 'nav', 'header', 'footer']
        
        for selector in section_selectors:
            elements = soup.find_all(selector)
            if elements:
                section_name = selector.title()
                section_texts = []
                
                for elem in elements:
                    # Extract main text content
                    text_elements = elem.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span'])
                    for el in text_elements:
                        text = el.get_text(strip=True)
                        if text and len(text) > 5 and len(text) < 1000:
                            section_texts.append(text)
                
                if section_texts:
                    sections[section_name] = section_texts[:20]  # Limit to 20 items
        
        # If no semantic sections, try to find main content areas
        if not sections:
            # Look for divs with content classes
            containers = soup.find_all('div', class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['content', 'main', 'section', 'container']
            ))
            
            if containers:
                for idx, container in enumerate(containers[:5]):  # Limit to 5
                    texts = []
                    for el in container.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                        text = el.get_text(strip=True)
                        if text and len(text) > 5 and len(text) < 1000:
                            texts.append(text)
                    
                    if texts:
                        sections[f'Section_{idx+1}'] = texts[:20]
        
        return sections
    
    def extract_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract data from tables"""
        tables = []
        
        for idx, table in enumerate(soup.find_all('table')[:5]):  # Limit to 5 tables
            table_data = {
                'table_number': idx + 1,
                'headers': [],
                'rows': []
            }
            
            # Extract headers
            headers = table.find_all('th')
            table_data['headers'] = [th.get_text(strip=True)[:50] for th in headers]
            
            # Extract rows (limit to 20)
            for tr in table.find_all('tr')[1:21]:
                cells = tr.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True)[:50] for cell in cells]
                table_data['rows'].append(row_data)
            
            if table_data['headers'] or table_data['rows']:
                tables.append(table_data)
        
        return tables
    
    def crawl_page(self, url: str) -> Optional[Dict]:
        """Crawl a single page"""
        if url in self.crawled_urls:
            return None
        
        if not self._is_same_domain(url):
            return None
        
        logger.info(f"Crawling: {url}")
        self.crawled_urls.add(url)
        
        html_content = self.fetch_page(url)
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            page_data = {
                'url': url,
                'metadata': self.extract_metadata(soup, url),
                'links': self.extract_links(soup, url),
                'images': self.extract_images(soup, url),
                'contact_info': self.extract_contact_info(soup),
                'sections': self.extract_text_sections(soup),
                'tables': self.extract_tables(soup)
            }
            
            # Store for PDF generation
            if url == self.base_url:
                self.crawled_data['main_page'] = page_data
            else:
                if 'pages' not in self.crawled_data:
                    self.crawled_data['pages'] = []
                self.crawled_data['pages'].append(page_data)
            
            # Accumulate data
            self.all_links.extend(page_data['links'])
            self.all_images.extend(page_data['images'])
            self.all_tables.extend(page_data['tables'])
            
            # Extract emails and phones for aggregation
            for email in page_data['contact_info']['emails']:
                self.all_emails.add(email)
            for phone in page_data['contact_info']['phones']:
                self.all_phones.add(phone)
            
            return page_data
        
        except Exception as e:
            logger.error(f"Error parsing page {url}: {e}")
            return None
    
    def crawl(self) -> bool:
        """Main crawling function with multi-page support"""
        print(f"\n{'='*80}")
        print(f"Website Crawler Starting")
        print(f"{'='*80}")
        print(f"URL: {self.base_url}")
        print(f"Max Depth: {self.max_depth}")
        print(f"Max Pages: {self.max_pages}")
        print(f"{'='*80}\n")
        
        # Queue for BFS crawling
        to_crawl = [(self.base_url, 0)]  # (url, depth)
        
        try:
            while to_crawl and len(self.crawled_urls) < self.max_pages:
                url, depth = to_crawl.pop(0)
                
                # Respect depth limit
                if depth > self.max_depth:
                    continue
                
                # Crawl page
                page_data = self.crawl_page(url)
                if not page_data:
                    continue
                
                time.sleep(0.5)  # Be respectful to server
                
                # Queue new links if within depth limit
                if depth < self.max_depth:
                    for link_info in page_data['links']:
                        link_url = link_info['url'].split('#')[0]
                        if link_url not in self.crawled_urls and self._is_same_domain(link_url):
                            to_crawl.append((link_url, depth + 1))
            
            # Download images
            print(f"\n[*] Downloading {len(self.all_images)} images...")
            for idx, img_info in enumerate(self.all_images[:30]):  # Limit to 30 images
                self._download_image(img_info['url'], idx)
            
            # Aggregate data
            self.crawled_data['metadata'] = {
                'base_url': self.base_url,
                'pages_crawled': len(self.crawled_urls),
                'crawl_time': datetime.now().isoformat(),
                'total_images': len(self.all_images),
                'total_links': len(self.all_links),
                'total_emails': len(self.all_emails),
                'total_phones': len(self.all_phones)
            }
            
            self.crawled_data['all_emails'] = list(self.all_emails)
            self.crawled_data['all_phones'] = list(self.all_phones)
            self.crawled_data['all_links'] = self.all_links[:100]  # Limit for JSON
            
            # Save data
            self._save_data()
            
            print(f"\n[+] Crawling completed!")
            print(f"[+] Pages crawled: {len(self.crawled_urls)}")
            print(f"[+] Images found: {len(self.all_images)}")
            print(f"[+] Links found: {len(self.all_links)}")
            print(f"[+] Emails found: {len(self.all_emails)}")
            print(f"[+] Phones found: {len(self.all_phones)}\n")
            
            return True
        
        except Exception as e:
            logger.error(f"Crawling error: {e}")
            return False
    
    def _save_data(self):
        """Save crawled data to JSON"""
        json_file = f"{self.output_dir}/crawled_data.json"
        
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.crawled_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved: {json_file}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("GENERAL WEBSITE CRAWLER")
    print("="*80 + "\n")
    
    # Get user input
    while True:
        website_url = input("Enter website URL (or 'quit' to exit): ").strip()
        
        if website_url.lower() == 'quit':
            print("Exiting...")
            sys.exit(0)
        
        if not website_url:
            print("Please enter a valid URL")
            continue
        
        break
    
    # Optional: Get crawl depth
    while True:
        try:
            max_depth = input("Enter max crawl depth (1-5, default=2): ").strip()
            max_depth = int(max_depth) if max_depth else 2
            if 1 <= max_depth <= 5:
                break
            else:
                print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")
    
    # Optional: Get max pages
    while True:
        try:
            max_pages = input("Enter max pages to crawl (1-100, default=50): ").strip()
            max_pages = int(max_pages) if max_pages else 50
            if 1 <= max_pages <= 100:
                break
            else:
                print("Please enter a number between 1 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    # Create and run crawler
    output_dir = "crawled_data"
    crawler = WebsiteCrawler(website_url, output_dir, max_depth, max_pages)
    
    if crawler.crawl():
        print(f"[+] Data ready in: {output_dir}")
        print(f"[+] Next: Run 'python pdf_generator.py' to generate PDF")
    else:
        print("[-] Crawling failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
