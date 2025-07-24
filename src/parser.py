import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

import aiofiles
from bs4 import BeautifulSoup

from src.utils import clean_text, extract_price_number, normalize_url
from src.types import ProductData, ProductList


class HTMLParser:
    """Parse HTML content and extract structured product data"""
    
    def __init__(self, selectors: Dict[str, str], logger: logging.Logger):
        self.selectors = selectors
        self.logger = logger
    
    def html_parser(self, html_content: str, base_url: str = "https://www.amazon.sg") -> ProductList:
        """
        Parse HTML content using Beautiful Soup to extract product information
        1. Use Beautiful Soup to parse HTML
        2. Extract product title, price, rating, and image_url
        3. Return structured data
        """
        products: List[Dict[str, Union[str, float, int, None]]] = []
        
        try:
            # Parse HTML with Beautiful Soup
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Find all product containers
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            self.logger.info(f"Found {len(product_containers)} products in HTML")
            
            for idx, container in enumerate(product_containers):
                try:
                    product_data = self._extract_amazon_product_from_soup(container, base_url)
                    if product_data:
                        products.append(product_data)
                        self.logger.debug(f"Extracted product {idx + 1}: {product_data.get('title', 'Unknown')}")
                except Exception as e:
                    self.logger.warning(f"Failed to extract product {idx + 1}: {str(e)}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to parse HTML: {str(e)}")
        
        return products
    
    async def load_and_parse_html_files(self, file_paths: List[str]) -> ProductList:
        """Load saved HTML files and parse them for product data"""
        all_products: List[Dict[str, Union[str, float, int, None]]] = []
        
        for file_path in file_paths:
            try:
                self.logger.info(f"Parsing HTML file: {file_path}")
                
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    html_content = await f.read()
                
                products = self.html_parser(html_content)
                all_products.extend(products)
                
                self.logger.info(f"Extracted {len(products)} products from {file_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to parse HTML file {file_path}: {str(e)}")
        
        return all_products
    
    def _extract_amazon_product_from_soup(self, container, base_url: str) -> Optional[ProductData]:
        """Extract individual product data from Beautiful Soup container"""
        try:
            product_data: Dict[str, Union[str, float, int, None]] = {
                'extracted_at': datetime.now().isoformat(),
                'source': 'amazon.sg'
            }
            
            # Extract product title
            title_selectors = [
                'h2 a span',
                '.a-size-base-plus',
                '.a-size-medium',
                '.a-size-base',
                '[data-cy="title-recipe-title"]'
            ]
            
            title = None
            for selector in title_selectors:
                title_elem = container.select_one(selector)
                if title_elem and title_elem.get_text(strip=True):
                    title = title_elem.get_text(strip=True)
                    break
            
            product_data['title'] = clean_text(title) if title else "Unknown"
            
            # Extract price
            price_selectors = [
                '.a-price .a-offscreen',
                '.a-price-whole',
                '.a-price-range',
                '.a-price'
            ]
            
            price_text = None
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text and 'S$' in price_text:
                        break
            
            product_data['price_text'] = clean_text(price_text) if price_text else ""
            product_data['price_numeric'] = extract_price_number(price_text) if price_text else None
            
            # Extract rating
            rating_selectors = [
                '.a-icon-alt',
                '.a-icon-rating',
                '[aria-label*="stars"]'
            ]
            
            rating_text = None
            rating_numeric = None
            for selector in rating_selectors:
                rating_elem = container.select_one(selector)
                if rating_elem:
                    # Check aria-label first
                    aria_label = rating_elem.get('aria-label', '')
                    if 'out of' in aria_label.lower():
                        rating_text = aria_label
                    else:
                        rating_text = rating_elem.get_text(strip=True)
                    
                    if rating_text:
                        # Extract numeric rating (e.g., "4.5 out of 5 stars" -> 4.5)
                        rating_match = re.search(r'(\d+\.?\d*)\s*out of', rating_text)
                        if rating_match:
                            rating_numeric = float(rating_match.group(1))
                        break
            
            product_data['rating_text'] = clean_text(rating_text) if rating_text else ""
            product_data['rating_numeric'] = rating_numeric
            
            # Extract image URL
            image_selectors = [
                '.s-image',
                '.a-dynamic-image',
                'img[data-image-latency]',
                'img'
            ]
            
            image_url = None
            for selector in image_selectors:
                img_elem = container.select_one(selector)
                if img_elem:
                    image_url = img_elem.get('src') or img_elem.get('data-src')
                    if image_url:
                        break
            
            product_data['image_url'] = normalize_url(image_url, base_url) if image_url else ""
            
            # Extract product URL
            link_selectors = [
                'h2 a',
                '.a-link-normal',
                'a[href*="/dp/"]'
            ]
            
            product_url = None
            for selector in link_selectors:
                link_elem = container.select_one(selector)
                if link_elem:
                    product_url = link_elem.get('href')
                    if product_url:
                        break
            
            product_data['product_url'] = normalize_url(product_url, base_url) if product_url else ""
            
            # Extract review count
            review_selectors = [
                '.a-size-base',
                '[aria-label*="reviews"]',
                'a[href*="#customerReviews"]'
            ]
            
            review_count_text = None
            for selector in review_selectors:
                review_elem = container.select_one(selector)
                if review_elem:
                    text = review_elem.get_text(strip=True)
                    if re.search(r'\d+', text) and ('review' in text.lower() or 'rating' in text.lower()):
                        review_count_text = text
                        break
            
            product_data['review_count_text'] = clean_text(review_count_text) if review_count_text else ""
            
            # Extract numeric review count
            if review_count_text:
                review_match = re.search(r'(\d+(?:,\d+)*)', review_count_text)
                if review_match:
                    product_data['review_count_numeric'] = int(review_match.group(1).replace(',', ''))
                else:
                    product_data['review_count_numeric'] = None
            else:
                product_data['review_count_numeric'] = None
            
            # Only return if we have meaningful data
            if product_data['title'] != "Unknown" or product_data['price_text']:
                return product_data
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error extracting Amazon product from soup: {str(e)}")
            return None 