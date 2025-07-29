import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from config import DATASOURCE_URL, DATASOURCE_PATH


# Setup Selenium with a headless browser
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for better performance
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model (useful for some servers)
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Provide the path to your ChromeDriver
    # chromedriver_path = r"C:\WORK\6. Python\HW4AIArch env\chromedriver.exe"
    service = Service("../chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# Scrape the ASPX page
def scrape_aspx_page():
    driver = initialize_driver()
    driver.get(DATASOURCE_URL)

    # Wait for the page to load (adjust time as needed)
    driver.implicitly_wait(3)

    # Get the fully rendered HTML
    html = driver.page_source

    # Close the browser
    driver.quit()

    return html

# Extracts text, tables, and image metadata from a local HTML file.
def extract_content_from_html():

    # Check if the file exists
    if not os.path.exists(DATASOURCE_PATH):
        raise FileNotFoundError(f"File not found: {DATASOURCE_PATH}")

    # Read the HTML file
    with open(DATASOURCE_PATH, "r", encoding="utf-8") as file:
        html_content = file.read()

    return html_content


