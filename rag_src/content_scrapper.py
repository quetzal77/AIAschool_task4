from urllib.parse import urljoin

import requests
import os
from bs4 import BeautifulSoup

from config import DATASOURCE_URL

# Scrape text content from the specified web pages
def scrape_web_pages(html_page):
    table_headers = []
    table_rows = []
    page_contents = []
    soup = BeautifulSoup(html_page, "html.parser")

    # Extract data
    text_data = extract_text(soup)
    page_contents.append(" ".join(text_data))
    table_data = extract_tables(soup)

    # Process table data
    for table_index, table in enumerate(table_data):
        # Separate headers and rows
        headers, rows = _separate_headers_and_rows(table)
        table_headers.append(headers)  # Collect headers for this table
        table_rows.append(rows)  # Collect rows for this table

    # Process image data
    # image_data = extract_images(soup, DATASOURCE_URL)

    # Additional metadata
    metadata = {
        "source_url": DATASOURCE_URL,
        "table_size": len(table_data)  # Add size of table_data array
    }

    return text_data, table_headers, table_rows, metadata


# Extract all visible text
def extract_text(soup):
    # Extract visible text from <p>, <div>, <span>, and heading tags
    text_content = [element.get_text(strip=True) for element in
                    soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4'])]
    text_content = text_content[451:511] # this is filter to remove garbage and leave only important text information
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
    return tables

def filter_rows(table):
    """
    Filters rows in the table:
    1. Removes empty rows.
    2. Keeps rows where the first cell is empty but the row has more than one element.
    """
    filtered_rows = []
    for row in table:
        if not row or all(cell.strip() == "" for cell in row):
            continue  # Skip completely empty rows
        if row[0].strip() == "" and len(row) > 1:  # Keep rows with empty first cell but multiple elements
            filtered_rows.append(row)
        elif any(cell.strip() != "" for cell in row):  # Keep rows with at least one non-empty cell
            filtered_rows.append(row)
    return filtered_rows

def _separate_headers_and_rows(table):
    # Separates header rows (rows with a single element) from table data rows.
    headers = []
    rows = []

    for row in table:
        if len(row) == 1:  # Identify header rows
            headers.append(row[0])  # Collect the single element as a header
        elif len(row) > 1:  # Identify table data rows
            rows.append(row)

    #     Filters rows in the table:
    #     1. Removes empty rows.
    #     2. Keeps rows where the first cell is empty but the row has more than one element.
    rows = filter_rows(rows)
    return headers, rows

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