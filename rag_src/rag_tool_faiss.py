import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import DATASOURCE_URL
from rag_src.content_scrapper import scrape_web_pages
from rag_src.html_parser import extract_content_from_html

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def combine_text_and_rows_to_chunks(table_headers, table_rows):
    # Combine table headers and rows into coherent chunks
    table_chunks = []
    for headers, rows in zip(table_headers, table_rows):
        # Combine headers into a single string
        header_string = " | ".join(headers)  # Using " | " separator between headers

        # Combine rows into a single string
        row_strings = [" | ".join(row) for row in rows]  # Combine cells in each row using " | "
        rows_string = "\n".join(row_strings)  # Combine all rows into a single string, separated by newlines

        # Create a meaningful chunk for the table
        table_chunk = f"Table Headers: {header_string}\nTable Rows:\n{rows_string}"
        table_chunks.append(table_chunk)
    return table_chunks

# Define the RAG pipeline
def convert_text_to_embeddings(embeddings):
    # Convert embeddings to numpy array
    embedding_matrix = np.array(embeddings)
    return embedding_matrix

# Index the embeddings using FAISS
def index_embeddings(embedding_matrix):
    dimension = embedding_matrix.shape[1]  # Dimension of the embeddings
    index = faiss.IndexFlatL2(dimension)  # L2 distance metric
    index.add(embedding_matrix)  # Add embeddings to the index

    # Save the index for later use
    faiss.write_index(index, "vector_index.faiss")
    return index

class RAGPipeline:
    def __init__(self):
        self.text_data = []
        self.table_headers = []
        self.table_rows = []
        self.metadata = []

    def __call__(self, query):
        """
        End-to-end RAG pipeline: retrieve information and generate an answer.
        """
        # Extracting content from URL
        html = extract_content_from_html()
        self.text_data, self.table_headers, self.table_rows, self.metadata = scrape_web_pages(html)

        # Combine text data and table chunks
        table_chunks = combine_text_and_rows_to_chunks(self.table_headers, self.table_rows)
        all_chunks = self.text_data + table_chunks

        # Generate embeddings for all chunks
        embeddings = model.encode(all_chunks)

        # Convert text chunks to embeddings
        embedding_matrix = convert_text_to_embeddings(embeddings)

        # Initialize FAISS index
        index = index_embeddings(embedding_matrix)

        # Query embedding
        query_embedding = model.encode([query])

        # Perform similarity search
        k = 5  # Number of top results to retrieve
        distances, indices = index.search(np.array(query_embedding), k)

        # Retrieve results
        results = [all_chunks[i] for i in indices[0]]
        # print("Top results:", results)

        return results




