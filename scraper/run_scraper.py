import os
import sys
import time
import random
import logging
import os
import sys
import time
import random
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional

import httpx
import pandas as pd
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"

OUTPUTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CHECKPOINTS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / "scraper.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

TARGET_URL = "https://www.5paisa.com/stocks/all"
CHECKPOINT_FILE = CHECKPOINTS_DIR / "progress.csv"
OUTPUT_FILE = OUTPUTS_DIR / "all_stock_script_Nov15_2025.xlsx"
CHECKPOINT_INTERVAL = 50


def scroll_until_loaded(page: Page) -> None:
    """Scroll until company images stop loading or max iterations reached."""
    logger.info("Starting infinite scroll to load company images...")

    previous_height = 0
    previous_image_count = 0
    no_change_count = 0
    max_no_change = 5
    scroll_count = 0
    max_scrolls = 100

    while scroll_count < max_scrolls:
        scroll_count += 1
        try:
            current_height = page.evaluate("document.body.scrollHeight")
            current_image_count = page.evaluate(
                "() => document.querySelectorAll('img[src*=\"MarketIcons\"], img[src*=\"images.5paisa.com\"]').length"
            )

            logger.debug(f"Scroll {scroll_count}: Height={current_height}px, Company images={current_image_count}")

            if current_height == previous_height and current_image_count == previous_image_count:
                no_change_count += 1
                if no_change_count >= max_no_change:
                    logger.info(f"Reached end of page. Total company images loaded: {current_image_count}")
                    break
            else:
                no_change_count = 0
                if current_image_count > previous_image_count:
                    logger.info(f"Loading more content... (Company images: {previous_image_count} → {current_image_count})")

            previous_height = current_height
            previous_image_count = current_image_count

            page.evaluate("() => { window.scrollBy(0, window.innerHeight * 0.8); }")
            time.sleep(random.uniform(1.0, 2.0))

            if scroll_count % 10 == 0:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

            try:
                page.wait_for_load_state("networkidle", timeout=2000)
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error during scrolling at iteration {scroll_count}: {e}")
            break

    if scroll_count >= max_scrolls:
        logger.warning(f"Reached maximum scroll limit ({max_scrolls}). Proceeding with extraction...")


def extract_stock_data(page: Page) -> List[Dict]:
    """Extract company names and logo URLs from the loaded page HTML."""
    logger.info("Extracting stock data from page...")
    html_content = page.content()
    soup = BeautifulSoup(html_content, 'html.parser')
    stock_data: List[Dict] = []

    all_images = soup.find_all('img')
    for img in all_images:
        alt_text = img.get('alt', '')
        src = img.get('src', '')
        if not alt_text or len(alt_text) < 4:
            continue
        if any(skip in alt_text.lower() for skip in ['home', 'banner', 'arrow', 'icon', '5paisa']):
            continue
        if 'menu' in src.lower() or 'banner' in src.lower() or 'hamburger' in src.lower():
            continue
        if 'MarketIcons' in src or 'images.5paisa.com' in src or 'storage.googleapis.com' in src:
            logo_url = src
            if not logo_url.startswith('http'):
                if logo_url.startswith('//'):
                    logo_url = 'https:' + logo_url
                elif logo_url.startswith('/'):
                    logo_url = 'https://www.5paisa.com' + logo_url
            stock_data.append({'serial_no': len(stock_data) + 1, 'company_name': alt_text.strip(), 'logo_url': logo_url, 'notes': ''})

    if stock_data:
        logger.info(f"Found {len(stock_data)} company logos via direct image extraction")
        return stock_data

    debug_file = LOGS_DIR / "page_html_debug.html"
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.error(f"No stock elements found. HTML saved to {debug_file} for debugging")
    return []


def normalize_company_name(name: str) -> str:
    normalized = name.lower()
    normalized = ' '.join(normalized.split())
    normalized = re.sub(r'[^a-z0-9\\s]', '', normalized)
    return normalized


def validate_logo(url: str) -> str:
    try:
        with httpx.Client(timeout=10.0) as client:
            try:
                response = client.head(url, follow_redirects=True)
            except Exception:
                response = client.get(url, follow_redirects=True)
            status_code = response.status_code
            content_type = response.headers.get('content-type', '').lower()
        if status_code == 200 and 'image' in content_type:
            return "Valid"
        return f"Invalid (Status: {status_code}, Type: {content_type})"
    except Exception as e:
        logger.debug(f"Logo validation failed for {url}: {e}")
        return "Broken or Missing"


def save_checkpoint(data: List[Dict]) -> None:
    try:
        pd.DataFrame(data).to_csv(CHECKPOINT_FILE, index=False, encoding='utf-8')
        logger.info(f"Checkpoint saved: {len(data)} records in {CHECKPOINT_FILE}")
    except Exception as e:
        logger.error(f"Failed to save checkpoint: {e}")


def resume_from_checkpoint() -> Optional[List[Dict]]:
    if CHECKPOINT_FILE.exists():
        try:
            df = pd.read_csv(CHECKPOINT_FILE, encoding='utf-8')
            data = df.to_dict('records')
            logger.info(f"Resumed from checkpoint: {len(data)} records loaded")
            return data
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None
    logger.info("No checkpoint found. Starting fresh scraping...")
    return None


