from typing import TypedDict, Optional, List


class ProductData(TypedDict):
    """Structured product data with consistent types"""
    extracted_at: str
    source: str
    title: str
    price_text: str
    price_numeric: Optional[float]
    rating_text: str
    rating_numeric: Optional[float]
    image_url: str
    product_url: str
    review_count_text: str
    review_count_numeric: Optional[int]


# Type aliases for cleaner code
ProductList = List[ProductData] 