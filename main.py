"""
Main entry point for Website Crawler
Provides user-friendly menu interface
"""

import sys
import os
from pathlib import Path
import logging

# Import our modules
try:
    from web_crawler import WebsiteCrawler
    from pdf_generator import ProfessionalPDFGenerator
    from config import create_directories, OUTPUT_DIR
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all files are in the same directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}[+] {message}{Colors.ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.CYAN}[*] {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}[!] {message}{Colors.ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}[-] {message}{Colors.ENDC}")


def get_website_url():
    """Get website URL from user with validation"""
    while True:
        url = input(f"\n{Colors.CYAN}Enter website URL{Colors.ENDC} (or 'quit' to exit): ").strip()
        
        if url.lower() == 'quit':
            return None
        
        if not url:
            print_error("Please enter a valid URL")
            continue
        
        # Basic URL validation
        if not any(url.startswith(proto) for proto in ['http://', 'https://', 'www.', 'https://www.']):
            if '.' not in url:
                print_error("Invalid URL format")
                continue
        
        return url


def get_crawl_depth():
    """Get crawl depth from user"""
    while True:
        try:
            depth_input = input(f"\n{Colors.CYAN}Enter max crawl depth{Colors.ENDC} (1-5, default=2): ").strip()
            
            if not depth_input:
                return 2
            
            depth = int(depth_input)
            if 1 <= depth <= 5:
                return depth
            else:
                print_error("Please enter a number between 1 and 5")
        except ValueError:
            print_error("Please enter a valid number")


def get_max_pages():
    """Get maximum pages to crawl from user"""
    while True:
        try:
            pages_input = input(f"\n{Colors.CYAN}Enter max pages to crawl{Colors.ENDC} (1-100, default=50): ").strip()
            
            if not pages_input:
                return 50
            
            pages = int(pages_input)
            if 1 <= pages <= 100:
                return pages
            else:
                print_error("Please enter a number between 1 and 100")
        except ValueError:
            print_error("Please enter a valid number")


