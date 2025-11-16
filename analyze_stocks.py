"""Detailed analysis of stock elements."""

from bs4 import BeautifulSoup
from pathlib import Path

html_file = Path("logs/page_after_scroll.html")
if html_file.exists():
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    print("=" * 80)
    print("DETAILED STOCK ELEMENTS ANALYSIS")
    print("=" * 80)

    stock_elements = soup.find_all(class_=lambda x: x and 'stock' in x.lower() if x else False)
    print(f"\n✓ Found {len(stock_elements)} elements with 'stock' in class")

    if stock_elements:
        print("\nFirst 10 stock elements:")
        for i, elem in enumerate(stock_elements[:10], 1):
            print(f"\n--- Element {i} ---")
            print(f"Tag: {elem.name}")
            print(f"Classes: {elem.get('class')}")
            print(f"Has img: {bool(elem.find('img'))}")
            if elem.find('img'):
                img = elem.find('img')
                print(f"  - Image src: {img.get('src')}")
                print(f"  - Image alt: {img.get('alt')}")
            print(f"Text content (first 100 chars): {elem.get_text(strip=True)[:100]}")
            print(f"Has href: {bool(elem.get('href'))}")
            if elem.get('href'):
                print(f"  - href: {elem.get('href')}")

    print("\n" + "=" * 80)
    scrip_elements = soup.find_all(class_=lambda x: x and 'scrip' in x.lower() if x else False)
    print(f"\n✓ Found {len(scrip_elements)} elements with 'scrip' in class")

    if scrip_elements:
        print("\nFirst 10 scrip elements:")
        for i, elem in enumerate(scrip_elements[:10], 1):
            print(f"\n--- Element {i} ---")
            print(f"Tag: {elem.name}")
            print(f"Classes: {elem.get('class')}")
            print(f"Has img: {bool(elem.find('img'))}")
            if elem.find('img'):
                img = elem.find('img')
                print(f"  - Image src: {img.get('src')}")
                print(f"  - Image alt: {img.get('alt')}")
            print(f"Text content (first 100 chars): {elem.get_text(strip=True)[:100]}")

    print("\n" + "=" * 80)
    company_images = soup.find_all('img', alt=lambda x: x and 'Ltd' in x if x else False)
    print(f"\n✓ Found {len(company_images)} images with 'Ltd' in alt text")

    if company_images:
        print("\nFirst 20 company images:")
        for i, img in enumerate(company_images[:20], 1):
            print(f"{i}. {img.get('alt')} -> {img.get('src')}")
else:
    print("No HTML file found!")
