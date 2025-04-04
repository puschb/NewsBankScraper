"""
Default configuration settings for NewsBank scraper.
This module contains all the standard settings that don't change between scraping sessions.
"""

# Standard base URL for NewsBank search
BASE_URL = "https://infoweb.newsbank.com/apps/news/results"

# Standard headers for requests
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "upgrade-insecure-requests": "1"
}

# Standard cookies for authentication
# These will need to be updated if authentication expires
DEFAULT_COOKIES = {
    "gnus_advanced_search_map": "true",
    "SSESSd9c4cf748ca49c2a057546a885da9b19": "PBTZXWPYdqnTUP00gIkmro6ZpY80K1vftfOmSipbf70",
    "_ga": "GA1.1.2073962454.1743538352",
    "fileDownload": "true",
    "__Host-next-auth.csrf-token": "a908913fcf8d8f92fa04720b851e218bfe39f4339df5d9a775fd7f06e52673e0%7C11f3692bd4f80bcb9a23b31c82abe176beb7ca3463cc174be8095a4c498dbc51",
    "__Secure-next-auth.callback-url": "https%3A%2F%2Finfoweb.newsbank.com%2Fhome",
    "AWSALB": "ADNoxTbMWGOgJ3KRGSMtTT992yOc7Vl3wd11WFgpRjOGJtS2jlYM/J9y/XKZ8uSJ2vwVMRypryXIC+DBjBatXKbGgf1t2HgsH9mzQx0DX1MgJjcexp6BjwzLCF/r",
    "AWSALBCORS": "ADNoxTbMWGOgJ3KRGSMtTT992yOc7Vl3wd11WFgpRjOGJtS2jlYM/J9y/XKZ8uSJ2vwVMRypryXIC+DBjBatXKbGgf1t2HgsH9mzQx0DX1MgJjcexp6BjwzLCF/r",
    "sugar": "W46Y49KEMTc0MzU0MDg5OC44OTQwNjE6MToxNToxOTkuMTExLjIyNC4yMDk",
    "__Secure-next-auth.session-token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..Gh4TS9HBu79bCUZB.WLjItDKIkFLM_oOfH_N4T3boiCVd1GFpjzN1KEGk1rHcxiipAHghHl1fGD7NpFAMWYx7Eu127fgypKUVAlxebXrjNq5IN5ym2IWkUEpDnC0qvyBev0sy7_KCLiNh3D8p7P-wkz3hBfjqRvGXaG4uF_y3-j7oSHyW17qzxfY5P-705LQ89zXun-7ODNMWw4CBSOTR4VXMNlR7dz9d_1FS97nIxDRiQOob7zLrZFbFWtHVcDyQfz1ZYwao7Ox5_rNZzREmzwN5J2x98Smp1sLOyDVv3Fy5YT6RoqNH-xEDEw-AAqB3DUtSClSjQx7KYgdJDLtC64fzrl7OdqT_wA9VVhswoxYo7Ssmjx2jiiq2XitSY3bPn4TEqsoCBq1iJBtdOwuSumvUpFzH5oa6fqj6ItXVbzLWVGpdSw88HY3F3B-rUxr5zOcbZpc-M4tQgnJD9Nw0po2MRHI_UnXgfKgpi68I-YNUPzvweeVhWGB0vgLe-C94vLRSlXK8QyuoPCDwF9R1NiDs-O0uYKgL6EnBzmKtz1OMGchh2iPguprWeoadLjgGVra_Q412GWt8VjGskBS88Awget-C0pmUJdkDR5XbRUDlbPRMrXp6KXB_zl1q6njFlI6wJCcip7xOJteX8Nn0Wt52rQrrK5t29RNRfSk7u8LOyl7vuS5P4XgdR5w2U3W0Ro7zGLR2VQo8JMHX5o4pGRBdzoqB9bFmKQK-dQIKmGFq3uD02l5Apwqd-MKjH2-2RuqecTn0_RdPmei7z31uHcNy0JzKSMhLCTGGMIEIe5JD-wfeQuJaVoJpBVBqPJCQXaY5308x3z0awpNb544IE8jvHdoFbaWxQSeo5zqyWdkKQvxMSR7pZxgmUsfaux1AmpsOor6hRFUNeu2T4QzvMpikE81F_EsmiFhDCmP7OgwEa5ouN5DVga_rnE_J-X9XI7Gots6QUmlihd6bqxHh3S0a-54ts-9yL2sq_bQXRmUSJYtX18oS0N4VRQktQvx9n9za4oN8ShHcb7QEv9YJj1nf2gHBLLPP7S-taAxJtpQ0Wo5GdyqxEjWOrr4VAwEDzx45WJ7EmdWHDviAAyJ0LPDVZ0dypyDMO6ZXHffS7GvNMvvqZBn2ZhiW9wlON_-VafAva4w0yer4ty80IYi-q9-Mz_AhtL39rZlBFeS0VdwBgaV7ODXycfyvl1eckOMQfBlZBjRpZDsKtYmVSJfKh3-p8yfm5SRL0RarZFBicdwtsX1ZlQwlmei3DSMxSwWNhnNB21ficG2KT7ESiqwdP0qPO21-PLa1um6jaxfjldRI_eFliGevdiPCmwZKTC0MMBlRwK-Q2Q66twQWJHIGBfIXFzwRotJWhNiHmenCMEYXEJmX6pZZKRBnmf7LwXyLLsqKq21JwkWGcbchcFrz-tvI0zMFabHf_YzAgLJOPJuh0TRBmo1dTFCpsqvg-nVfgHr_StR1s_MOn3-0nWzjNeKY-TbqMZ0o_OfjHzXapbrqcPtVWKU_LoHScTjrEQCsBZqKJpNlwDp41zRe1HdxZF2uW9ECzpMl4B93.vMAq6FZayRk0rj8QOut-OQ"
}

# Standard query parameters that don't change between searches
STANDARD_PARAMS = {
    "sort": "YMD_date:D",
    "p": "WORLDNEWS",
    "f": "advanced"
}