def confirm_action(message):
    """Get yes/no confirmation from user"""
    while True:
        response = input(f"\n{Colors.CYAN}{message} (y/n){Colors.ENDC}: ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print_error("Please enter 'y' or 'n'")


def show_main_menu():
    """Display main menu"""
    print_header("GENERAL WEBSITE CRAWLER")
    
    print(f"{Colors.BOLD}Main Menu:{Colors.ENDC}")
    print("  1. Crawl a new website")
    print("  2. Generate PDF from existing crawl")
    print("  3. View crawl status")
    print("  4. Settings")
    print("  5. Help")
    print("  6. Exit")


def show_help():
    """Show help information"""
    print_header("HELP & DOCUMENTATION")
    
    help_text = """
{bold}Quick Start Guide:{endc}
  1. Choose 'Crawl a new website'
  2. Enter the website URL (e.g., https://example.com)
  3. Set crawl depth (how many page levels to crawl)
  4. Set max pages (maximum number of pages to crawl)
  5. Wait for crawling to complete
  6. Choose 'Generate PDF' to create the report

{bold}What Gets Extracted:{endc}
  • Page content and text sections
  • All images (automatically downloaded)
  • Hyperlinks and navigation
  • Contact information (emails, phones)
  • Table data
  • Metadata (title, description, keywords)

{bold}Output Files:{endc}
  • crawled_data.json - All extracted data in JSON format
  • *.pdf - Professional report with all content
  • crawled_data/images/ - Downloaded images
  • crawled_data/sections/ - Individual sections

{bold}Tips:{endc}
  • Start with depth=1 for faster crawling
  • Use max_pages=20 for testing
  • Check crawler.log for detailed errors
  • PDF generation can take a few minutes for large crawls

{bold}Common Issues:{endc}
  Q: Website won't crawl?
  A: Check your internet connection and website URL

  Q: No images downloaded?
  A: Website may be blocking image access

  Q: PDF is very large?
  A: Try reducing max_pages or max_depth

{bold}For More Information:{endc}
  See README.md for complete documentation
    """.format(bold=Colors.BOLD, endc=Colors.ENDC)
    
    print(help_text)


def show_settings():
    """Show settings menu"""
    print_header("SETTINGS")
    
    print(f"{Colors.BOLD}Current Settings:{Colors.ENDC}")
    print(f"  Output Directory: {OUTPUT_DIR}")
    print(f"  Log File: crawler.log")
    print(f"  Max Depth Limit: 5")
    print(f"  Max Pages Limit: 100")
    print(f"  Request Timeout: 10 seconds")
    print("\n(Additional settings can be modified in config.py)")


def show_crawl_status():
    """Show status of existing crawls"""
    print_header("CRAWL STATUS")
    
    json_file = os.path.join(OUTPUT_DIR, "crawled_data.json")
    
    if not os.path.exists(json_file):
        print_warning("No crawl data found")
        print("Run 'Crawl a new website' first")
        return
    
    import json
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        
        print(f"{Colors.BOLD}Latest Crawl Information:{Colors.ENDC}\n")
        print(f"  Base URL: {metadata.get('base_url', 'N/A')}")
        print(f"  Pages Crawled: {metadata.get('pages_crawled', 0)}")
        print(f"  Total Links: {metadata.get('total_links', 0)}")
        print(f"  Total Images: {metadata.get('total_images', 0)}")
        print(f"  Emails Found: {metadata.get('total_emails', 0)}")
        print(f"  Phones Found: {metadata.get('total_phones', 0)}")
        print(f"  Crawl Time: {metadata.get('crawl_time', 'N/A')[:10]}")
        
        # Check for PDFs
        pdfs = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if pdfs:
            print(f"\n  {Colors.BOLD}Generated PDFs:{Colors.ENDC}")
            for pdf in pdfs[-5:]:  # Show last 5
                size = os.path.getsize(pdf) / (1024 * 1024)
                print(f"    • {pdf} ({size:.2f} MB)")
    
    except Exception as e:
        print_error(f"Error reading crawl data: {e}")


def crawl_workflow():
    """Complete crawling workflow"""
    print_header("WEBSITE CRAWLER")
    
    # Get URL
    url = get_website_url()
    if not url:
        return False
    
    # Get depth
    depth = get_crawl_depth()
    
    # Get max pages
    max_pages = get_max_pages()
    
    # Confirm
    print(f"\n{Colors.BOLD}Crawl Configuration:{Colors.ENDC}")
    print(f"  URL: {url}")
    print(f"  Max Depth: {depth}")
    print(f"  Max Pages: {max_pages}")
    
    if not confirm_action("Start crawling?"):
        print_warning("Crawling cancelled")
        return False
    
    # Create crawler
    try:
        print_info("Initializing crawler...")
        crawler = WebsiteCrawler(url, OUTPUT_DIR, depth, max_pages)
        
        # Run crawler
        print_info("Starting crawl (this may take a few minutes)...")
        if crawler.crawl():
            print_success("Crawling completed!")
            print_info(f"Data saved to: {OUTPUT_DIR}")
            
            # Offer to generate PDF
            if confirm_action("Generate PDF report?"):
                return pdf_workflow()
            return True
        else:
            print_error("Crawling failed")
            return False
    
    except Exception as e:
        print_error(f"Error during crawling: {e}")
        logger.exception("Crawl error")
        return False


def pdf_workflow():
    """PDF generation workflow"""
    print_header("PDF REPORT GENERATION")
    
    json_file = os.path.join(OUTPUT_DIR, "crawled_data.json")
    
    if not os.path.exists(json_file):
        print_error("No crawled data found")
        print_info("Please crawl a website first")
        return False
    
    try:
        print_info("Initializing PDF generator...")
        generator = ProfessionalPDFGenerator(OUTPUT_DIR)
        
        print_info("Generating PDF (this may take a minute)...")
        if generator.generate():
            print_success("PDF generated successfully!")
            print_info(f"File: {generator.output_pdf}")
            return True
        else:
            print_error("PDF generation failed")
            return False
    
    except Exception as e:
        print_error(f"Error during PDF generation: {e}")
        logger.exception("PDF error")
        return False


def main():
    """Main application loop"""
    try:
        create_directories()
        
        while True:
            show_main_menu()
            
            choice = input(f"\n{Colors.CYAN}Enter your choice{Colors.ENDC} (1-6): ").strip()
            
            if choice == '1':
                crawl_workflow()
            elif choice == '2':
                pdf_workflow()
            elif choice == '3':
                show_crawl_status()
            elif choice == '4':
                show_settings()
            elif choice == '5':
                show_help()
            elif choice == '6':
                print_success("Goodbye!")
                sys.exit(0)
            else:
                print_error("Invalid choice. Please try again.")
            
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.exception("Main loop error")
        sys.exit(1)


if __name__ == "__main__":
    main()
