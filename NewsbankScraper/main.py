#!/usr/bin/env python3
"""
NewsBank Scraper - Main entry point
This script coordinates the scraping of articles from infoweb.newsbank.com
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from NewsbankScraper.config import load_config
from NewsbankScraper.scraper import NewsBankScraper


def setup_logging(debug=False):
    """Configure logging"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Scrape NewsBank search results")
    parser.add_argument(
        "-c", "--config", required=True, help="Path to JSON config file with search parameters"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to save the scraped results as JSON"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "-s", "--save-html", action="store_true", help="Save HTML responses for debugging"
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=None, 
        help="Limit the number of articles to scrape (default: all available)"
    )
    parser.add_argument(
        "-r", "--rate", type=float, default= 0.3,
        help="Rate limit in seconds between requests (default: 1.0)"
    )
    parser.add_argument(
        "-n", "--concurrency", type=int, default=10,
        help="Maximum number of concurrent requests (default: 10)"
    )
    parser.add_argument(
        "-p", "--processors", type=int, default=None,
        help="Number of CPU processors to use for parsing (default: half of available cores)"
    )

    parser.add_argument(
        "-f", "--full_text", action="store_true",  
        help="Enable scraping of full text (default: False)"
    )

    return parser.parse_args()


async def main():
    """Main entry point"""
    args = parse_args()
    setup_logging(args.debug)
    logger = logging.getLogger("NewsbankScraper")

    # Load configuration
    config = load_config(args.config)
    logger.info(f"Loaded configuration from {args.config}")

    # Initialize scraper with parser
    scraper = NewsBankScraper(
        config=config,
        rate_limit=args.rate,
        save_html=args.save_html,
        concurrency=args.concurrency,
        num_processors=args.processors,
        full_text=args.full_text
    )
    
    # Run scraper
    logger.info(f"Starting scraping process with concurrency: {args.concurrency}")
    articles = await scraper.scrape(limit=args.limit)
    logger.info(f"Scraped {len(articles)} articles")

    # Save results
    output_path = Path(args.output)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))