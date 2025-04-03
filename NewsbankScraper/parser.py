"""
Parser class for NewsBank scraper.
Handles extracting data from HTML using multiprocessing for performance.
"""

import logging
import re
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Any, Optional
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

from bs4 import BeautifulSoup
from newspaper import Article

logger = logging.getLogger(__name__)


# Define standalone functions for multiprocessing (must be at module level)
@lru_cache(maxsize=100)
def parse_html(html: str) -> BeautifulSoup:
    """
    Parse HTML with caching for better performance.
    
    Args:
        html: HTML string to parse
        
    Returns:
        BeautifulSoup object
    """
    return BeautifulSoup(html, 'lxml')


def extract_total_results_mp(html: str) -> int:
    """
    Standalone function to extract total results (for multiprocessing).
    
    Args:
        html: HTML content of the search page
        
    Returns:
        Total number of results as an integer
    """
    soup = parse_html(html)
    
    # Get total hits from the results element
    hits_div = soup.select_one('.search-hits__meta--total_hits, .search-hitsmeta--total_hits')
    
    if hits_div:
        hits_text = hits_div.get_text(strip=True)
        hits_match = re.search(r'([\d,]+)', hits_text)
        if hits_match:
            # Remove commas from number (e.g., "1,022" -> "1022")
            return int(hits_match.group(1).replace(',', ''))
    
    # Fallback: count articles on the page and assume there are more
    articles = soup.select('article.search-hits__hit, .search-hits__hit')
    if articles:
        return len(articles) * 5  # Assume at least 5 pages
    
    return 0


def extract_articles_mp(html: str) -> List[Dict[str, Any]]:
    """
    Standalone function to extract articles (for multiprocessing).
    
    Args:
        html: HTML content of the search page
        
    Returns:
        List of article preview dictionaries
    """
    soup = parse_html(html)
    articles = []
    
    # Find all article elements - need to try multiple selectors
    article_elements = soup.select('article.search-hits__hit')
    if not article_elements:
        # If first selector fails, try a more generic one
        article_elements = soup.select('div.search-hits__hit')
    
    if not article_elements:
        # If we still can't find any articles, raise an error
        raise ValueError("No article elements found in the HTML")
    
    for article_elem in article_elements:
        # Extract article ID
        article_id = article_elem.get('data-docref', '')
        
        # We need to try multiple selectors for title since the HTML structure varies
        title_elem = None
        for selector in ['.search-hits__hit__title a', 'h3.search-hits__title a', 'a[href*="document-view"]']:
            title_elem = article_elem.select_one(selector)
            if title_elem:
                break
                
        if not title_elem:
            raise ValueError(f"Could not find title element for article: {article_id}")
            
        title = title_elem.get_text(strip=True)
        # Remove "Go to the document viewer for " prefix if present
        if "Go to the document viewer for" in title:
            title = title.replace("Go to the document viewer for", "").strip()
        
        url = title_elem.get('href')
        
        # Try multiple selectors for metadata items
        date_elem = article_elem.select_one('.search-hits__hit__meta__item--display-date, li[class*="date"]')
        source_elem = article_elem.select_one('.search-hits__hit__meta__item--source, li[class*="source"]')
        author_elem = article_elem.select_one('.search-hits__hit__meta__item--author, li[class*="author"]')
        
        if not date_elem or not source_elem:
            # Look for metadata list items if we couldn't find with specific selectors
            meta_items = article_elem.select('.search-hits__hit__meta li, ul.search-hits__hit__meta li')
            for item in meta_items:
                item_text = item.get_text(strip=True)
                item_class = ' '.join(item.get('class', []))
                
                if not date_elem and ('date' in item_class or re.match(r'^[A-Z][a-z]+ \d{1,2}, \d{4}$', item_text)):
                    date_elem = item
                elif not source_elem and ('source' in item_class):
                    source_elem = item
                elif not author_elem and ('author' in item_class):
                    author_elem = item
        
        if not date_elem or not source_elem:
            raise ValueError(f"Missing required metadata for article: {article_id}")
            
        date = date_elem.get_text(strip=True)
        source = source_elem.get_text(strip=True)
        author = author_elem.get_text(strip=True) if author_elem else ""
        
        # Add to articles list
        articles.append({
            'article_id': article_id,
            'title': title,
            'article_url': url,
            'date': date,
            'source': source,
            'author': author,
        })
    
    return articles


