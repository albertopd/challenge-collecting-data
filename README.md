# 🏠 Real Estate Scraper for Immovlan

This Python project is a web scraper for extracting property listings from [Immovlan.be](https://www.immovlan.be/en/). It collects detailed real estate information and stores the data into a CSV file.

---

## 📦 Features

- Fetches listings for apartments, houses, villas, etc.
- Parses detailed attributes including price, area, EPB class, number of rooms, and more.
- Generates realistic HTTP headers to avoid being blocked.
- Automatically resumes from a previously saved URL.
- Caches listing URLs to reduce unnecessary requests.
- Writes clean structured output in CSV format.

---

## 🚀 Usage

### 1. Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Run the scraper:

```bash
python scraper.py
```

Or from another script using:

```python
from scraper import Scraper

scraper = Scraper()
scraper.scrape_data("listings_data.csv", "listings_urls.txt", 36000)
```

---

## 📂 Output

- **CSV File** (`listings_data.csv`): Contains listings with fields like type, price, surface, location, energy rating, etc.
- **URL Cache** (`listings_urls.txt`): A list of previously collected listing URLs.

---

## 🧠 Class and Methods Overview

### `class Scraper`

A web scraper for collecting real estate listings.

#### `scrape_data(output_csv_file, urls_txt_file, max_urls, start_from_url="")`

Main entry point to scrape and store listings.

#### `__get_headers()`

Generates randomized HTTP headers for anti-bot protection.

#### `__get_listing_urls(urls_txt_file, max_urls)`

Retrieves listing URLs from file or online source.

#### `__save_urls_to_file(urls, filename)`

Saves retrieved URLs for future reuse.

#### `__load_urls_from_file(filename)`

Loads cached URLs if available.

#### `__get_listing_data(listing_url)`

Scrapes and parses a single listing.

#### `__parse_listing_type(soup)`

Gets the type of the property (e.g., apartment, house).

#### `__parse_data_rows(soup)`

Extracts key-value property attributes (e.g., bedrooms, surface).

#### `__parse_address(soup)`

Parses postal code and locality.

#### `__parse_pricing(soup)`

Extracts listing price.

#### `__get_epb_class(epb)`

Converts EPB score to energy class (A++ to G).

---

## 📌 Notes

- Target site: [https://www.immovlan.be/en/](https://www.immovlan.be/en/)
- EPB classification is based on Brussels-Capital Region standards.
- Scraper includes delay between requests to avoid IP blocking.

---

## 📜 License

This project is intended for educational and non-commercial use only.

---

## 📄 Requirements

- Python 3.10+
- Requests
- BeautifulSoup4
- lxml (for faster HTML parsing)

See [requirements.txt](requirements.txt) for the full list.

---

## 👤 Author

**Alberto Pérez Dávila**  
GitHub: [@albertopd](https://github.com/albertopd)