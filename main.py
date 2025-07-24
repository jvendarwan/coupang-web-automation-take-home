from datetime import datetime
import asyncio
import random
from playwright.async_api import async_playwright

from config.settings import ScraperConfig
from src.data_extractor import ProductExtractor
from src.parser import HTMLParser
from src.processor import DataProcessor
from src.anti_bot import AntiBot
from src.utils import setup_logging, ensure_data_directories

async def extract_with_anti_bot(page, anti_bot, base_url, max_pages=2):
    """Use ProductExtractor with enterprise anti-bot features"""
    saved_files = []
    
    for page_num in range(1, max_pages + 1):
        print(f"\n📄 Processing Page {page_num}/{max_pages}")
        anti_bot.request_count += 1
        
        try:
            # Construct URL
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}&page={page_num}"
            
            # Navigate with enterprise monitoring
            print(f"   🌐 Navigating to: {url} (attempt 1)")
            response = await asyncio.wait_for(
                page.goto(url, wait_until='domcontentloaded'),
                timeout=30.0
            )
            
            if response:
                print(f"   📡 Response status: {response.status}")
                
                # Handle rate limiting 
                if await anti_bot.handle_rate_limiting(response.status, 1):
                    continue
                
                if response.status == 200:
                    print(f"   ✅ Page loaded successfully!")
                else:
                    print(f"   ⚠️ HTTP {response.status}")
                    continue
            
            # Page-specific timing
            if page_num == 1:
                print(f"   ⏳ Page 1 - waiting extra time for content...")
                await asyncio.sleep(8)
            else:
                await asyncio.sleep(3)
            
            # Try multiple selectors
            selectors_to_try = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-cel-widget*="search_result"]'
            ]
            
            products_found = False
            for selector in selectors_to_try:
                try:
                    await page.wait_for_selector(selector, timeout=15000)
                    elements = await page.query_selector_all(selector)
                    if len(elements) >= 10:
                        print(f"   ✅ Products found with {selector}! ({len(elements)} elements)")
                        products_found = True
                        break
                except Exception as e:
                    print(f"   ❌ {selector} failed: {str(e)[:50]}")
                    continue
            
            if products_found:
                # Light human simulation
                await page.mouse.move(random.randint(200, 400), random.randint(200, 400))
                await asyncio.sleep(random.uniform(1, 2))
                
                html_content = await page.content()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/raw/amazon_sg_enterprise_page_{page_num:02d}_{timestamp}.html"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                saved_files.append(filename)
                print(f"   💾 Saved: {filename}")
                
                # Intelligent delay before next page
                if page_num < max_pages:
                    await anti_bot.intelligent_delay()
            else:
                print(f"   ❌ No products found on page {page_num}")
                
        except Exception as e:
            print(f"   💥 Error on page {page_num}: {str(e)[:100]}")
            continue
    
    return saved_files


async def amazon_scraping():
    
    # Ensure all data directories exist
    print("\n📁 Setting up data directories...")
    ensure_data_directories()
    
    # Setup components
    logger = setup_logging("INFO", "logs/enterprise_scraper.log")
    config = ScraperConfig()
    selectors = config.get_selectors('amazon')
    extractor = ProductExtractor(selectors, logger)
    anti_bot = AntiBot()
    
    # Step 1: Data Extraction
    print(f"\n🔍 STEP 1: Raw Data Extraction")
    print(f"=" * 40)
    
    async with async_playwright() as playwright:
        try:
            current_proxy = anti_bot.get_next_proxy()
            proxy_config = {"server": current_proxy} if current_proxy else None
            
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context(
                user_agent=anti_bot.get_random_user_agent(),
                viewport={'width': 1280, 'height': 800},
                proxy=proxy_config
            )
            
            page = await context.new_page()
            
            if current_proxy:
                print(f"   🌐 Using proxy: {current_proxy}")
            else:
                print(f"   🌐 Direct connection (no proxy needed for respectful scraping)")
            
            base_url = "https://www.amazon.sg/s?k=electronics"
            saved_files = await extract_with_anti_bot(page, anti_bot, base_url, max_pages=2)
            
        except Exception as e:
            print(f"   💥 Browser error: {str(e)[:100]}")
            saved_files = []
        finally:
            try:
                await browser.close()
            except:
                pass
    
    # Step 2: HTML Parsing
    if saved_files:
        print(f"\n📊 STEP 2: HTML Parsing & Data Extraction")
        print(f"=" * 50)
        
        parser = HTMLParser(config.get_selectors(), logger)
        all_products = await parser.load_and_parse_html_files(saved_files)
        
        # Step 3: Data Processing
        print(f"\n💾 STEP 3: Data Processing & Export")
        print(f"=" * 40)
        
        processor = DataProcessor(logger)
        
        if all_products:
            print(f"\n🎯 SUCCESS!")
            print(f"   🌐 Successfully scraped Amazon.sg")
            print(f"   📄 Pages: {len(saved_files)}")
            print(f"   📊 Total Products: {len(all_products)}")
            print(f"   🔢 Total Requests: {anti_bot.request_count}")
            print(f"   🚨 Rate Limits Encountered: {'Yes' if anti_bot.rate_limit_encountered else 'No'}")
            
            # Validate and process data
            validated_products = processor.validate_products(all_products)
            
            # Calculate quality metrics
            quality_metrics = processor.calculate_data_quality_metrics(validated_products)
            
            # Export to JSON (complete the ETL pipeline)
            print(f"\n💾 Exporting structured data to JSON...")
            
            export_metadata = {
                "pages_scraped": len(saved_files),
                "total_requests": anti_bot.request_count,
                "rate_limits_encountered": anti_bot.rate_limit_encountered,
                "quality_metrics": quality_metrics["quality_metrics"]
            }
            
            json_filename = processor.export_to_json(validated_products, metadata=export_metadata)
            print(f"   ✅ JSON exported: {json_filename}")
            print(f"   📊 Structure: metadata + {len(validated_products)} product objects")
            
            # Show data quality metrics using processor
            processor.print_quality_summary(quality_metrics)
            
            # Show samples
            print(f"\n📱 Sample Products:")
            for i, product in enumerate(all_products[:5], 1):
                print(f"   {i}. {product.get('title', 'Unknown')[:60]}...")
                print(f"      💰 {product.get('price_text', 'N/A')}")
                print(f"      ⭐ {product.get('rating_text', 'N/A')}")
            
            return True
        else:
            print(f"\n⚠️  Files saved but no products extracted")
            return False
    else:
        print(f"\n❌ No files saved")
        return False


def main():
    """Main orchestration function"""
    
    try:
        amazon_success = asyncio.run(amazon_scraping())
        
        if amazon_success:
            print("   ✅ SUCCESS - Amazon.sg scraping completed")
        else:
            print("\n❌ FAILED - Check logs for details")
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted")
    except Exception as e:
        print(f"\n💥 Error: {e}")


if __name__ == "__main__":
    main() 