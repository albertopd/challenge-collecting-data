from scraper import Scraper

try:
    scraper = Scraper()
    scraper.scrape_data()
    scraper.save_data("immoweb_data.csv")
    
except Exception as ex:
    print(f"Oops! Something went wrong! => {ex}")