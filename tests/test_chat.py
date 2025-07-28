# from rag_src.html_parser import extract_content_from_html
# from rag_src.rag_tool import RAGPipeline
# from rag_src.content_scrapper import scrape_web_pages
#
# # Web pages using as datasource
# url = "https://investors.epam.com/news/news-details/2025/EPAM-Reports-Results-for-Fourth-Quarter-and-Full-Year-2024/default.aspx"
#
# # Path for datasource html page stored localy
# path = "../datasources/EPAM Systems, Inc. - EPAM Reports Results for Fourth Quarter and Full Year 2024.html"
#
# # Web page content retrieval
# # html = scrape_aspx_page(url) # doest work because EPAM aspx page protected from online attacks
# html = extract_content_from_html(path)
# text_data, table_data, metadata = scrape_web_pages(html, url)
#
# # User query
# query = "What is Cost of revenues (exclusive of depreciation and amortization)"
#
# # Instantiate RAG pipeline
# rag_pipeline = RAGPipeline(text_data, table_data, metadata)
#
# # Generate LLM answer
# results = rag_pipeline(query)
#
# print("Query Info:", results["query"])
#
# print("Query Results:")
# for result in results["retrieved_docs"]:
#      print(result)

from rag_src.chat_tool import chat

chat()