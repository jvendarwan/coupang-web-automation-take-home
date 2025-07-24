import asyncio
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import aiofiles
from playwright.async_api import Page


class ProductExtractor:
    """Extract raw HTML data from web pages with focus on Amazon.sg"""
    
    def __init__(self, selectors: Dict[str, str], logger: logging.Logger):
        self.selectors = selectors
        self.logger = logger
    
    async def extract_by_pagination(self, page: Page, base_url: str = "https://www.amazon.sg/s?k=electronics", max_pages: int = 5) -> List[str]:
        """
        Extract raw HTML data by navigating through paginated results
        
        Args:
            page: Playwright page instance
            base_url: Base URL for scraping
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of file paths to saved HTML files
        """
        saved_files = []
        
        try:
            self.logger.info(f"Starting pagination extraction from {base_url}")
            
            # Create raw data directory
            raw_data_path = Path("data/raw")
            raw_data_path.mkdir(parents=True, exist_ok=True)
            
            for page_num in range(1, max_pages + 1):
                try:
                    # Construct URL with pagination
                    if page_num == 1:
                        url = base_url
                    else:
                        separator = "&" if "?" in base_url else "?"
                        url = f"{base_url}{separator}page={page_num}"
                    
                    self.logger.info(f"Navigating to page {page_num}: {url}")
                    
                    # Navigate to the page
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    
                    # Wait for products to load
                    await page.wait_for_selector('[data-component-type="s-search-result"]', timeout=15000)
                    
                    # Get the HTML content
                    html_content = await page.content()
                    
                    # Save raw HTML with pagination prefix
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"amazon_sg_electronics_page_{page_num:02d}_{timestamp}.html"
                    file_path = raw_data_path / filename
                    
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                        await f.write(html_content)
                    
                    saved_files.append(str(file_path))
                    self.logger.info(f"Saved page {page_num} HTML to {file_path}")
                    
                    # Check if there are more pages (look for next button or page numbers)
                    next_button = page.locator('.s-pagination-next')
                    if await next_button.count() == 0:
                        self.logger.info(f"No more pages after page {page_num}")
                        break
                    
                    # Check if next button is disabled
                    if await next_button.count() > 0:
                        is_disabled = await next_button.first.get_attribute('aria-disabled')
                        if is_disabled == 'true':
                            self.logger.info(f"Reached last page at page {page_num}")
                            break
                    
                    # Random delay between page requests (anti-bot measure)
                    await asyncio.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    self.logger.error(f"Failed to extract page {page_num}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed pagination extraction: {str(e)}")
        
        return saved_files
    
    # NOT USED - but thought it was useful to have
    async def extract_single_page(self, page: Page, url: str, page_name: str = "page") -> str:
        """
        Extract HTML content from a single page
        
        Args:
            page: Playwright page instance
            url: URL to scrape
            page_name: Name identifier for the saved file
            
        Returns:
            Path to the saved HTML file
        """
        try:
            self.logger.info(f"Extracting single page: {url}")
            
            # Create raw data directory
            raw_data_path = Path("data/raw")
            raw_data_path.mkdir(parents=True, exist_ok=True)
            
            # Navigate to the page
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_load_state('domcontentloaded')
            
            # Get the HTML content
            html_content = await page.content()
            
            # Save raw HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"amazon_sg_{page_name}_{timestamp}.html"
            file_path = raw_data_path / filename
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(html_content)
            
            self.logger.info(f"Saved HTML to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to extract single page: {str(e)}")
            raise