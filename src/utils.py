import logging
import re
from datetime import datetime
from pathlib import Path
import os

def setup_logging(log_level: str = "INFO", log_file: str = "logs/scraper.log") -> logging.Logger:
    """Set up logging configuration"""
    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create logger
    logger = logging.getLogger('web_scraper')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return cleaned

def extract_price_number(price_text: str):
    """Extract numeric price from text"""
    if not price_text:
        return None
    
    # Remove currency symbols and extract numbers
    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
    
    if price_match:
        try:
            return float(price_match.group())
        except ValueError:
            return None
    
    return None

def normalize_url(url: str, base_url: str = "https://www.amazon.sg") -> str:
    """Normalize URL to absolute URL"""
    if not url:
        return ""
    
    if url.startswith('http'):
        return url
    elif url.startswith('/'):
        return base_url + url
    else:
        return base_url + '/' + url

def ensure_data_directories() -> None:
    """Ensure all required data directories exist"""
    directories = [
        "data",
        "data/raw", 
        "data/processed",
        "logs"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"   📁 Directory ensured: {directory}")
        except Exception as e:
            print(f"   ❌ Failed to create directory {directory}: {e}")
            raise 