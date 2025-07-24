from typing import Dict

class ScraperConfig:
    """Simple configuration class for Amazon.sg scraping"""
    
    def __init__(self):
        # Amazon.sg specific selectors
        self.SELECTORS: Dict[str, Dict[str, str]] = {
            'amazon': {
                'product_container': '[data-component-type="s-search-result"]',
                'product_name': 'h2 a span, .a-size-base-plus, .a-size-medium',
                'product_price': '.a-price-whole, .a-price .a-offscreen, .a-price-range',
                'product_rating': '.a-icon-alt, .a-icon-rating',
                'product_image': '.s-image, .a-dynamic-image',
                'product_link': 'h2 a, .a-link-normal',
                'next_button': '.s-pagination-next, .s-pagination-item:last-child',
                'pagination_links': '.s-pagination-item a'
            }
        }
    
    def get_selectors(self, site_name: str = 'amazon') -> Dict[str, str]:
        """Get selectors for Amazon"""
        return self.SELECTORS.get(site_name, self.SELECTORS['amazon']) 