def save_to_excel(data: List[Dict]) -> None:
    try:
        df = pd.DataFrame(data)
        df = df[['serial_no', 'company_name', 'logo_url', 'notes']]
        df.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
        logger.info(f"✅ Data successfully saved to: {OUTPUT_FILE}")
        logger.info(f"Total records in Excel: {len(df)}")
    except Exception as e:
        logger.error(f"Failed to save Excel file: {e}")
        raise


def run_scraper() -> None:
    start_time = time.time()
    logger.info("=" * 80)
    logger.info("🚀 5Paisa Stocks Scraper Started")
    logger.info("=" * 80)
    logger.info(f"Target URL: {TARGET_URL}")
    logger.info(f"Output will be saved to: {OUTPUT_FILE}")

    existing_data = resume_from_checkpoint()
    all_stock_data = existing_data if existing_data else []

    try:
        with sync_playwright() as p:
            logger.info("Launching browser (with stealth features)...")
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage"])
            realistic_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            context = browser.new_context(user_agent=realistic_ua, viewport={'width': 1920, 'height': 1080}, locale='en-US', timezone_id='Asia/Kolkata')
            page = context.new_page()
            try:
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
            except Exception:
                pass
            page.set_default_timeout(60000)

            logger.info(f"Navigating to {TARGET_URL}...")
            logger.info("⚠️  A browser window will open. Please wait for the scraping to complete.")
            logger.info("⚠️  Do not close the browser manually!")
            try:
                page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)
            except Exception as e:
                logger.error(f"Failed to navigate to page: {e}")
                browser.close()
                return

            try:
                title = page.title()
                logger.info(f"Page loaded: {title}")
                if "Access Denied" in title or "access denied" in page.content().lower()[:500]:
                    logger.error("❌ Access denied by website. The site is blocking automated access.")
                    browser.close()
                    return
            except Exception:
                pass

            try:
                screenshot_path = LOGS_DIR / "page_screenshot.png"
                page.screenshot(path=str(screenshot_path), full_page=False)
                logger.info(f"Screenshot saved to: {screenshot_path}")
            except Exception:
                pass

            scroll_until_loaded(page)
            try:
                html_debug_path = LOGS_DIR / "page_after_scroll.html"
                with open(html_debug_path, 'w', encoding='utf-8') as f:
                    f.write(page.content())
                logger.info(f"Page HTML saved to: {html_debug_path}")
            except Exception:
                pass

            stock_data = extract_stock_data(page)
            try:
                page.close(); context.close(); browser.close()
                logger.info("Browser closed.")
            except Exception:
                pass

        if not stock_data:
            logger.error("❌ No stock data extracted. Please check the page structure.")
            return

        logger.info("Cleaning data and removing duplicates...")
        seen_names = set(); unique_data: List[Dict] = []; duplicates_count = 0
        for record in stock_data:
            normalized_name = normalize_company_name(record['company_name'])
            if normalized_name not in seen_names:
                seen_names.add(normalized_name); unique_data.append(record)
            else:
                duplicates_count += 1

        logger.info(f"Removed {duplicates_count} duplicate entries")
        logger.info(f"Unique companies: {len(unique_data)}")

        for idx, record in enumerate(unique_data, start=1):
            record['serial_no'] = idx

        logger.info("Validating logo URLs...")
        invalid_count = 0
        for idx, record in enumerate(unique_data):
            if (idx + 1) % 10 == 0:
                logger.info(f"Validated {idx + 1}/{len(unique_data)} logos...")
            validation_result = validate_logo(record['logo_url'])
            record['notes'] = validation_result
            if validation_result != "Valid":
                invalid_count += 1
            time.sleep(random.uniform(0.1, 0.3))
            if (idx + 1) % CHECKPOINT_INTERVAL == 0:
                save_checkpoint(unique_data[:idx + 1])

        logger.info(f"Logo validation complete. Invalid/broken logos: {invalid_count}")
        logger.info("Saving final data to Excel...")
        save_to_excel(unique_data)

        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink(); logger.info("Checkpoint file removed (scraping complete)")

        elapsed_time = time.time() - start_time
        logger.info("=" * 80)
        logger.info("✅ SCRAPING COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"📊 Total companies scraped: {len(unique_data)}")
        logger.info(f"🔄 Duplicates removed: {duplicates_count}")
        logger.info(f"❌ Invalid logos: {invalid_count}")
        logger.info(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
        logger.info(f"📁 Output file: {OUTPUT_FILE}")
        logger.info(f"📝 Log file: {LOG_FILE}")
        logger.info("=" * 80)

        logger.info(f"📂 Opening Excel file: {OUTPUT_FILE}")
        try:
            import subprocess, platform
            if platform.system() == 'Windows':
                os.startfile(str(OUTPUT_FILE))
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(OUTPUT_FILE)])
            else:
                subprocess.run(['xdg-open', str(OUTPUT_FILE)])
            logger.info("✅ Excel file opened successfully! You can now view the scraped data.")
        except Exception as e:
            logger.warning(f"Could not automatically open Excel file: {e}")
            logger.info(f"Please manually open: {OUTPUT_FILE}")

    except KeyboardInterrupt:
        logger.warning("⚠️  Scraping interrupted by user. Progress saved to checkpoint.")
        if 'unique_data' in locals():
            save_checkpoint(unique_data)
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error during scraping: {e}", exc_info=True)
        if 'unique_data' in locals():
            save_checkpoint(unique_data)
        sys.exit(1)


if __name__ == "__main__":
    run_scraper()
