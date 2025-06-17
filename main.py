from scraper import ImmowebScraper

try:
    scraper = ImmowebScraper()
    scraper.scrape_data()
    scraper.save_data("immoweb_data.csv")
    
except Exception as ex:
    print(f"Oops! Something went wrong! => {ex}")