import time
import requests
import csv
import random
from random import randint
from pathlib import Path
from bs4 import BeautifulSoup
from fake_headers import Headers

class Scraper:
    """
    A web scraper for extracting real estate listings from Immovlan.

    This scraper retrieves property listings, parses relevant attributes such as
    price, surface area, number of rooms, and EPB classification, and saves the
    data into a CSV file. It also supports resuming from a specific URL.

    Attributes:
        data (list[dict]): A list of dictionaries containing parsed listing data.
    """

    # Immovlan listings URL
    LISTINGS_URL = "https://immovlan.be/en/real-estate?transactiontypes=for-sale,in-public-sale&propertytypes=apartment,house&propertysubtypes=apartment,ground-floor,penthouse,studio,duplex,loft,triplex,residence,villa,mixed-building,master-house,bungalow,cottage,chalet,mansion&page=2&noindex=1"

    # Listing fields
    FIELD_URL = "URL"
    FIELD_TYPE = "Type of property"
    FIELD_STATE = "State of the property"
    FIELD_LOCALITY = "Locality"
    FIELD_POSTAL_CODE = "Postal Code"
    FIELD_PRICE: str = "Price"
    FIELD_BEDROOMS = "Number of bedrooms"
    FIELD_BATHROOMS = "Number of bathrooms"
    FIELD_TOILETS = "Number of toilets"
    FIELD_LIVING_AREA = "Living area"
    FIELD_CONSTRUCTION_YEAR = "Construction year"
    FIELD_FURNISHED = "Furnished"
    FIELD_FACADES = "Number of facades"
    FIELD_EPB = "EPB"
    FIELD_ENERGY_CLASS = "Energy class"
    FIELD_FULL_KITCHEN = "Fully equipped kitchen"
    FIELD_TERRACE = "Terrace" 
    FIELD_TERRACE_AREA = "Terrace area"
    FIELD_GARDEN = "Garden"
    FIELD_GARDEN_AREA = "Garden area"
    FIELD_SWIMMING_POOL = "Swimming pool"
    FIELD_GARAGE = "Garage"
    FIELD_BIKE_STORAGE = "Bike storage"
    FIELD_BALCONY = "Balcony"
    FIELD_CELLAR = "Cellar"
    FIELD_ATTIC = "Attic"
    FIELD_FLOOR_NUMBER = "Floor number"
    FIELD_ELEVATOR = "Elevator"
    FIELD_AC = "Air conditioning"
    FIELD_ALARM = "Alarm"
    FIELD_ACCESS_DISABLED = "Access for disabled"
    FIELD_HEATING_TYPE = "Type of heating"
    FIELD_NAMES = [
        FIELD_TYPE,
        FIELD_STATE,
        FIELD_LOCALITY,
        FIELD_POSTAL_CODE,
        FIELD_PRICE,
        FIELD_BEDROOMS, 
        FIELD_BATHROOMS,
        FIELD_TOILETS,
        FIELD_LIVING_AREA,
        FIELD_CONSTRUCTION_YEAR,
        FIELD_FURNISHED,
        FIELD_FACADES,
        FIELD_EPB,
        FIELD_ENERGY_CLASS,
        FIELD_FULL_KITCHEN,
        FIELD_TERRACE,
        FIELD_TERRACE_AREA,
        FIELD_GARDEN,
        FIELD_GARDEN_AREA,
        FIELD_SWIMMING_POOL,
        FIELD_GARAGE,
        FIELD_BIKE_STORAGE,
        FIELD_BALCONY,
        FIELD_CELLAR,
        FIELD_ATTIC,
        FIELD_FLOOR_NUMBER,
        FIELD_ELEVATOR,
        FIELD_AC,
        FIELD_ALARM,
        FIELD_ACCESS_DISABLED,
        FIELD_HEATING_TYPE,
        FIELD_URL
    ]

    def __init__(self) -> None:
        """
        Initialize the Scraper instance with an empty data list.
        """
        self.data: list[dict] = []

    def scrape_data(self, output_csv_file: str, urls_txt_file: str, max_urls: int, start_from_url: str = "") -> None:
        """
        Main scraping function to collect real estate data and write it to a CSV file.

        Args:
            output_csv_file (str): Path to the CSV file to write scraped data.
            urls_txt_file (str): File to store/retrieve listing URLs for efficiency.
            max_urls (int): Maximum number of listing URLs to scrape.
            start_from_url (str, optional): URL from which to resume scraping. Defaults to "".
        """
        listing_urls = self.__get_listing_urls(urls_txt_file, max_urls)

        start_from = 0
        if start_from_url:
            try:
                print(f"Start parsing from URL: {start_from_url}")
                start_from = listing_urls.index(start_from_url)
            except ValueError as ve:
                print(ve)   

        # If we are starting from a specific URL, then we will append to the existing file
        mode = 'w' if start_from == 0 else 'a'

        with open(output_csv_file, mode, newline='\n') as csvfile:

            writer = csv.DictWriter(csvfile, fieldnames = self.FIELD_NAMES)

            # Only write the header if we are not starting from an specific URL
            if start_from == 0:
                writer.writeheader()

            for listing_url in listing_urls[start_from:]: 
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

    def __get_listing_urls(self, urls_txt_file: str, max_urls) -> list[str]:
        """
        Retrieve or generate a list of property listing URLs.

        Args:
            urls_txt_file (str): Path to a text file to cache listing URLs.
            max_urls (int): Maximum number of URLs to retrieve.

        Returns:
            list[str]: A list of listing URLs.
        """

        # Try to load URLs from previus saved file
        listing_urls = self.__load_urls_from_file(urls_txt_file)

        if not listing_urls:
            page = 0
            there_are_listings = True

            while len(listing_urls) < max_urls and there_are_listings:
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
                        listing_urls.append(article["data-url"])
                        found_urls_count += 1

                print(f"Found {found_urls_count} listings")

                # Add a delay to avoid blocking
                time.sleep(randint(0, 1))
            
            if listing_urls:
                self.__save_urls_to_file(listing_urls, urls_txt_file)

        return listing_urls

    def __save_urls_to_file(self, urls: list[str], filename: str) -> None:
        """
        Save listing URLs to a file.

        Args:
            urls (list[str]): List of URLs to save.
            filename (str): File path where URLs will be written.
        """
        try:
            with open(filename, 'w') as urls_file:
                urls_file.writelines(url + '\n' for url in urls)
        except Exception as e:
            print(f"[ERROR] Failed to save URLs to file: {filename} => {e}")

    def __load_urls_from_file(self, filename: str) -> list[str]:
        """
        Load listing URLs from a text file if it exists.

        Args:
            filename (str): Path to the file containing saved URLs.

        Returns:
            list[str]: List of URLs loaded from file.
        """
        try:
            if Path(filename).exists():
                with open(filename, 'r') as urls_file:
                    return [line.rstrip() for line in urls_file]
        except Exception as e:
            print(f"[ERROR] Failed to load URLs from file: {filename} => {e}")
        return []

    def __get_listing_data(self, listing_url: str) -> dict:
        """
        Scrape and parse data for a single property listing.

        Args:
            listing_url (str): URL of the property listing.

        Returns:
            dict: Parsed data fields for the listing.
        """
        listing_data: dict = {}

        try:
            print(f">>>> Scraping listing data from page => {listing_url}")

            response = requests.get(
                listing_url,
                headers = self.__get_headers()
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            listing_type = self.__parse_listing_type(soup)

            if not listing_type or listing_type == "Project":
                print(f"Skipping property because of type: {listing_type}")
            else:
                listing_data[self.FIELD_TYPE] = listing_type
                listing_data.update(self.__parse_data_rows(soup))
                listing_data.update(self.__parse_address(soup))
                listing_data[self.FIELD_PRICE] = self.__parse_pricing(soup)
                listing_data[self.FIELD_URL] = listing_url
        
        except Exception as e:
            print(f"[ERROR] Failed to parse listing data from page: {listing_url} => {e}")
            
        return listing_data

    def __parse_listing_type(self, soup) -> str:
        """
        Extract the property type from the listing HTML.

        Args:
            soup (BeautifulSoup): Parsed HTML of the listing page.

        Returns:
            str: Property type or empty string if not found.
        """
        try:
            title = soup.find(class_ = "detail__header_title_main")

            if title:
                return title.text.strip().split(' ')[0].replace(':', '')

        except Exception as e:
            print(f"[ERROR] Failed to parse: {self.FIELD_TYPE} => {e}")

        return ""
    
    def __parse_data_rows(self, soup) -> dict:
        """
        Parse the core property details from the listing.

        Args:
            soup (BeautifulSoup): Parsed HTML of the listing page.

        Returns:
            dict: Dictionary of property features and values.
        """
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
                        case "State of the property":
                            listing_data[self.FIELD_STATE] = data_value_text
                        case "Livable surface":
                            try:
                                listing_data[self.FIELD_LIVING_AREA] = int(data_value_text.split(' ')[0])
                            except Exception as ie:
                                listing_data[self.FIELD_LIVING_AREA] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_LIVING_AREA} => {ie}")
                        case "Number of bedrooms":
                            try:
                                listing_data[self.FIELD_BEDROOMS] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_BEDROOMS] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_BEDROOMS} => {ie}")
                        case "Number of bathrooms":
                            try:
                                listing_data[self.FIELD_BATHROOMS] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_BATHROOMS] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_BATHROOMS} => {ie}")
                        case "Number of toilets":
                            try:
                                listing_data[self.FIELD_TOILETS] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_TOILETS] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_TOILETS} => {ie}")
                        case "Build Year":
                            try:
                                listing_data[self.FIELD_CONSTRUCTION_YEAR] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_CONSTRUCTION_YEAR] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_CONSTRUCTION_YEAR} => {ie}")
                        case "Furnished":
                            try:
                                listing_data[self.FIELD_FURNISHED] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_FURNISHED] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_FURNISHED} => {ie}") 
                        case "Number of facades":
                            try:
                                listing_data[self.FIELD_FACADES] = int(data_value_text)
                            except Exception as ie:
                                listing_data[self.FIELD_FACADES] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_FACADES} => {ie}")
                        case "Specific primary energy consumption":
                            try:
                                listing_data[self.FIELD_EPB] = int(data_value_text.split(' ')[0])
                                listing_data[self.FIELD_ENERGY_CLASS] = self.__get_epb_class(listing_data[self.FIELD_EPB])
                            except Exception as ie:
                                listing_data[self.FIELD_EPB] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_EPB} => {ie}")
                        case "Kitchen equipment":
                            try:
                                listing_data[self.FIELD_FULL_KITCHEN] = int(data_value_text != "")
                            except Exception as ie:
                                listing_data[self.FIELD_FULL_KITCHEN] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_FULL_KITCHEN} => {ie}")
                        case "Terrace":
                            try:
                                listing_data[self.FIELD_TERRACE] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_TERRACE] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_TERRACE} => {ie}")
                        case "Surface terrace":
                            try:
                                listing_data[self.FIELD_TERRACE_AREA] = int(data_value_text.split(' ')[0])
                            except Exception as ie:
                                listing_data[self.FIELD_TERRACE_AREA] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_TERRACE_AREA} => {ie}")
                        case "Garden":
                            try:
                                listing_data[self.FIELD_GARDEN] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_GARDEN] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_GARDEN} => {ie}")
                        case "Surface garden":
                            try:
                                listing_data[self.FIELD_GARDEN_AREA] = int(data_value_text.split(' ')[0])
                            except Exception as ie:
                                listing_data[self.FIELD_GARDEN_AREA] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_GARDEN_AREA} => {ie}")
                        case "Swimming pool":
                            try:
                                listing_data[self.FIELD_SWIMMING_POOL] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_SWIMMING_POOL] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_SWIMMING_POOL} => {ie}")
                        case "Garage":
                            try:
                                listing_data[self.FIELD_GARAGE] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_GARAGE] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_GARAGE} => {ie}")
                        case "Bike storage":
                            try:
                                listing_data[self.FIELD_BIKE_STORAGE] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_BIKE_STORAGE] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_BIKE_STORAGE} => {ie}")
                        case "Balcony":
                            try:
                                listing_data[self.FIELD_BALCONY] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_BALCONY] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_BALCONY} => {ie}")
                        case "Cellar":
                            try:
                                listing_data[self.FIELD_CELLAR] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_CELLAR] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_CELLAR} => {ie}")
                        case "Attic":
                            try:
                                listing_data[self.FIELD_ATTIC] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_ATTIC] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_ATTIC} => {ie}")
                        case "Floor of appartment":
                            try:
                                listing_data[self.FIELD_FLOOR_NUMBER] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_FLOOR_NUMBER] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_FLOOR_NUMBER} => {ie}")
                        case "Elevator":
                            try:
                                listing_data[self.FIELD_ELEVATOR] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_ELEVATOR] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_ELEVATOR} => {ie}")
                        case "Air conditioning":
                            try:
                                listing_data[self.FIELD_AC] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_AC] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_AC} => {ie}")
                        case "Alarm":
                            try:
                                listing_data[self.FIELD_ALARM] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_ALARM] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_ALARM} => {ie}")
                        case "Access for disabled":
                            try:
                                listing_data[self.FIELD_ACCESS_DISABLED] = int(data_value_text == "Yes")
                            except Exception as ie:
                                listing_data[self.FIELD_ACCESS_DISABLED] = None
                                print(f"[ERROR] Failed to parse: {self.FIELD_ACCESS_DISABLED} => {ie}")
                        case "Type of heating":
                            listing_data[self.FIELD_HEATING_TYPE] = data_value_text if data_value_text != "Not specified" else None

                        
        except Exception as e:
            print(f"[ERROR] Failed to parse data rows => {e}")

        return listing_data
        
    def __parse_address(self, soup) -> dict:
        """
        Parse the postal code and locality from the listing.

        Args:
            soup (BeautifulSoup): Parsed HTML of the listing page.

        Returns:
            dict: Dictionary with postal code and locality.
        """
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
            print(f"[ERROR] Failed to parse: {self.FIELD_POSTAL_CODE}, {self.FIELD_LOCALITY} => {e}")
            return {}

    def __parse_pricing(self, soup) -> int | None:
        """
        Extract the property price from the listing.

        Args:
            soup (BeautifulSoup): Parsed HTML of the listing page.

        Returns:
            int | None: Price of the listing, or None if not found.
        """
        try:
            price_tag = soup.find(class_ = "detail__header_price_data")
            price_text = price_tag.text.strip().replace(" €", "").replace("\u202f", "")
            return int(price_text)
        except Exception as e:
            print(f"[ERROR] Failed to parse: {self.FIELD_PRICE} => {e}")
            return None
        
    def __get_epb_class(self, epb: int) -> str:
        """
        Returns the EPB (Energy Performance of Buildings) class based on thresholds used in Brussels.

        Args:
            epb (int): The EPB value in kWh/m²·year.

        Returns:
            str: EPB class (e.g., 'A', 'B-', 'G').
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