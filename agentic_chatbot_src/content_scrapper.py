from urllib.parse import urljoin

import requests
import os
from bs4 import BeautifulSoup

from PIL import Image
import pytesseract

from config import DATASOURCE_URL, DATASOURCE_PATH


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
    image_data = extract_images(soup, DATASOURCE_PATH)

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
    images_metadata = []
    for img in soup.find_all("img"):
        src = img.get("src")
        alt = img.get("alt", "")
        title = img.get("title", "")
        if src and src.endswith(".jpg"):  # Check if the src ends with ".jpg"
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(base_url, src)
            images_metadata.append({"src": absolute_url, "alt": alt, "title": title})

    # images_data = convert_images_to_text(images_metadata)
    return images_metadata


# Download images (optional)
# def convert_images_to_text(image_metadata):
#     extracted_text = {}
#
#     for image_data in image_metadata:
#         # Get the path of the image from the 'src' key
#         image_path = image_data['src']
#         try:
#             # Open the image using PIL
#             img = Image.open(image_path)
#             # Use Tesseract to extract text
#             text = pytesseract.image_to_string(img)
#             # Store the extracted text with the image's title as the key
#             extracted_text[image_data['title']] = text
#         except Exception as e:
#             print(f"Error reading image {image_path}: {e}")