# 5Paisa Stocks Scraper

> 🎯 Official Project for **DSC Winter of Code 2026**

A Python-based web scraper built using **Playwright** that automatically extracts all company names and logo URLs from the 5Paisa Stocks page. This project handles dynamic content loading via infinite scroll, validates logo URLs, removes duplicates, and exports clean data to Excel.

> **⚠️ IMPORTANT:** The scraper opens a visible browser window (non-headless mode) to bypass anti-bot protection. **Do not close the browser window manually!** Let the script complete and it will close automatically. The scraping process may take 2-5 minutes depending on the number of stocks.

---

## 📋 Features

- ✅ **Automated Infinite Scrolling** – Dynamically loads all stock data by scrolling until no more content appears
- ✅ **Company Name & Logo Extraction** – Parses HTML to extract company names and logo image URLs
- ✅ **Logo URL Validation** – Validates each logo URL using HTTP HEAD/GET requests
- ✅ **Duplicate Removal** – Normalizes company names and removes duplicate entries
- ✅ **Resume from Checkpoint** – Automatically resumes scraping from the last saved checkpoint if interrupted
- ✅ **Excel Export** – Saves final data to a well-formatted Excel file with serial numbers
- ✅ **Comprehensive Logging** – Tracks progress, errors, and statistics in a detailed log file
- ✅ **Polite Scraping** – Implements random delays and custom user-agent to avoid overwhelming the server

---

## 📂 Project Structure

```
5paisa_stocks_scraper/
│
├── scraper/
│   └── run_scraper.py             # Main Playwright scraper script
│
├── outputs/
│   └── all_stock_script_Nov15_2025.xlsx   # Final Excel output file
│
├── logs/
│   └── scraper.log                # Log file for progress and errors
│
├── checkpoints/
│   └── progress.csv               # For resumable scraping (created during run)
│
├── README.md                      # This documentation file
└── requirements.txt               # Python dependencies
```

---

## ⚙️ Technology Stack

- **Python 3.10+**
- **Playwright** – Browser automation for dynamic content
- **BeautifulSoup4** – HTML parsing
- **httpx** – Async HTTP client for logo validation
- **pandas** – Data manipulation
- **openpyxl** – Excel file generation

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher installed on your system
- Internet connection for scraping

### Step 1: Clone or Download the Project
Download the project folder or clone it to your local machine.

### Step 2: Navigate to Project Directory
```powershell
cd c:\Users\Mashr\Desktop\5paisa_stocks_scraper
```

### Step 3: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers
Playwright requires browser binaries to be installed:
```powershell
playwright install chromium
```

---

## 🎯 Usage

### Running the Scraper

To start scraping all stock data from 5Paisa:

```powershell
python scraper/run_scraper.py
```

### What Happens During Execution:

1.  **Browser Launch** – Opens Chromium browser in visible (non-headless) mode
2. **Navigate to Page** – Loads https://www.5paisa.com/stocks/all
3. **Infinite Scroll** – Scrolls down repeatedly until all stocks are loaded
4. **Data Extraction** – Parses HTML and extracts company names and logo URLs
5. **Data Cleaning** – Removes duplicates based on normalized company names
6. **Logo Validation** – Checks each logo URL for validity (HTTP status and content-type)
7. **Save to Excel** – Exports final data to `outputs/all_stock_script_Nov15_2025.xlsx`
8. **Logging** – Records all activity to `logs/scraper.log`

---

## 🔄 Resume After Interruption

If the scraper is interrupted (e.g., network issue, manual stop), it automatically saves progress to:
```
checkpoints/progress.csv
```

When you run the scraper again, it will:
- Detect the checkpoint file
- Resume from where it left off
- Skip re-scraping already collected data

To force a fresh start, simply delete `checkpoints/progress.csv` before running.

---

## 🔍 Logo Validation Logic

For each logo URL, the scraper:
1. Sends an HTTP **HEAD** request (faster, no content download)
2. Falls back to **GET** request if HEAD fails
3. Checks:
   - Status code is **200** (OK)
   - Content-Type header contains **"image"**
4. Marks logo as:
   - ✅ **"Valid"** – Logo accessible and is an image
   - ❌ **"Broken or Missing"** – Logo inaccessible or not an image
   - ⚠️ **"Invalid (Status: XXX)"** – Other HTTP errors

The validation status is saved in the **"notes"** column in the Excel output.

---

## 📊 Output Format

The Excel file (`outputs/all_stock_script_Nov15_2025.xlsx`) contains:

| serial_no | company_name       | logo_url                          | notes  |
|-----------|--------------------|-----------------------------------|--------|
| 1         | Reliance Industries| https://example.com/logo1.png    | Valid  |
| 2         | TCS Limited        | https://example.com/logo2.png    | Valid  |
| 3         | HDFC Bank          | https://example.com/logo3.png    | Broken or Missing |

---

## 📝 Logging

All scraping activity is logged to:
```
logs/scraper.log
```

The log file includes:
- Start and end timestamps
- Total companies scraped
- Number of duplicates removed
- Number of invalid logos
- Total execution time
- Any errors or warnings

---

## ⚠️ **Known Limitations**

1. **Limited Stock Listings on Page** – The 5Paisa "All Stocks" page (https://www.5paisa.com/stocks/all) only displays a limited sample of companies (~30-40) on initial load, not all listed companies as the title suggests. The website may require using search functionality, filters, or accessing different pages to view all stocks. The scraper extracts all visible companies from the page.

2. **Anti-Bot Protection** – The 5Paisa website uses anti-bot protection that may block automated access. The scraper runs in non-headless mode (visible browser) to help bypass this. **Do not close the browser window manually during scraping.**

3. **Manual Intervention May Be Required** – If the website shows a CAPTCHA or "Access Denied" message, you may need to:
   - Complete the CAPTCHA manually in the browser window that opens
   - Wait a few minutes and try again
   - Use a VPN if your IP has been temporarily blocked

4. **Website Structure Changes** – If 5Paisa updates their HTML structure, the CSS selectors may need adjustment

5. **Rate Limiting** – Excessive requests may trigger rate limiting; scraper includes polite delays to minimize risk

6. **Dynamic Content** – Some stocks may load asynchronously; the scraper waits for network idle but rare edge cases may occur

7. **Logo Validation Speed** – Validating hundreds/thousands of URLs takes time; expect 1-3 seconds per logo

---

## 🛠️ Troubleshooting

### Error: "playwright not found"
**Solution:** Run `playwright install chromium`

### Error: "No module named 'openpyxl'"
**Solution:** Run `pip install -r requirements.txt`

### No data extracted
**Solution:** The website structure may have changed. Check `logs/scraper.log` for details. You may need to update CSS selectors in `extract_stock_data()` function.

### Scraper stuck during scrolling
**Solution:** Check your internet connection. The scraper will timeout after 60 seconds on page load.

## 🤝 Contributing

We welcome contributions from the community, especially participants of **DSC Winter of Code 2026**.

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for:
- Setup instructions
- Beginner-friendly issues
- Pull request guidelines
- Code of conduct


## ⚠️ Disclaimer

This project is intended for **educational purposes only**.  
Users are responsible for ensuring compliance with the website’s terms of service before scraping any data.


## 📜 License

This project is created for educational and internship evaluation purposes.

---

## 🙏 Acknowledgments

- **5Paisa** for providing publicly accessible stock data
- **Playwright** team for excellent browser automation tools
- **Python community** for amazing open-source libraries

---

## 📞 Support

For issues, questions, or suggestions, please contact via LinkedIn or GitHub.

---


