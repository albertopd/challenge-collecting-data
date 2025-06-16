from scraper import ImmowebScraper

try:
    scraper = ImmowebScraper()
    scraper.scrape_data()
    
except Exception as ex:
    print(f"Oops! Something went wrong! => {ex}")