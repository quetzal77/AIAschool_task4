from rag_src.html_parser import scrape_aspx_page, extract_content_from_html
from rag_src.rag_tool import RAGPipeline
from rag_src.content_scrapper import scrape_web_pages

# Web pages using as datasource
url = "https://investors.epam.com/news/news-details/2025/EPAM-Reports-Results-for-Fourth-Quarter-and-Full-Year-2024/default.aspx"

# Path for datasource html page stored localy
path = "../datasources/EPAM Systems, Inc. - EPAM Reports Results for Fourth Quarter and Full Year 2024.html"

# Web page content retrieval
# html = scrape_aspx_page(url) # doest work because EPAM aspx page protected from online attacks
html = extract_content_from_html(path)
web_page_content = scrape_web_pages(html, url)

# User query
query = "What is a maximum dimensions of language in centimeters?"

# Instantiate RAG pipeline
rag_pipeline = RAGPipeline(web_page_content = web_page_content)

# Generate LLM answer
answer = rag_pipeline(query, top_k=3)

# Print the results
print("Query:", answer['query'])

print("Retrieved Documents:")
for i, doc in enumerate(answer['retrieved_docs']):
     print(f"[{i+1}] {doc[:300]}...")  # Show the first 300 characters of each document

print("\nGenerated Answer:", answer['answer'])