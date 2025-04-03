# NewsBank Scraper

A Python tool for scraping articles from infoweb.newsbank.com with configurable search parameters.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/newsbank-scraper.git
   cd newsbank-scraper
   ```

2. Install the package:
   ```
   pip install -e .
   ```

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Usage

1. Create a configuration file (see `Configs/sample_config.json` for an example)

2. Run the scraper:
   ```
   python -m NewsbankScraper.main --config Configs/your_config.json --output results.json
   ```

   Or if you installed it as a package:
   ```
   newsbank-scraper --config Configs/your_config.json --output results.json
   ```

### Command-line Arguments

- `-c, --config`: Path to JSON config file with search parameters (required)
- `-o, --output`: Path to save the scraped results as JSON (required)
- `-d, --debug`: Enable debug logging
- `-v, --verbose`: Enable verbose output with more details
- `-s, --save-html`: Save raw HTML responses for debugging
- `-l, --limit`: Limit the number of articles to scrape
- `-r, --rate`: Rate limit in seconds between requests (default: 1.0)
- `--test-request`: Make a single test request and analyze the response (useful for debugging)

#### Debugging Tips

If you're having issues with the scraper, try these approaches:

1. **Test a single request**:
   ```
   newsbank-scraper --config Configs/your_config.json --output test.json --test-request
   ```
   This will make just one request and save the HTML response for inspection.

2. **Enable detailed logging**:
   ```
   newsbank-scraper --config Configs/your_config.json --output results.json --debug --verbose
   ```
   This will show detailed logs including the exact request URLs and equivalent curl commands.

3. **Save HTML responses**:
   ```
   newsbank-scraper --config Configs/your_config.json --output results.json --save-html
   ```
   This saves each page's HTML response as `debug_response_page0.html`, etc., for manual inspection.

## Configuration

The configuration file is a simplified JSON file with the following structure:

```json
{
  "location": {
    "country": "USA",
    "state": "IL",
    "city": "Chicago"
  },
  "hide_duplicates": true,
  "date_range": {
    "start": "2016",
    "end": "2025"
  },
  "search": {
    "query": "immigration OR migrant OR migration OR border",
    "fields": "alltext alltext alltext Title"
  },
  "max_results_per_page": 60
}
```

### Configuration Options

- **location**: Geographic filtering
  - `country`: Country name (e.g., "USA")
  - `state`: State/province code (e.g., "IL")
  - `city`: City name (e.g., "Chicago")

- **hide_duplicates**: Whether to hide duplicate articles (boolean)

- **date_range**: Publication date range
  - `start`: Start year (e.g., "2016")
  - `end`: End year (e.g., "2025")

- **search**: Search terms and fields
  - `query`: Search query with Boolean operators (e.g., "immigration OR migrant OR migration OR border")
  - `fields`: Space-separated list of field types matching the query terms (e.g., "alltext alltext alltext Title")

- **max_results_per_page**: Number of results per page (e.g., 60)

## Output Format

The script outputs a JSON file with an array of article objects:

```json
[
  {
    "title": "Article Title",
    "date": "2025-03-28T00:00:00",
    "source": "Hyde Park Herald: Web Edition Articles (Chicago, IL)",
    "author": "Herald staff report",
    "location": "Chicago, IL",
    "url": "https://infoweb.newsbank.com/apps/news/document-view?p=...",
    "text": "Full article text..."
  },
  ...
]
```

## License

MIT