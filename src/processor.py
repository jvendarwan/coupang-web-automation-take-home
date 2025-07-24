import json
import os
from datetime import datetime
from typing import Dict, List, Any, Union
import logging


class DataProcessor:
    """Handle all data processing operations including export and quality metrics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def export_to_json(self, products: List[Dict[str, Union[str, float, int, None]]], 
                      output_dir: str = "data/processed",
                      metadata: Dict[str, Any] = {}) -> str:
        """
        Export product data to JSON file with metadata
        
        Args:
            products: List of product dictionaries
            output_dir: Directory to save JSON file
            metadata: Additional metadata to include
            
        Returns:
            Path to the saved JSON file
        """
        try:
            # Create processed directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = f"{output_dir}/amazon_sg_products_{timestamp}.json"
            
            # Prepare data for JSON export
            export_data = {
                "scraping_metadata": {
                    "source": "Amazon.sg",
                    "search_query": "electronics",
                    "scraping_timestamp": datetime.now().isoformat(),
                    "total_products": len(products),
                    "scraper_version": "enterprise-v1.0",
                    **(metadata or {})
                },
                "products": products
            }
            
            # Save to JSON file
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"JSON exported: {json_filename}")
            return json_filename
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {str(e)}")
            raise
    
    def calculate_data_quality_metrics(self, products: List[Dict[str, Union[str, float, int, None]]]) -> Dict[str, Any]:
        """
        Calculate data quality metrics for the extracted products
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Dictionary containing quality metrics
        """
        if not products:
            return {
                "total_products": 0,
                "quality_metrics": {}
            }
        
        total = len(products)
        
        # Count valid data points
        valid_prices = [p for p in products if p.get('price_numeric')]
        valid_ratings = [p for p in products if p.get('rating_numeric')]
        valid_images = [p for p in products if p.get('image_url')]
        valid_titles = [p for p in products if p.get('title') and p.get('title') != "Unknown"]
        valid_urls = [p for p in products if p.get('product_url')]
        valid_reviews = [p for p in products if p.get('review_count_numeric')]
        
        metrics = {
            "total_products": total,
            "quality_metrics": {
                "titles": {
                    "valid_count": len(valid_titles),
                    "coverage_percentage": round(len(valid_titles) / total * 100, 1) if total > 0 else 0
                },
                "prices": {
                    "valid_count": len(valid_prices),
                    "coverage_percentage": round(len(valid_prices) / total * 100, 1) if total > 0 else 0,
                    "price_range": {
                        "min": min([float(p['price_numeric']) for p in valid_prices if p['price_numeric'] is not None]) if valid_prices else None,
                        "max": max([float(p['price_numeric']) for p in valid_prices if p['price_numeric'] is not None]) if valid_prices else None,
                        "avg": round(sum([float(p['price_numeric']) for p in valid_prices if p['price_numeric'] is not None]) / len(valid_prices), 2) if valid_prices else None
                    }
                },
                "ratings": {
                    "valid_count": len(valid_ratings),
                    "coverage_percentage": round(len(valid_ratings) / total * 100, 1) if total > 0 else 0,
                    "rating_range": {
                        "min": min([float(p['rating_numeric']) for p in valid_ratings if p['rating_numeric'] is not None]) if valid_ratings else None,
                        "max": max([float(p['rating_numeric']) for p in valid_ratings if p['rating_numeric'] is not None]) if valid_ratings else None,
                        "avg": round(sum([float(p['rating_numeric']) for p in valid_ratings if p['rating_numeric'] is not None]) / len(valid_ratings), 2) if valid_ratings else None
                    }
                },
                "images": {
                    "valid_count": len(valid_images),
                    "coverage_percentage": round(len(valid_images) / total * 100, 1) if total > 0 else 0
                },
                "product_urls": {
                    "valid_count": len(valid_urls),
                    "coverage_percentage": round(len(valid_urls) / total * 100, 1) if total > 0 else 0
                },
                "reviews": {
                    "valid_count": len(valid_reviews),
                    "coverage_percentage": round(len(valid_reviews) / total * 100, 1) if total > 0 else 0,
                    "review_range": {
                        "min": min([int(p['review_count_numeric']) for p in valid_reviews if p['review_count_numeric'] is not None]) if valid_reviews else None,
                        "max": max([int(p['review_count_numeric']) for p in valid_reviews if p['review_count_numeric'] is not None]) if valid_reviews else None,
                        "total": sum([int(p['review_count_numeric']) for p in valid_reviews if p['review_count_numeric'] is not None]) if valid_reviews else None
                    }
                }
            }
        }
        
        return metrics
    
    def print_quality_summary(self, metrics: Dict[str, Any]):
        """Print a formatted quality summary"""
        if not metrics or metrics["total_products"] == 0:
            print("📊 No products to analyze")
            return
        
        total = metrics["total_products"]
        quality = metrics["quality_metrics"]
        
        print(f"\n📈 Data Quality Metrics:")
        print(f"   📝 Titles: {quality['titles']['valid_count']}/{total} ({quality['titles']['coverage_percentage']}%)")
        print(f"   💰 Prices: {quality['prices']['valid_count']}/{total} ({quality['prices']['coverage_percentage']}%)")
        print(f"   ⭐ Ratings: {quality['ratings']['valid_count']}/{total} ({quality['ratings']['coverage_percentage']}%)")
        print(f"   🖼️ Images: {quality['images']['valid_count']}/{total} ({quality['images']['coverage_percentage']}%)")
        print(f"   🔗 URLs: {quality['product_urls']['valid_count']}/{total} ({quality['product_urls']['coverage_percentage']}%)")
        print(f"   📝 Reviews: {quality['reviews']['valid_count']}/{total} ({quality['reviews']['coverage_percentage']}%)")
        
        # Price analysis
        if quality['prices']['price_range']['min'] is not None:
            price_range = quality['prices']['price_range']
            print(f"\n💰 Price Analysis:")
            print(f"   📊 Range: S${price_range['min']:.2f} - S${price_range['max']:.2f}")
            print(f"   📈 Average: S${price_range['avg']:.2f}")
        
        # Rating analysis
        if quality['ratings']['rating_range']['min'] is not None:
            rating_range = quality['ratings']['rating_range']
            print(f"\n⭐ Rating Analysis:")
            print(f"   📊 Range: {rating_range['min']:.1f} - {rating_range['max']:.1f} stars")
            print(f"   📈 Average: {rating_range['avg']:.1f} stars")
    
    def validate_products(self, products: List[Dict[str, Union[str, float, int, None]]]) -> List[Dict[str, Union[str, float, int, None]]]:
        """
        Validate and clean product data
        
        Args:
            products: List of product dictionaries
            
        Returns:
            List of validated product dictionaries
        """
        validated_products = []
        
        for idx, product in enumerate(products):
            try:
                # Basic validation
                if not product.get('title') or product.get('title') == "Unknown":
                    self.logger.warning(f"Product {idx + 1}: Missing or invalid title")
                    continue
                
                # Ensure required fields exist with proper type handling
                def safe_strip(value):
                    """Safely strip strings, return empty string for non-strings"""
                    return str(value).strip() if value is not None else ""
                
                validated_product = {
                    'extracted_at': product.get('extracted_at', datetime.now().isoformat()),
                    'source': product.get('source', 'amazon.sg'),
                    'title': safe_strip(product.get('title', '')),
                    'price_text': safe_strip(product.get('price_text', '')),
                    'price_numeric': product.get('price_numeric'),
                    'rating_text': safe_strip(product.get('rating_text', '')),
                    'rating_numeric': product.get('rating_numeric'),
                    'image_url': safe_strip(product.get('image_url', '')),
                    'product_url': safe_strip(product.get('product_url', '')),
                    'review_count_text': safe_strip(product.get('review_count_text', '')),
                    'review_count_numeric': product.get('review_count_numeric')
                }
                
                validated_products.append(validated_product)
                
            except Exception as e:
                self.logger.warning(f"Product {idx + 1}: Validation failed - {str(e)}")
                continue
        
        self.logger.info(f"Validated {len(validated_products)} out of {len(products)} products")
        return validated_products 