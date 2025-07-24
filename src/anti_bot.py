import asyncio
import random


class AntiBot:
    """
    Enterprise-level anti-bot features for production environments.
    
    DISCLAIMER: These advanced features (proxy rotation, 429 handling) were not 
    required for Amazon.sg scraping due to our respectful approach with proper 
    delays and conservative request patterns. However, they are essential for 
    high-volume production scraping or when dealing with more aggressive 
    anti-bot systems.
    """
    
    def __init__(self):
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Proxy list (placeholder - in production, use actual proxy services)
        # NOTE: Not needed for Amazon.sg due to respectful scraping practices
        self.proxy_list = [
            # Example proxy format (disabled for Amazon.sg):
            # "http://proxy1.example.com:8080",
            # "http://proxy2.example.com:8080", 
            # "http://proxy3.example.com:8080"
        ]
        
        self.current_proxy_index = 0
        self.request_count = 0
        self.rate_limit_encountered = False
        
    def get_random_user_agent(self):
        """Get random user agent for request diversity"""
        return random.choice(self.user_agents)
    
    def get_next_proxy(self):
        """
        Rotate to next proxy in list.
        
        DISCLAIMER: Proxy rotation not implemented for Amazon.sg as our 
        conservative approach with proper delays was sufficient. In production 
        environments with higher request volumes, proxy rotation would be 
        essential to distribute requests across different IP addresses.
        """
        if not self.proxy_list:
            return None
            
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy
    
    async def handle_rate_limiting(self, response_status, attempt=1):
        """
        Handle 429 Too Many Requests responses with exponential backoff.
        
        DISCLAIMER: This was not triggered during Amazon.sg testing due to 
        our respectful request patterns (5-10s delays). However, this handler 
        is crucial for production environments where rate limiting is more 
        aggressive.
        """
        if response_status == 429:
            self.rate_limit_encountered = True
            backoff_time = min(60, (2 ** attempt) * random.uniform(1, 3))
            
            print(f"   🚨 429 Rate Limit Detected!")
            print(f"   ⏳ Backing off for {backoff_time:.1f}s (attempt {attempt})")
            print(f"   💡 Note: This demonstrates production-level rate limit handling")
            
            await asyncio.sleep(backoff_time)
            return True
        return False
    
    async def intelligent_delay(self, base_min=5, base_max=10):
        """Respectful delays that prevent rate limiting"""
        # Increase delays if we've encountered rate limiting
        multiplier = 2 if self.rate_limit_encountered else 1
        min_delay = base_min * multiplier
        max_delay = base_max * multiplier
        
        delay = random.uniform(min_delay, max_delay)
        print(f"   ⏳ Respectful delay: {delay:.1f}s (prevents rate limiting)")
        await asyncio.sleep(delay) 