def extract_article_text_mp(html: str) -> str:
    """
    Standalone function to extract article text (for multiprocessing).
    
    Args:
        html: HTML content of the article page
        
    Returns:
        Article text as a string
    """
    soup = parse_html(html)
    
    # Get the main content using multiple possible selectors
    content_elem = None
    for selector in ['.document-view__body', '.document-body', '.article-body']:
        content_elem = soup.select_one(selector)
        if content_elem:
            break
    
    # If we found content directly, return it
    if content_elem:
        return content_elem.get_text(strip=True)
    
    # Otherwise use newspaper3k
    article = Article('')
    article.set_html(html)
    article.parse()
    
    if not article.text:
        # If we still have no text, raise an error
        raise ValueError("Could not extract article text using any method")
            
    return article.text


class NewsBankParser:
    """Class to handle parsing of NewsBank HTML content with multiprocessing"""
    
    def __init__(self, num_workers: Optional[int] = None):
        """
        Initialize the parser with a process pool.
        
        Args:
            num_workers: Number of worker processes to use (default: half of available cores)
        """
        self.num_workers = num_workers or max(multiprocessing.cpu_count() // 2, 1)
        self.process_pool = None
        logger.info(f"Initialized parser with {self.num_workers} workers")
        
        # Start the process pool immediately
        self.start()
    
    def start(self):
        """Start the process pool if not already running"""
        if self.process_pool is None:
            self.process_pool = ProcessPoolExecutor(max_workers=self.num_workers)
            logger.debug(f"Started process pool with {self.num_workers} workers")
    
    def shutdown(self):
        """Shutdown the process pool if running"""
        if self.process_pool:
            self.process_pool.shutdown()
            self.process_pool = None
            logger.debug("Shut down process pool")
    
    async def get_total_results(self, html: str) -> int:
        """
        Get the total number of search results using the process pool.
        
        Args:
            html: HTML content of the search page
            
        Returns:
            Total number of results as an integer
        """
        # Ensure process pool is started
        self.start()
        
        # Direct synchronous execution for simplicity and reliability
        if True:  # Set to False to use process pool
            # Direct execution without process pool
            return extract_total_results_mp(html)
        else:
            # Process pool execution
            future = self.process_pool.submit(extract_total_results_mp, html)
            return future.result()
    
    async def extract_articles_from_search_page(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract article data from search results page using the process pool.
        
        Args:
            html: HTML content of the search page
            
        Returns:
            List of article preview dictionaries
        """
        # Ensure process pool is started
        self.start()
        
        # Submit the task to the process pool
        future = self.process_pool.submit(extract_articles_mp, html)
        # Wait for the result
        return future.result()
    
    async def extract_article_text(self, html: str) -> str:
        """
        Extract article text from article page using the process pool.
        
        Args:
            html: HTML content of the article page
            
        Returns:
            Article text as a string
        """
        # Ensure process pool is started
        self.start()
        
        # Submit the task to the process pool
        future = self.process_pool.submit(extract_article_text_mp, html)
        # Wait for the result
        return future.result()
    
    @staticmethod
    def convert_date_to_iso(date_str: str) -> str:
        """
        Convert date string to ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Date string from the article (e.g., "November 29, 2024")
            
        Returns:
            Date in ISO format (e.g., "2024-11-29")
        """
        # NewsBank dates are in format: "Month DD, YYYY" (e.g., "November 29, 2024")
        parsed_date = datetime.strptime(date_str, '%B %d, %Y')
        return parsed_date.strftime('%Y-%m-%d')