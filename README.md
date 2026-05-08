# General Purpose Website Crawler

A Python tool to crawl any website and generate professional PDF reports with extracted data including content, links, images, and contact information.

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Create virtual environment** (optional but recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

## How to Use

### Option 1: Interactive Menu (Recommended)
```bash
python main.py
```
Follow the on-screen menu to crawl and generate PDF.

### Option 2: Direct Commands

**Step 1: Crawl Website**
```bash
python web_crawler.py
```
Enter the website URL when prompted (e.g., `https://example.com`)

**Step 2: Generate PDF**
```bash
python pdf_generator.py
```

## Output

```
crawled_data/
├── crawled_data.json    # All extracted data
├── images/              # Downloaded images
└── sections/            # Content sections

example.com_20240508.pdf # Generated report
```

## Features

- 🌐 Crawl any website with multi-page support
- 📄 Generate professional PDF reports
- 🖼️ Auto-download images
- 🔗 Extract all links
- 📞 Extract contact info (emails, phones)
- 📊 Extract tables and data
- 📋 Organized JSON output

## Commands Reference

| Command | Purpose |
|---------|---------|
| `python main.py` | Interactive menu |
| `python web_crawler.py` | Start crawling |
| `python pdf_generator.py` | Generate PDF from crawled data |
| `pip install -r requirements.txt` | Install dependencies |

## Configuration

Edit `config.py` to customize:
- Max crawl depth (1-5)
- Max pages to crawl (1-100)
- Request timeout
- PDF styling
- Output directories

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection error | Check internet and website URL |
| No images downloaded | Website may block image access |
| Slow crawling | Reduce `max_depth` or `max_pages` |
| PDF too large | Reduce number of pages crawled |

## Requirements

See `requirements.txt`:
```
requests>=2.31.0
beautifulsoup4>=4.12.0
pillow>=10.0.0
reportlab>=4.0.0
lxml>=4.9.0
```
