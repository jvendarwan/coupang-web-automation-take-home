# Web Automation Take-Home Assignment

## Overview

Web scraper on amazon.sg products

## Installation

### Prerequisites

- Python 3.12 or higher
- conda package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd coupang-web-automation-take-home

# Create conda environment
conda create -n web-scraper python=3.12
conda activate web-scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## Usage

### Run the Complete Pipeline

```bash
python main.py
```

This will execute the full ETL pipeline:

1. **Data Extraction**: Scrape product data from Amazon.sg
2. **HTML Parsing**: Extract structured product information
3. **Data Processing**: Validate, analyze, and export to JSON

## Project Structure

```
coupang-web-automation-take-home/
├── main.py                     # Main orchestration script
├── src/
│   ├── data_extractor.py       # Raw HTML extraction
│   ├── parser.py               # HTML parsing & data extraction
│   ├── processor.py            # Data validation & export
│   ├── anti_bot.py             # Anti-bot mitigation strategies
│   └── utils.py                # Utility functions
├── config/
│   └── settings.py             # Configuration settings
├── data/                       # Output directory
│   ├── raw/                    # Raw HTML files
│   └── processed/              # Final JSON exports
├── logs/                       # Application logs
└── requirements.txt            # Dependencies
```

## Input and Output

### Input

- **Target Site**: Amazon.sg electronics section
- **Configuration**: Automatic (no manual input required)

### Output

The scraper generates files in the `data/` folder:

**📁 data/raw/**

- Raw HTML files from each scraped page
- Format: `amazon_sg_enterprise_page_01_YYYYMMDD_HHMMSS.html`

**📁 data/processed/**

- Structured JSON export with product data and metadata
- Format: `amazon_sg_products_YYYYMMDD_HHMMSS.json`

### JSON Output Structure

```json
{
  "scraping_metadata": {
    "source": "Amazon.sg",
    "total_products": 120,
    "pages_scraped": 2,
    "scraping_timestamp": "2025-01-01T10:00:00Z",
    "quality_metrics": {...}
  },
  "products": [
    {
      "title": "Product Name",
      "price_text": "S$29.99",
      "price_numeric": 29.99,
      "rating_text": "4.5 out of 5 stars",
      "rating_numeric": 4.5,
      "image_url": "https://...",
      "product_url": "https://...",
      "extracted_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```
