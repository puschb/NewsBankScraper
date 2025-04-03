"""
Configuration handler for NewsBank scraper.
Handles loading and parsing configuration files.
"""

import json
import logging
import urllib.parse
from typing import Dict, Any, List



from NewsbankScraper.default_scraper import BASE_URL, HEADERS, DEFAULT_COOKIES, STANDARD_PARAMS

logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load simplified configuration from a JSON file and convert to full config.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the full configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        simple_config = json.load(f)
    
    # Convert the simplified config to the full config format
    full_config = {
        'base_url': BASE_URL,
        'headers': HEADERS,
        'cookies': DEFAULT_COOKIES,
        'query_params': build_query_params(simple_config)
    }
    
    return full_config

def build_query_params(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Build query parameters from the simplified config format.
    
    Args:
        config: Simplified configuration dictionary
        
    Returns:
        Dict of query parameters for the NewsBank API
    """
    # Start with standard parameters
    params = STANDARD_PARAMS.copy()
    
    # Add hide duplicates parameter
    params['hide_duplicates'] = "2" if config.get('hide_duplicates', True) else "0"
    
    # Add location parameters
    location = config.get('location', {})
    location_filter = build_location_filter(location)
    if location_filter:
        params['t'] = location_filter
    
    # Add date range
    date_range = config.get('date_range', {})
    start_date = date_range.get('start', '')
    end_date = date_range.get('end', '')
    if start_date and end_date:
        params['fld-nav-0'] = "YMD_date"
        params['val-nav-0'] = f"{start_date} - {end_date}"
    
    # Add search query and fields
    search = config.get('search', {})
    query_string = search.get('query', '')
    fields = search.get('fields', '')
    
    if query_string and fields:
        query_terms = parse_query_string(query_string)
        field_terms = fields.split()
        
        # Add each query term and field
        for i, (term, field) in enumerate(zip(query_terms, field_terms)):
            params[f'val-base-{i}'] = term['value']
            params[f'fld-base-{i}'] = field
            
            # Add boolean operator if not first term
            if i > 0:
                params[f'bln-base-{i}'] = term['operator'].lower()
    
    # Add max results per page
    params['maxresults'] = str(config.get('max_results_per_page', 60))
    
    return params

def parse_query_string(query_string: str) -> List[Dict[str, str]]:
    """
    Parse a query string like "term1 OR term2 AND term3" into a structured format.
    
    Args:
        query_string: Query string with terms and operators
        
    Returns:
        List of dictionaries with 'value' and 'operator' keys
    """
    # Split the query string to separate terms and operators
    # This is a simplified version - a more robust parser would be needed for complex queries
    terms = []
    parts = query_string.split()
    
    current_term = ""
    current_operator = "AND"  # Default operator
    
    for part in parts:
        if part.upper() in ("AND", "OR"):
            if current_term:  # Add the previous term if it exists
                terms.append({"value": current_term.strip(), "operator": current_operator})
                current_term = ""
            current_operator = part.upper()
        else:
            if current_term:
                current_term += " " + part
            else:
                current_term = part
    
    # Add the last term
    if current_term:
        terms.append({"value": current_term.strip(), "operator": current_operator})
    
    return terms

def build_location_filter(location: Dict[str, str]) -> str:
    """
    Build the location filter string for the query parameters.
    
    Args:
        location: Dictionary with country, state, city
        
    Returns:
        Location filter string
    """
    filter_parts = []
    
    # Add country filter
    country = location.get('country', '')
    if country:
        country_encoded = urllib.parse.quote(country)
        filter_parts.append(f"country:{country}!{country_encoded}")
    
    # Add source type filter (hardcoded for now)
    filter_parts.append("stp:Newspaper|Web-Only+Source!Multiple Source Types (2)")
    
    
    # Add continent filter (hardcoded for North America)
    filter_parts.append("continent:North+America!North+America")
    
    # Add city and state filter
    city = location.get('city', '')
    state = location.get('state', '')
    if city and state:
        city_state = f"{city} ({state})"
        city_state_encoded = urllib.parse.quote(city_state)
        filter_parts.append(f"city:{city_state}!{city_state_encoded}")
    
    # Add language filter
    filter_parts.append("language:English!English")
    
    # Join all filter parts with slash
    print('/'.join(filter_parts))
    return '/'.join(filter_parts)
