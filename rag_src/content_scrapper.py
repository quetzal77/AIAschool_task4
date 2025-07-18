# Scrape text content from the specified web pages
from urllib.parse import urljoin

import requests
import os
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup


def scrape_web_pages(html_page, url):
    page_contents = []
    soup = BeautifulSoup(html_page, "html.parser")

    # Extract data
    text_data = extract_text(soup)
    page_contents.append(" ".join(text_data))
    table_data = extract_tables(soup)
    # image_data = extract_images(soup, url)

    # Additional metadata
    metadata = {"source_url": url}

    return text_data, table_data, metadata


# Extract all visible text
def extract_text(soup):
    # Extract visible text from <p>, <div>, <span>, and heading tags
    text_content = [element.get_text(strip=True) for element in
                    soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4'])]
    return text_content


# Extract all tables
def extract_tables(soup):
    tables = []
    for table in soup.find_all("table"):
        rows = []
        for row in table.find_all("tr"):
            cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            rows.append(cells)
        tables.append(rows)

    # for table in soup.find_all("table"):
    #     rows = []
    #     for row in table.find_all("tr"):
    #         cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
    #         rows.append(cells)
    #     df = pd.DataFrame(rows)
    #     tables.append(df)

    # for table in soup.find_all("table"):
    #     df = pd.read_html(StringIO(str(table)))[0]  # Convert HTML table to Pandas DataFrame
    #     tables.append(df)

    return tables


# Extract all images
def extract_images(soup, base_url):
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        alt = img.get("alt", "")
        title = img.get("title", "")
        if src:
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(base_url, src)
            images.append({"src": absolute_url, "alt": alt, "title": title})
    return images


# Download images (optional)
def download_images(image_data, download_folder="images"):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for i, img in enumerate(image_data):
        img_url = img["src"]
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            file_name = os.path.join(download_folder, f"image_{i + 1}.jpg")
            with open(file_name, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {file_name}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")