from scraper import Scraper

try:
    scraper = Scraper()
    scraper.scrape_data()
    
except Exception as ex:
    print(f"Oops! Something went wrong! => {ex}")