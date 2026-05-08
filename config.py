"""
Configuration settings for Website Crawler
"""

import os
from pathlib import Path

# Output directories
OUTPUT_DIR = "crawled_data"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
SECTIONS_DIR = os.path.join(OUTPUT_DIR, "sections")

# Crawling settings
DEFAULT_MAX_DEPTH = 2
DEFAULT_MAX_PAGES = 50
MAX_DEPTH_LIMIT = 5
MAX_PAGES_LIMIT = 100

# Network settings
REQUEST_TIMEOUT = 10
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds

# User Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Image settings
MAX_IMAGES_TO_DOWNLOAD = 30
MAX_IMAGES_IN_PDF = 40
ALLOWED_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp')

# PDF settings
PDF_PAGE_SIZE = 'A4'  # or 'letter'
PDF_LEFT_MARGIN = 0.6  # inches
PDF_RIGHT_MARGIN = 0.6  # inches
PDF_TOP_MARGIN = 0.75  # inches
PDF_BOTTOM_MARGIN = 0.75  # inches

# Content limits
MAX_SECTION_ITEMS = 20
MAX_LINKS_IN_PDF = 60
MAX_TABLES_TO_EXTRACT = 5
MAX_TABLE_ROWS = 20
MAX_ADDRESSES = 5
MAX_EMAILS = 10
MAX_PHONES = 10

# Color scheme for PDF
COLOR_PRIMARY = '#1a5490'
COLOR_SECONDARY = '#2c5aa0'
COLOR_ACCENT = '#0066cc'
COLOR_BACKGROUND = '#f5f5f5'

# Logging
LOG_FILE = 'crawler.log'
LOG_LEVEL = 'INFO'

# File size limits
MAX_JSON_SIZE = 50  # MB
MAX_PDF_SIZE = 200  # MB

# Request headers
REQUEST_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# URL patterns to skip
SKIP_EXTENSIONS = ['.pdf', '.zip', '.exe', '.rar', '.7z', '.bin']
SKIP_PROTOCOLS = ['mailto:', 'tel:', 'javascript:', 'sms:']

def create_directories():
    """Create necessary directories"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(IMAGES_DIR).mkdir(exist_ok=True)
    Path(SECTIONS_DIR).mkdir(exist_ok=True)

if __name__ == "__main__":
    create_directories()
    print("Configuration module - not meant to run directly")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Default max depth: {DEFAULT_MAX_DEPTH}")
    print(f"Default max pages: {DEFAULT_MAX_PAGES}")
