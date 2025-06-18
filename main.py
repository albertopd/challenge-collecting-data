from wakepy import keep
from scraper import Scraper

try:
    scraper = Scraper()

    with keep.running():
        scraper.scrape_data("listings_data.csv", "listings_urls.txt", 36000)
    
except Exception as ex:
    print(f"Oops! Something went wrong! => {ex}")