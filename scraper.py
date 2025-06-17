import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By

class ImmowebScraper:
    # URLs file
    URLS_FILE = "urls.txt"

    ZIMMO_URL = "https://www.zimmo.be"
    LISTINGS_URL = "/fr/rechercher/?search=eyJmaWx0ZXIiOnsic3RhdHVzIjp7ImluIjpbIkZPUl9TQUxFIiwiVEFLRV9PVkVSIl19LCJjYXRlZ29yeSI6eyJpbiI6WyJIT1VTRSIsIkFQQVJUTUVOVCJdfX0sInBhZ2luZyI6eyJmcm9tIjowLCJzaXplIjoxN30sInNvcnRpbmciOlt7InR5cGUiOiJQT1NUQUxfQ09ERSIsIm9yZGVyIjoiQVNDIn1dfQ%3D%3D&p={}"
    
    # Listing attribute names
    LISTING_LOCALITY = "Locality"
    LISTING_POSTAL_CODE = "Postal Code"
    LISTING_TYPE = "Type of property"
    LISTING_PRICE: str = "Price"
    LISTING_BEDROOMS = "Number of bedrooms"
    LISTING_BATHROOMS = "Number of bathrooms"
    LISTING_LIVING_AREA = "Living area"
    LISTING_CONSTRUCTION_YEAR = "Construction year"
    LISTING_NUMBER_FACADES = "Number of facades"
    LISTING_EPB = "EPB (kWh/m²)"
    LISTING_ENERGY_CLASS = "Energy class"

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
        """
        for listing_url in all_listing_urls:
            listing_data = self.__get_listing_data(listing_url)

            if listing_data:
                self.data.append(listing_data)
        """

    def save_data(self, filename: str) -> None:
        print(self.data)

    def __open_page_in_selenium(self, page_url: str):
        driver = webdriver.Chrome()
        driver.get(page_url)
        """
        # Accept cookies
        time.sleep(1) # Wait 1 sec for the cookie pop-up to show
        cookie_button = driver.find_element(By.ID ,"didomi-notice-agree-button")
        if cookie_button:
            cookie_button.click()
        """
        return driver

    def __get_all_listing_urls(self) -> list[str]:
        # Try to load URLs from previous file
        all_listing_urls = self.__load_urls_from_file(self.URLS_FILE)

        if len(all_listing_urls) == 0:
            page = 0
            there_are_listings = True

            while there_are_listings:
                page += 1
                print(f">> Getting listings URLs from page {page}")

                listings_page_url = urljoin(self.ZIMMO_URL, self.LISTINGS_URL.format(page))
                listings_urls_per_page = self.__get_listings_urls_per_page(listings_page_url)
                there_are_listings = len(listings_urls_per_page) > 0

                print(f"Found {len(listings_urls_per_page)} listings")
                all_listing_urls.extend(listings_urls_per_page) 
            
            if len(all_listing_urls) > 0:
                self.__save_urls_to_file(all_listing_urls, self.URLS_FILE)

        return all_listing_urls

    def __save_urls_to_file(self, urls: list[str], file_path: str) -> None:
        try:
            with open(file_path, 'w') as urls_file:
                urls_file.writelines(url + '\n' for url in urls)
        except Exception as e:
            print(f"[ERROR] Failed to save URLs to file: {file_path} => {e}")

    def __load_urls_from_file(self, file_path: str) -> list[str]:
        try:
            with open(file_path, 'r') as urls_file:
                return urls_file.readlines()
        except Exception as e:
            print(f"[ERROR] Failed to load URLs from file: {file_path} => {e}")
            return []

    def __get_listings_urls_per_page(self, listings_page_url: str) -> list[str]:
        listings_urls: list[str] = []

        try:
            driver = webdriver.Chrome()
            driver.get(listings_page_url)

            for _ in range(3):
                links = driver.find_elements(By.CLASS_NAME, "property-item_link")
                if len(links) > 0:
                    break
                time.sleep(1)

            print(f"Number of listings found: {len(links)}")
            
            for link in links:
                href = link.get_attribute("href")
                if href:
                    listings_urls.append(urljoin(self.ZIMMO_URL, href))
        except Exception as e:
            print(f"[ERROR] Failed to get listings from page: {listings_page_url} => {e}")
        finally:
            if driver:
                driver.close()

        return listings_urls
    
    def __get_listing_data(self, listing_url: str) -> dict:
        try:
            print(f">>>> Scraping listing data from page => {listing_url}")

            #driver = self.__open_page_in_selenium(listing_url)
            driver = webdriver.Chrome()
            driver.get(listing_url)

            listing_data = self.__parse_main_features(driver)
            listing_data.update(self.__parse_address(driver))
            listing_data[self.LISTING_PRICE] = self.__parse_pricing(driver)
            listing_data["URL"] = listing_url

            return listing_data     
        except Exception as e:
            print(f"[ERROR] Failed to parse listing data from page: {listing_url} => {e}")
            return {}
        finally:
            if driver:
                driver.close()

    def __parse_main_features(self, driver) -> dict:
        listing_data = {}

        try:
            main_features_ul = driver.find_element(By.CLASS_NAME, "main-features")
            items = main_features_ul.find_elements(By.TAG_NAME, "li")

            for item in items:
                feature_label = item.find_element(By.CLASS_NAME, "feature-label").text.strip()
                feature_value = item.find_element(By.CLASS_NAME, "feature-value").text.strip()
                match feature_label:
                    case "Type":
                        listing_data[self.LISTING_TYPE] = feature_value
                    case "Surf. habitable":
                        try:
                            listing_data[self.LISTING_LIVING_AREA] = int(feature_value.replace(" m²", ""))
                        except Exception as ie:
                            listing_data[self.LISTING_LIVING_AREA] = None
                            print(f"[ERROR] Failed to parse living area => {ie}")
                    case "Chambres":
                        try:
                            listing_data[self.LISTING_BEDROOMS] = int(feature_value)
                        except Exception as ie:
                            listing_data[self.LISTING_BEDROOMS] = None
                            print(f"[ERROR] Failed to parse number of bedrooms => {ie}")
                    case "Salles de bain":
                        try:
                            listing_data[self.LISTING_BATHROOMS] = int(feature_value)
                        except Exception as ie:
                            listing_data[self.LISTING_BATHROOMS] = None
                            print(f"[ERROR] Failed to parse number of bathrooms => {ie}")
                    case "Construit en":
                        try:
                            listing_data[self.LISTING_CONSTRUCTION_YEAR] = int(feature_value)
                        except Exception as ie:
                            listing_data[self.LISTING_CONSTRUCTION_YEAR] = None
                            print(f"[ERROR] Failed to parse construction year => {ie}")
                    case "Construction":
                        try:
                            listing_data[self.LISTING_NUMBER_FACADES] = int(feature_value.replace("-façades", ""))
                        except Exception as ie:
                            listing_data[self.LISTING_NUMBER_FACADES] = None
                            print(f"[ERROR] Failed to parse number of facades => {ie}")
                    case "PEB":
                        try:
                            listing_data[self.LISTING_EPB] = int(feature_value.replace(" kWh/m²", ""))
                            listing_data[self.LISTING_ENERGY_CLASS] = self.__get_epb_class(listing_data[self.LISTING_EPB])
                        except Exception as ie:
                            listing_data[self.LISTING_EPB] = None
                            print(f"[ERROR] Failed to parse EPB => {ie}")   
                        
        except Exception as e:
            print(f"[ERROR] Failed to parse main features => {e}")

        return listing_data
    
    def __parse_address(self, driver) -> dict:
        try:
            try:
                address_element = driver.find_element(By.CLASS_NAME, "__full-address")
            except:
                address_element = driver.find_element(By.CLASS_NAME, "address-not-fully-available")

            address_parts = address_element.text.strip().split(',')[-1].strip().split(' ')

            return {
                self.LISTING_POSTAL_CODE: int(address_parts[0]),
                self.LISTING_LOCALITY: address_parts[1]
            }
        except Exception as e:
            print(f"[ERROR] Failed to parse address => {e}")
            return {}

    def __parse_pricing(self, driver) -> float | None:
        try:
            price_tag = driver.find_element(By.CLASS_NAME, "price-value")
            price_text = price_tag.text.strip().replace("€ ", "").replace('.', "")
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