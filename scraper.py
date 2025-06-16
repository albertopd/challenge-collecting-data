import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

class ImmowebScraper:
    IMMOWEB_LISTINGS_URL: str = "https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&orderBy=postal_code&page={}" 

    def __init__(self) -> None:
        self.session = requests.Session()
        self.data = []

    def scrape_data(self) -> None:
        page = 0
        there_are_listings = True

        while there_are_listings:
            page += 1
            print(f"Getting listings from page {page}")

            listings_page_url = self.IMMOWEB_LISTINGS_URL.format(page)
            listings_urls = self.get_listing_urls(listings_page_url)
            there_are_listings = len(listings_urls) > 0

            print(f"Found {len(listings_urls)} listings")

            for listing_url in listings_urls:
                listing_data = self.get_listing_data(listing_url)
             
    def get_listing_urls(self, listings_url: str) -> list[str]:
        listings: list[str] = []
        return listings
    
    def get_listing_data(self, listing_url: str) -> list[str]:
        listing_data: list[str] = []
        return listing_data
    
    def save_data(self, filename: str) -> None:
        pass