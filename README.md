# Immoweb scraper

A web scraper that gets real estate information from the company Immoweb.

---

## 📦 Installation

1. **Clone the repository**  
   ```bash
   git clone git@github.com:albertopd/challenge-collecting-data.git
   cd wikipedia-scraper
   ```

2. **(Optional) Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

---

## 🧠 Features

- Retrieves real-time country and leader data from a public API.
- Handles cookie expiration and retries automatically.
- Scrapes the **first paragraph** of each leader’s Wikipedia page.
- Outputs a well-structured JSON file.

---

## 📄 Requirements

- Python 3.10+
- Requests
- BeautifulSoup4
- lxml (for faster HTML parsing)

See [requirements.txt](requirements.txt) for the full list.

## 👤 Author

**Alberto Pérez Dávila**  
GitHub: [@albertopd](https://github.com/albertopd)