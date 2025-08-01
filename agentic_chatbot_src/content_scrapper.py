from urllib.parse import urljoin

import requests
import os
from bs4 import BeautifulSoup

from PIL import Image, ImageOps
import pytesseract

from config import DATASOURCE_URL, DATASOURCE_PATH

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
    image_table_rows = extract_images(soup, DATASOURCE_PATH)

    # Additional metadata
    metadata = {
        "source_url": DATASOURCE_URL,
        "table_size": len(table_data)  # Add size of table_data array
    }

    return text_data, table_headers, table_rows, image_table_rows, metadata


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

    return convert_images_to_text(images_metadata)


# Download images (optional)
def convert_images_to_text(image_metadata):
    image_text_data = []

    for image_data in image_metadata:
        # Get the path of the image from the 'src' key
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        image_path = os.path.normpath(
            os.path.join(project_root, image_data['src'])
        )
        # Check if the file exists
        if os.path.exists(image_path):
            # print(f"Found file: {image_path}")
            try:
                # Open the image and extract text using pytesseract
                image = Image.open(image_path)
                extracted_text = pytesseract.image_to_string(image, lang="eng")

                # Split text into lines
                lines = extracted_text.splitlines()

                # Split lines into blocks based on uppercase headers
                blocks = split_into_blocks(lines)

                # Append results
                image_text_data = image_text_data + blocks

            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        else:
            print(f"File not found: {image_path}")

    return image_text_data

def split_into_blocks(lines):
    blocks = []  # To store the resulting blocks
    current_block = []  # To build the current block

    def is_uppercase_header(line):
        # Check if the line contains at least one word with two or more uppercase letters
        return any(word.isalpha() and sum(1 for char in word if char.isupper()) > 1 for word in line.split())

    for line in lines:
        # Check if the line is an uppercase header
        if is_uppercase_header(line) and current_block:
            # If a new header is found, save the current block and start a new one
            blocks.append("\n".join(current_block))
            current_block = []  # Reset current block

        # Add the current line to the block
        current_block.append(line)

    # Append the last block if there is any remaining
    if current_block:
        blocks.append("\n".join(current_block))

    return blocks
