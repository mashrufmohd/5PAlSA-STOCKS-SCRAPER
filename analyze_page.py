"""Quick script to analyze the page structure."""

from bs4 import BeautifulSoup
from pathlib import Path

html_file = Path("logs/page_after_scroll.html")
if not html_file.exists():
    html_file = Path("logs/page_html_debug.html")

if html_file.exists():
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    print("=" * 80)
    print(f"PAGE ANALYSIS - {html_file.name}")
    print("=" * 80)

    stock_links = soup.select('a[href*="/stock/"]')
    print(f"\n✓ Links containing '/stock/': {len(stock_links)}")
    if stock_links:
        print("  First 5 hrefs:")
        for link in stock_links[:5]:
            print(f"    - {link.get('href')}")

    all_images = soup.find_all('img')
    print(f"\n✓ Total <img> tags: {len(all_images)}")
    if all_images:
        print("  First 5 img sources:")
        for img in all_images[:5]:
            print(f"    - {img.get('src', 'NO SRC')} | alt: {img.get('alt', 'NO ALT')}")

    print("\n✓ Checking common class patterns:")
    for pattern in ['stock', 'company', 'scrip', 'card', 'item', 'list']:
        elements = soup.find_all(class_=lambda x: x and pattern in x.lower() if x else False)
        if elements:
            print(f"  - Elements with '{pattern}' in class: {len(elements)}")
            if len(elements) <= 3:
                for elem in elements[:3]:
                    print(f"    {elem.name}: {elem.get('class')}")

    print("\n✓ List structures:")
    print(f"  - <ul> tags: {len(soup.find_all('ul'))}")
    print(f"  - <ol> tags: {len(soup.find_all('ol'))}")
    print(f"  - <li> tags: {len(soup.find_all('li'))}")
    print(f"  - <div> tags: {len(soup.find_all('div'))}")

    print("\n✓ First 2000 characters of body:")
    body = soup.find('body')
    if body:
        print(body.get_text()[:2000])

    print("\n" + "=" * 80)
else:
    print("❌ No debug HTML file found. Run the scraper first.")
