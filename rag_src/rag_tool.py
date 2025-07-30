# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer
#
# from config import DATASOURCE_URL
# from rag_src.content_scrapper import scrape_web_pages
# from rag_src.html_parser import extract_content_from_html
#
# # Initialize the embedding model using SentenceTransformers
# embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
#
# # Initialize FAISS index
# def initialize_faiss_index():
#     embedding_dimension = embedding_model.get_sentence_embedding_dimension()
#     faiss_index = faiss.IndexFlatL2(embedding_dimension)  # Use L2 distance
#     return faiss_index
#
# # Define the RAG pipeline
# class RAGPipeline:
#     def __init__(self):
#         self.text_data = []
#         self.table_headers = []
#         self.table_rows = []
#         self.metadata = {}
#         self.url = DATASOURCE_URL
#         self.metadata_store = {
#             "text": [],
#             "table_header": [],
#             "table_row": []
#         }
#         self.faiss_indices = {
#             "text": initialize_faiss_index(),
#             "table_header": initialize_faiss_index(),
#             "table_row": initialize_faiss_index(),
#         }
#
#     def _extract_and_process_data(self):
#         # Extract content from the URL, scrape web pages, and process the data.
#         try:
#             # Extracting content from URL
#             html = extract_content_from_html()
#             self.text_data, self.table_headers, self.table_rows, self.metadata = scrape_web_pages(html)
#
#             # Log success
#             # print("Data extraction and processing completed successfully.")
#         except Exception as e:
#             print(f"An error occurred during data extraction and processing: {e}")
#             raise
#
#     def _process_and_store_embeddings(self, data_type, items, table_index=None):
#         for index, item in enumerate(items):
#             item_str = "\t".join(item) if isinstance(item, list) else item
#
#             try:
#                 embedding = embedding_model.encode(item_str)
#                 embedding = embedding / np.linalg.norm(embedding)
#
#                 self.faiss_indices[data_type].add(np.array([embedding]))
#                 metadata = {"type": data_type, "content": item_str, "index": len(self.metadata_store[data_type])}
#                 if table_index is not None:
#                     metadata.update({"table_index": table_index, "row_index": index})
#
#                 self.metadata_store[data_type].append(metadata)
#             except Exception as e:
#                 print(f"Error generating embedding for {item_str}: {e}")
#
#     # Generate embeddings and store in FAISS
#     def process_and_store_data(self):
#         """
#         Processes text data and table data, generates embeddings, and stores them in FAISS index.
#         """
#         # Process text data
#         self._process_and_store_embeddings("text", self.text_data)
#
#         # Process table data
#         # Process headers
#         self._process_and_store_embeddings("table_header", self.table_headers)
#
#         # Process rows
#         self._process_and_store_embeddings("table_row", self.table_rows)
#
#     # Retrieve top-k most relevant documents
#     def retrieve_faiss_index(self, query, top_k=5, data_type="text"):
#         if self.faiss_indices[data_type].ntotal == 0:
#             print(f"No embeddings found in FAISS index for data type: {data_type}")
#             return []
#
#         query_embedding = embedding_model.encode(query).reshape(1, -1)
#         query_embedding = query_embedding / np.linalg.norm(query_embedding)
#
#         distances, indices = self.faiss_indices[data_type].search(query_embedding, top_k)
#         results = []
#         for idx, dist in zip(indices[0], distances[0]):
#             if idx >= 0:
#                 result = self.metadata_store[data_type][idx]
#                 result["distance"] = dist
#                 results.append(result)
#
#         return results
#
#     def preprocess_data(self):
#         self._extract_and_process_data()
#         self.process_and_store_data()
#
#     def __call__(self, query, top_k=3):
#         """
#         End-to-end RAG pipeline: retrieve information and generate an answer.
#         """
#         self.preprocess_data()
#
#         retrieved_docs = self.retrieve_faiss_index(query, top_k=top_k)
#         if not retrieved_docs:
#             return {"query": query, "retrieved_docs": [], "answer": "No relevant information found."}
#
#         return {"query": query, "retrieved_docs": retrieved_docs}