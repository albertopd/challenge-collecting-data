import time
import requests
import csv
import random
from random import randint
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fake_headers import Headers

class Scraper:
    # File names
    LISTINGS_URLS_FILE = "listings_urls.txt"
    LISTINGS_DATA_FILE = "listings_data.csv"

    # Immovlan listings URL
    LISTINGS_URL = "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=apartment,house&propertysubtypes=apartment,ground-floor,penthouse,studio,duplex,loft,triplex,residence,villa,mixed-building,master-house,bungalow,cottage,chalet,mansion&page=2&noindex=1"

    # Listing fields
    FIELD_URL = "URL"
    FIELD_LOCALITY = "Locality"
    FIELD_POSTAL_CODE = "Postal Code"
    FIELD_TYPE = "Type of property"
    FIELD_PRICE: str = "Price"
    FIELD_BEDROOMS = "Number of bedrooms"
    FIELD_BATHROOMS = "Number of bathrooms"
    FIELD_LIVING_AREA = "Living area"
    FIELD_CONSTRUCTION_YEAR = "Construction year"
    FIELD_FACADES = "Number of facades"
    FIELD_EPB = "EPB"
    FIELD_ENERGY_CLASS = "Energy class"
    FIELD_NAMES = [
        FIELD_LOCALITY,
        FIELD_POSTAL_CODE,
        FIELD_TYPE,
        FIELD_PRICE,
        FIELD_BEDROOMS, 
        FIELD_BATHROOMS,
        FIELD_LIVING_AREA,
        FIELD_CONSTRUCTION_YEAR,
        FIELD_FACADES,
        FIELD_EPB,
        FIELD_ENERGY_CLASS,
        FIELD_URL
    ]

    LISTING_FULL_KITCHEN = "Fully equipped kitchen" # 1/0
    LISTING_FURNISHED = "Furnished" # 1/0
    LISTING_OPEN_FIRE = "Open fire" # 1/0
    LISTING_TERRACE = "Terrace"  # 1/0
    LISTING_TERRACE_AREA = "Terrace area"
    LISTING_GARDEN = "Garden" # 1/0
    LISTING_GARDEN = "Garden area"
    LISTING_SURFACE_LAND = "Surface of the land"
    LISTING_SURFACE_PLOT_LAND =  "Surface area of the plot of land"
    LISTING_SWIMMING_POOL = "Swimming pool" # 1/0
    LISTING_STATE = "State of the building" # New, to be renovated, ...

    def __init__(self) -> None:
        self.data: list[dict] = []

    def scrape_data(self) -> None:
        all_listing_urls = self.__get_all_listing_urls()

        with open(self.LISTINGS_DATA_FILE, 'w', newline='\n') as csvfile:

            writer = csv.DictWriter(csvfile, fieldnames = self.FIELD_NAMES)
            writer.writeheader()

            for listing_url in all_listing_urls[:3]: # TODO: Remove limit 
                listing_data = self.__get_listing_data(listing_url.strip())

                if listing_data:
                    self.data.append(listing_data)
                
                writer.writerow(listing_data)

                # Add a delay to avoid blocking
                time.sleep(randint(0, 1))

    def __get_headers(self) -> dict:
        """
        Generate randomized, realistic HTTP headers to reduce request blocking.
        
        The function selects random combinations of browser and OS
        to generate diverse and legitimate-looking headers.
        """
        browsers = ["chrome", "firefox", "opera", "safari", "edge"]
        os_choices = ["win", "mac", "linux"]

        headers = Headers(
            browser=random.choice(browsers),
            os=random.choice(os_choices),
            headers=True
        )
        return headers.generate()

    def __get_all_listing_urls(self) -> list[str]:
        # Try to load URLs from previous file
        all_listing_urls = self.__load_urls_from_file(self.LISTINGS_URLS_FILE)

        if len(all_listing_urls) == 0:
            page = 0
            there_are_listings = True

            while len(all_listing_urls) < 36000 and there_are_listings:
                page += 1
                print(f">> Getting listings URLs from page {page}")

                listings_page_url = self.LISTINGS_URL.format(page)
                response = requests.get(
                    listings_page_url,
                    headers = self.__get_headers()
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all("article")

                found_urls_count = 0
                for article in articles:
                    if article.has_attr("data-url"):
                        all_listing_urls.append(article["data-url"])
                        found_urls_count += 1

                print(f"Found {found_urls_count} listings")

                # Add a delay to avoid blocking
                time.sleep(randint(0, 1))
            
            if len(all_listing_urls) > 0:
                self.__save_urls_to_file(all_listing_urls, self.LISTINGS_URLS_FILE)

        return all_listing_urls

    def __save_urls_to_file(self, urls: list[str], filename: str) -> None:
        try:
            with open(filename, 'w') as urls_file:
                urls_file.writelines(url + '\n' for url in urls)
        except Exception as e:
            print(f"[ERROR] Failed to save URLs to file: {filename} => {e}")

    def __load_urls_from_file(self, filename: str) -> list[str]:
        try:
            with open(filename, 'r') as urls_file:
                return urls_file.readlines()
        except Exception as e:
            print(f"[ERROR] Failed to load URLs from file: {filename} => {e}")
            return []

    def __get_listing_data(self, listing_url: str) -> dict:
        try:
            print(f">>>> Scraping listing data from page => {listing_url}")

            response = requests.get(
                listing_url,
                headers = self.__get_headers()
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            listing_data = self.__parse_data_rows(soup)
            listing_data.update(self.__parse_address(soup))
            listing_data[self.FIELD_PRICE] = self.__parse_pricing(soup)
            listing_data[self.FIELD_URL] = listing_url

            return listing_data     
        except Exception as e:
            print(f"[ERROR] Failed to parse listing data from page: {listing_url} => {e}")
            return {}

    def __parse_data_rows(self, soup) -> dict:
        listing_data = {}

        try:
            data_rows = soup.find_all(class_ = "data-row-wrapper")

            for data_row in data_rows:
                data_divs = data_row.find_all("div")

                for data_div in data_divs:
                    data_label = data_div.find("h4")
                    if not data_label:
                        continue

                    data_value = data_div.find("p")
                    if not data_value:
                        continue

                    data_label_text = data_label.text.strip()
                    data_value_text = data_value.text.strip()

                    match data_label_text:
                        case "Type":
                            listing_data[self.FIELD_TYPE] = data_value_text
                        case "Livable surface":
                            try:
                                listing_data[self.FIELD_LIVING_AREA] = int(data_value_text.split(' ')[0])
                            except Exception as ie:
                                listing_data[self.FIELD_LIVING_AREA] = None
                                print(f"[ERROR] Failed to parse living area => {ie}")
                        case "Number of bedrooms":
                            try:
                                listing_data[self.FIELD_BEDROOMS] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_BEDROOMS] = None
                                print(f"[ERROR] Failed to parse number of bedrooms => {ie}")
                        case "Number of bathrooms":
                            try:
                                listing_data[self.FIELD_BATHROOMS] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_BATHROOMS] = None
                                print(f"[ERROR] Failed to parse number of bathrooms => {ie}")
                        case "Build Year":
                            try:
                                listing_data[self.FIELD_CONSTRUCTION_YEAR] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_CONSTRUCTION_YEAR] = None
                                print(f"[ERROR] Failed to parse construction year => {ie}")
                        case "Number of facades":
                            try:
                                listing_data[self.FIELD_FACADES] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_FACADES] = None
                                print(f"[ERROR] Failed to parse number of facades => {ie}")
                        case "Specific primary energy consumption":
                            try:
                                listing_data[self.FIELD_EPB] = int(data_value_text.split(' ')[0])
                                listing_data[self.FIELD_ENERGY_CLASS] = self.__get_epb_class(listing_data[self.FIELD_EPB])
                            except Exception as ie:
                                listing_data[self.FIELD_EPB] = None
                                print(f"[ERROR] Failed to parse EPB => {ie}")   
                        
        except Exception as e:
            print(f"[ERROR] Failed to parse main features => {e}")

        return listing_data
    
    def __parse_address(self, soup) -> dict:
        try:
            city_line = soup.find(class_ = "city-line")

            if city_line:
                parts = city_line.text.strip().split(' ')

                return {
                    self.FIELD_POSTAL_CODE: int(parts[0]),
                    self.FIELD_LOCALITY: parts[1]
                }
            else:
                return {}
        except Exception as e:
            print(f"[ERROR] Failed to parse address => {e}")
            return {}

    def __parse_pricing(self, soup) -> float | None:
        try:
            price_tag = soup.find(class_ = "detail__header_price_data")
            price_text = price_tag.text.strip().replace(" €", "").replace("\u202f", "")
            return int(price_text)
        except Exception as e:
            print(f"[ERROR] Failed to parse pricing => {e}")
            return None
        
    def __get_epb_class(self, epb: int) -> str:
        """
        Returns the EPB class based on the Brussels-Capital Region thresholds.
        :param epb: Primary energy value in kWh PE/m²·year (integer)
        :return: EPB class as a string
        """
        thresholds = [
            (epb < 0, "A++"),
            (0 <= epb < 15, "A+"),
            (15 <= epb < 30, "A"),
            (30 <= epb < 45, "A-"),
            (45 <= epb < 62, "B+"),
            (62 <= epb < 78, "B"),
            (78 <= epb < 95, "B-"),
            (95 <= epb < 113, "C+"),
            (113 <= epb < 132, "C"),
            (132 <= epb < 150, "C-"),
            (150 <= epb < 170, "D+"),
            (170 <= epb < 190, "D"),
            (190 <= epb < 210, "D-"),
            (210 <= epb < 232, "E+"),
            (232 <= epb < 253, "E"),
            (253 <= epb < 275, "E-"),
            (275 <= epb < 345, "F"),
            (epb >= 345, "G"),
        ]

        for condition, epb_class in thresholds:
            if condition:
                return epb_class

        return "Unknown"