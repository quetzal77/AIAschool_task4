# Encode the corpus into embeddings
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import AZURE_OPENAI_DEPLOYMENT_NAME, DATASOURCE_URL
from rag_src.content_scrapper import scrape_web_pages
from rag_src.html_parser import extract_content_from_html

# Initialize the embedding model using SentenceTransformers
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS index
def initialize_faiss_index():
    embedding_dimension = embedding_model.get_sentence_embedding_dimension()
    faiss_index = faiss.IndexFlatL2(embedding_dimension)  # Use L2 distance
    return faiss_index

# Define the RAG pipeline
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


class RAGPipeline:
    def __init__(self):
        self.text_data = []
        self.table_data = []
        self.metadata = {}
        self.url = DATASOURCE_URL
        self. metadata_store = []
        self.faiss_index = initialize_faiss_index()

    def _extract_and_process_data(self):
        # Extract content from the URL, scrape web pages, and process the data.
        try:
            # Extracting content from URL
            html = extract_content_from_html()
            self.text_data, self.table_data, self.metadata = scrape_web_pages(html)

            # Log success
            # print("Data extraction and processing completed successfully.")
        except Exception as e:
            print(f"An error occurred during data extraction and processing: {e}")
            raise

    # Generate embeddings and store in FAISS
    def process_and_store_data(self):
        # Generate embeddings for text data
        for i, chunk in enumerate(self.text_data):
            text_embedding = embedding_model.encode(chunk)  # Generate embedding
            self.faiss_index.add(np.array([text_embedding]))  # Add embedding to FAISS index
            self.metadata_store.append({"type": "text", "chunk_index": i, "content": chunk})

        # # Generate embeddings for table data - doesnt work as we have to break table string to chunks
        # for i, table in enumerate(self.table_data):
        #     # Convert the table to a string representation
        #     # table_str = table.to_string(index=False, header=True) # doesnt work with pandas lib, need time to understand why
        #     table_str = "\n".join(["\t".join(row) for row in table])  # Join rows with tabs and rows with newlines
        #     table_embedding = embedding_model.encode(table_str)  # Generate embedding
        #     self.faiss_index.add(np.array([table_embedding]))  # Add embedding to FAISS index
        #     self.metadata_store.append({"type": "table", "source_url": self.url, "table_index": i, "content": table_str})

        # print("Extracted Table Data:")
        # for i, table in enumerate(self.table_data):
        #     print(f"Table {i}:")
        #     for row in table:
        #         print(row)

        # Generate embeddings for table data
        for i, table in enumerate(self.table_data):

            """
            Separates header rows (rows with a single element) from table data rows.
            """
            table_headers = []
            table_rows = []

            for row in table:
                if len(row) == 1:  # Identify header rows (rows with a single element)
                    table_headers.append(row[0])  # Collect the single element as a header
                elif len(row) > 1:  # Identify table data rows (rows with multiple elements)
                    table_rows.append(row)

            #     Filters rows in the table:
            #     1. Removes empty rows.
            #     2. Keeps rows where the first cell is empty but the row has more than one element.
            table_rows = filter_rows(table_rows)

            # Process each row in the table
            for row_index, row in enumerate(table_headers):
                row_str = "".join(row)
                # Generate embedding for the row
                self.faiss_index.add(
                    np.array(
                        [embedding_model.encode(row_str)]
                ))
                self.metadata_store.append({
                    "type": "table_header",
                    "table_index": i,
                    "row_index": row_index,
                    "content": row_str
                })

            # Process each row in the table
            for row_index, row in enumerate(table_rows):
                row_str = "\t".join(row)
                # Generate embedding for the row
                self.faiss_index.add(
                    np.array(
                        [embedding_model.encode(row_str)]
                ))
                self.metadata_store.append({
                    "type": "table_row",
                    "table_index": i,
                    "row_index": row_index,
                    "content": row_str
                })

        # print(f"Data from {self.url} has been processed and stored in the FAISS index.")

    # Retrieve top-k most relevant documents
    def retrieve_faiss_index(self, query, top_k=5):

        # Generate embedding for the query
        query_embedding = embedding_model.encode(query).reshape(1, -1)

        # Perform similarity search
        distances, indices = self.faiss_index.search(query_embedding, top_k)

        # Retrieve metadata for the top results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx >= 0:  # Ensure valid index
                result = self.metadata_store[idx]
                result["distance"] = dist
                results.append(result)

        return results

    # Save and Load FAISS Index and Metadata (optional, potentially can use it later)
    def save_faiss_index(self, index_file="faiss_index.bin", metadata_file="metadata.pkl"):
        faiss.write_index(self.faiss_index, index_file)
        with open(metadata_file, "wb") as f:
            pickle.dump(self.metadata_store, f)
        print("FAISS index and metadata have been saved.")

    def load_faiss_index(self, index_file="faiss_index.bin", metadata_file="metadata.pkl"):
        self.faiss_index = faiss.read_index(index_file)
        with open(metadata_file, "rb") as f:
            self.metadata_store = pickle.load(f)
        print("FAISS index and metadata have been loaded.")

    def __call__(self, query, top_k=3):
        """
        End-to-end RAG pipeline: retrieve information and generate an answer.
        """
        self._extract_and_process_data()
        self.process_and_store_data()
        retrieved_docs = self.retrieve_faiss_index(query, top_k=top_k)
        if not retrieved_docs:
            return {"query": query, "retrieved_docs": [], "answer": "No relevant information found."}

        # answer = self.generate(query, retrieved_docs)
        # return {"query": query, "retrieved_docs": retrieved_docs, "answer": answer}
        return {"query": query, "retrieved_docs": retrieved_docs}