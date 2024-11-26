from ocr_process import extract_text_with_ocr
from metadata import chunk_text, ocr_to_dict

from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

from sentence_transformers import SentenceTransformer

# Example Usage
pdf_path = "CV.pdf"
ocr_text = extract_text_with_ocr(pdf_path)

# Print the extracted text for the first page
print(ocr_text.get("Page 1"))

data = ocr_to_dict(ocr_text)
print(data)

# Example usage:
chunked_data = chunk_text(data, max_chunk_size=100)
#CHUNK OVERLAPS
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# Print the first 5 chunks
for chunk in chunked_data:
    print(chunk)
    chunk["embedding"] = embedding_model.encode(chunk["text"])
    print(chunk)
    
import faiss
import numpy as np

# Extract embeddings and metadata
embeddings = np.array([chunk["embedding"] for chunk in chunked_data])
metadata = [chunk["metadata"] for chunk in chunked_data]

# Initialize FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the index
index.add(embeddings)

# Now you have an index for your pre-chunks

# Generate a query embedding
query = "Find relevant information on chunk 1."
query_embedding = embedding_model.encode(query)

# Search the FAISS index
k = 5  # Number of results to retrieve
distances, indices = index.search(np.array([query_embedding]), k)

# Retrieve the top-k results and their metadata
results = [metadata[idx] for idx in indices[0]]
print(results)