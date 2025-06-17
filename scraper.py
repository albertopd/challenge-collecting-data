import re
import time

from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By

class ImmowebScraper:
    ZIMMO_URL = "https://www.zimmo.be"
    LISTINGS_URL = "/fr/rechercher/?search=eyJmaWx0ZXIiOnsic3RhdHVzIjp7ImluIjpbIkZPUl9TQUxFIiwiVEFLRV9PVkVSIl19LCJjYXRlZ29yeSI6eyJpbiI6WyJIT1VTRSIsIkFQQVJUTUVOVCJdfX0sInBhZ2luZyI6eyJmcm9tIjowLCJzaXplIjoxN30sInNvcnRpbmciOlt7InR5cGUiOiJQT1NUQUxfQ09ERSIsIm9yZGVyIjoiQVNDIn1dfQ%3D%3D&p={}"
    
    # Listing attribute names
    LISTING_LOCALITY = "Locality"
    LISTING_TYPE = "Type of property"
    LISTING_SUBTYPE = "Subtype of property"
    LISTING_SALE_TYPE = "Type of sale"
    LISTING_PRICE: str = "Price"
    LISTING_BEDROOMS = "Number of bedrooms"
    LISTING_BATHROOMS = "Number of bathrooms"
    LISTING_LIVING_AREA = "Living area"
    LISTING_FULL_KITCHEN = "Fully equipped kitchen" # 1/0
    LISTING_FURNISHED = "Furnished" # 1/0
    LISTING_OPEN_FIRE = "Open fire" # 1/0
    LISTING_TERRACE = "Terrace"  # 1/0
    LISTING_TERRACE_AREA = "Terrace area"
    LISTING_GARDEN = "Garden" # 1/0
    LISTING_GARDEN = "Garden area"
    LISTING_SURFACE_LAND = "Surface of the land"
    LISTING_SURFACE_PLOT_LAND =  "Surface area of the plot of land"
    LISTING_NUMBER_FACADES = "Number of facades"
    LISTING_SWIMMING_POOL = "Swimming pool" # 1/0
    LISTING_STATE = "State of the building" # New, to be renovated, ...

    # Compiled regex patterns
    PATTERN_BEDROOMS = re.compile(r"(\d?) bedroom")
    PATTERN_BATHROOMS = re.compile(r"(\d?) bathroom")
    PATTERN_LIVABLE_SPACE = re.compile(r"(\d?) livable space")

    def __init__(self) -> None:
        self.data: list[dict] = []

    def scrape_data(self) -> None:
        page = 0
        there_are_listings = True

        while page < 1: #there_are_listings:
            page += 1
            print(f"Getting listings from page {page}")

            listings_page_url = urljoin(self.ZIMMO_URL, self.LISTINGS_URL.format(page))
            listings_urls = self.__get_listings_urls(listings_page_url)
            there_are_listings = len(listings_urls) > 0

            print(f"Found {len(listings_urls)} listings")

            for listing_url in listings_urls:
                listing_data = self.__get_listing_data(listing_url)

                if listing_data:
                    self.data.append(listing_data)

    def save_data(self, filename: str) -> None:
        print(self.data)

    def __open_page_in_selenium(self, page_url: str):
        driver = webdriver.Chrome()
        driver.get(page_url)

        # Accept cookies
        time.sleep(1) # Wait 1 sec for the cookie pop-up to show
        cookie_button = driver.find_element(By.ID ,"didomi-notice-agree-button")
        if cookie_button:
            cookie_button.click()

        return driver

    def __get_listings_urls(self, listings_page_url: str) -> list[str]:
        listings_urls: list[str] = []

        try:
            driver = self.__open_page_in_selenium(listings_page_url)
            links = driver.find_elements(By.CLASS_NAME, "property-item_link")

            print(f"Number of listings found: {len(links)}")
            
            for link in links:
                href = link.get_attribute("href")
                if href:
                    listings_urls.append(urljoin(self.ZIMMO_URL, href))
        except Exception as e:
            print(f"Failed to get listings from page: {listings_page_url} => {e}")
        finally:
            if driver:
                driver.close()

        return listings_urls
    
    def __get_listing_data(self, listing_url: str) -> dict:
        try:
            driver = self.__open_page_in_selenium(listing_url)
            print(driver.title)

            listing_data = {}
            listing_data["URL"] = listing_url
            listing_data[self.LISTING_LOCALITY] = self.__get_locality()
            listing_data[self.LISTING_TYPE] = self.__get_property_type()
            listing_data[self.LISTING_SUBTYPE] = self.__get_property_subtype()
            listing_data[self.LISTING_SALE_TYPE] = self.__get_sale_type()
            listing_data[self.LISTING_PRICE] = self.__get_pricing(driver)

            return listing_data     
        except Exception as e:
            print(f"Failed to get listing data from page: {listing_url} => {e}")
            return {}
        finally:
            if driver:
                driver.close()
    
    def __get_locality(self) -> str | None:
        try:
            return ""
        except:
            return None
        
    def __get_property_type(self) -> str | None:
        try:
            return ""
        except:
            return None
        
    def __get_property_subtype(self) -> str | None:
        try:
            return ""
        except:
            return None   
        
    def __get_sale_type(self) -> str | None:
        try:
            return ""
        except:
            return None
        
    def __get_pricing(self, driver) -> float | None:
        try:
            price_tag = driver.find_element(By.CLASS_NAME, "price-value")
            price_text = price_tag.text.strip().replace("€ ", "").replace('.', "")
            return int(price_text)
        except:
            return None
        
    def get_rooms(self) -> int | None:
        try:
            return 0
        except:
            return None
        
    def get_living_area(self) -> int | None:
        try:
            return 0
        except:
            return None