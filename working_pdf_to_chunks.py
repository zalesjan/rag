from metadata import chunk_text, extract_metadata
from db_utils import insert_chunks_to_db
from sentence_transformers import SentenceTransformer

#pdf_path = "didakticke_modifikace.pdf"
#pdf_path = "CV.pdf"
pdf_path = "rozhodnuti_Navratil_trvale_bydliste.pdf"

structured_data = extract_metadata(pdf_path, 'ces', 2)

chunked_data = chunk_text(structured_data, max_chunk_size=100)
#CHUNK OVERLAPS
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Print the first 5 chunks
for chunk in chunked_data[:1]:
    chunk["embedding"] = embedding_model.encode(chunk["text"])
    print(chunk["embedding"])
    embedding_length = len(chunk["embedding"])
    print(embedding_length)
    insert_chunks_to_db(chunk)


import faiss
import numpy as np

# Extract embeddings and metadata
embeddings = np.array([chunk["embedding"] for chunk in chunked_data])
document_metadata = [chunk["document_metadata"] for chunk in chunked_data]



# Initialize FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the index
index.add(embeddings)

# Now you have an index for your pre-chunks

# Generate a query embedding
query = "Find relevant information on veřejné zakázky."
query_embedding = embedding_model.encode(query)


# Search the FAISS index
k = 3  # Number of results to retrieve
distances, indices = index.search(np.array([query_embedding]), k)

# Retrieve the top-k results and their metadata
results = [document_metadata[idx] for idx in indices[0]]
print(results)