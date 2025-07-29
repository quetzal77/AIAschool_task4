import os

from dotenv import load_dotenv
import openai

load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-05-15"

# # Web pages using as datasource
DATASOURCE_URL = "https://investors.epam.com/news/news-details/2025/EPAM-Reports-Results-for-Fourth-Quarter-and-Full-Year-2024/default.aspx"

# Path for datasource html page stored locally
DATASOURCE_PATH = "../datasources/EPAM Systems, Inc. - EPAM Reports Results for Fourth Quarter and Full Year 2024.html"



