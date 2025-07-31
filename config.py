import os

from dotenv import load_dotenv
import openai
from langchain_openai import AzureChatOpenAI

load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Initialize LLM
llm_azure = AzureChatOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2023-07-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    model=AZURE_OPENAI_DEPLOYMENT_NAME,
    temperature=0.0
)

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-05-15"

# # Web pages using as datasource
DATASOURCE_URL = "https://investors.epam.com/news/news-details/2025/EPAM-Reports-Results-for-Fourth-Quarter-and-Full-Year-2024/default.aspx"

# Path for datasource html page stored locally
DATASOURCE_PATH = "../datasources/EPAM Systems, Inc. - EPAM Reports Results for Fourth Quarter and Full Year 2024.html"



