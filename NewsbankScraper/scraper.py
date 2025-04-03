"""
Main scraper class for NewsBank.
Handles the high-level scraping process.
"""

import asyncio
import logging
import math
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm
from tqdm.asyncio import tqdm as async_tqdm

from NewsbankScraper.parser import NewsBankParser

logger = logging.getLogger(__name__)

class NewsBankScraper:
    """NewsBank scraper main class"""
    
    def __init__(self, config: Dict[str, Any], rate_limit: float = 1.0, save_html: bool = False, 
                concurrency: int = 10, num_processors: Optional[int] = None, full_text = False):
        """
        Initialize the scraper.
        
        Args:
            config: Configuration dictionary
            rate_limit: Rate limit in seconds between requests
            save_html: Whether to save HTML responses for debugging
            concurrency: Maximum number of concurrent requests
            num_processors: Number of CPU processors to use for parsing
        """
        self.config = config
        self.rate_limit = rate_limit
        self.save_html = save_html
        self.session = None
        self.semaphore = asyncio.Semaphore(concurrency)  # Configurable concurrency
        self.full_text = full_text
        
        # Initialize parser
        self.parser = NewsBankParser(num_workers=num_processors)
        
        # Extract location from config 
        self.location = self._extract_location_from_config()
    
    def _extract_location_from_config(self) -> Dict[str, str]:
        """Extract location information from the config"""
        location = {}
        
        # Get location from t parameter in query params
        t_param = self.config['query_params'].get('t', '')
        
        # Extract city, state and country from t parameter if available
        country_match = re.search(r'country:([^!]+)!', t_param)
        city_state_match = re.search(r'city:([^!]+)!', t_param)
        
        if country_match:
            country = country_match.group(1)
            location['country'] = country.replace('+', ' ')
        
        if city_state_match:
            # Extract city and state from format "City (State)"
            city_state = city_state_match.group(1)
            city_state = city_state.replace('+', ' ')
            
            # Parse out city and state
            state_match = re.search(r'(.+)\s+\(([A-Z]{2})\)', city_state)
            if state_match:
                location['city'] = state_match.group(1)
                location['state'] = state_match.group(2)
            else:
                location['city'] = city_state
        
        return location
        
    async def _init_session(self):
        """Initialize HTTP session with cookies and headers"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers=self.config['headers'],
                cookies=self.config.get('cookies', {})
            )
    
    async def _close_session(self):
        """Close HTTP session and parser"""
        if self.session is not None:
            await self.session.close()
            self.session = None
        
        # Shutdown the parser process pool
        self.parser.shutdown()
    
    async def fetch_page(self, url: str, params: Dict[str, Any] = None) -> str:
        """
        Fetch a page with rate limiting.
        
        Args:
            url: URL to fetch
            params: Query parameters
            
        Returns:
            Page content as string
        """
        async with self.semaphore:
            # Apply rate limiting
            await asyncio.sleep(self.rate_limit)
            
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.text()
    
    def get_absolute_url(self, relative_url: str) -> str:
        """
        Convert a relative URL to an absolute URL using the base domain.
        
        Args:
            relative_url: Relative URL from the website
            
        Returns:
            Absolute URL
        """
        # If it's already an absolute URL, return it
        if relative_url.startswith('http'):
            return relative_url
        
        # Get the base domain (scheme + netloc only)
        parsed_base = urlparse(self.config.get('base_url', ''))
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        # Use urljoin to properly handle path joining
        return urljoin(base_domain, relative_url)
    
    async def fetch_search_page(self, page_index: int = 0) -> str:
        """
        Fetch a search results page.
        
        Args:
            page_index: Page index (0-based, where 0 is the first page)
            
        Returns:
            Page content as string
        """
        params = self.config['query_params'].copy()
        
        # Get or set default results per page
        results_per_page = int(params.get('maxresults', '20'))
        
        # For pages after the first, add pagination parameters
        if page_index > 0:
            # Add page parameter for pagination (0-based)
            params['page'] = str(page_index)
            
            # Calculate offset based on page number and results per page
            offset = page_index * results_per_page
            params['offset'] = str(offset)
            
            # Ensure maxresults is set
            params['maxresults'] = str(results_per_page)
        
        html = await self.fetch_page(self.config['base_url'], params)
        
        # Save HTML for debugging if requested
        if self.save_html:
            debug_path = Path(f"debug_response_page{page_index}.html")
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
        return html
    
    async def fetch_article_text(self, url: str) -> str:
        """Fetch article page and extract the text"""
        absolute_url = self.get_absolute_url(url)
        html = await self.fetch_page(absolute_url)
        
        # Save article HTML for debugging if requested
        if self.save_html:
            article_id = url.split("docref=")[-1].split("&")[0] if "docref=" in url else "unknown"
            safe_id = re.sub(r'[\\/*?:"<>|]', "_", article_id)
            debug_path = Path(f"debug_article_{safe_id}.html")
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return await self.parser.extract_article_text(html)
    
    async def scrape(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Scrape articles from NewsBank.
        
        Args:
            limit: Optional limit on the number of articles to scrape
            
        Returns:
            List of article data dictionaries
        """
        await self._init_session()
        try:
            # First get search result pages
            first_page_html = await self.fetch_search_page(0)
            total_results = await self.parser.get_total_results(first_page_html)
            
            # Get results per page from config or default to 20
            results_per_page = int(self.config['query_params'].get('maxresults', '20'))
            
            # Calculate total pages
            total_pages = math.ceil(total_results / results_per_page)
            logger.info(f"Found {total_results} results across {total_pages} pages")
            
            # Apply limit if provided
            if limit:
                total_pages = min(math.ceil(limit / results_per_page), total_pages)
                logger.info(f"Limiting to first {total_pages} pages")
            
            # STAGE 1: Get all search result pages concurrently (with progress bar)
            logger.info("Stage 1: Fetching search result pages...")
            search_page_tasks = [self.fetch_search_page(i) for i in range(total_pages)]
            search_pages = []
            
            for f in async_tqdm.as_completed(search_page_tasks, desc="Fetching search pages", total=len(search_page_tasks)):
                search_pages.append(await f)
            
            # STAGE 2: Extract article info from all pages (with progress bar)
            logger.info("Stage 2: Extracting article information...")
            all_articles = []
            
            for i, page_html in enumerate(tqdm(search_pages, desc="Parsing search pages")):
                articles = await self.parser.extract_articles_from_search_page(page_html)
                
                # Add location to each article
                for article in articles:
                    article['location'] = self.location
                
                all_articles.extend(articles)
                
                # Apply limit if needed
                if limit and len(all_articles) >= limit:
                    all_articles = all_articles[:limit]
                    break
            
            # STAGE 3: Fetch article text for all articles (with progress bar)

            if self.full_text:
                logger.info(f"Stage 3: Fetching full text for {len(all_articles)} articles...")
                text_tasks = [self.fetch_article_text(article['article_url']) for article in all_articles]
                article_texts = []
                
                for f in async_tqdm.as_completed(text_tasks, desc="Fetching article texts", total=len(text_tasks)):
                    article_texts.append(await f)
                
            # Format final output
            final_articles = []
            for i in range(len(all_articles)):
                # Get location parts
                location = all_articles[i]['location']
                
                # Create clean article object with only needed fields
                final_article = {
                    'title': all_articles[i]['title'],
                    'date': self.parser.convert_date_to_iso(all_articles[i]['date']),
                    'source': all_articles[i]['source'],
                    'author': all_articles[i]['author'],
                    'location': {
                        'city': location.get('city', ''),
                        'state': location.get('state', ''),
                        'country': location.get('country', '')
                    },
                    'text': article_texts[i] if self.full_text else "",
                    'url': self.get_absolute_url(all_articles[i]['article_url'])
                }
                final_articles.append(final_article)
            
            return final_articles
            
        finally:
            await self._close_session()