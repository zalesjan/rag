
import faiss
import numpy as np
from db_utils import fetch_chunks_from_db, fetch_metadata_keys, fetch_distinct_values
from sentence_transformers import SentenceTransformer

# Fetch metadata keys from the database
metadata_keys = fetch_metadata_keys()  # Assume this function fetches a list of metadata column names

# Ask user to select a metadata column
print("Available metadata columns:")
for idx, key in enumerate(metadata_keys):
    print(f"{idx + 1}: {key}")
metadata_column_idx = int(input("Select a metadata column by number: ")) - 1
if metadata_column_idx not in range(len(metadata_keys)):
    raise ValueError("Invalid selection")
metadata_column = metadata_keys[metadata_column_idx]

# Fetch distinct values for the selected column
distinct_values = fetch_distinct_values(metadata_column)  # Fetch distinct values from the selected column
print(f"\nDistinct values in '{metadata_column}':")
for idx, value in enumerate(distinct_values):
    print(f"{idx + 1}: {value}")
selected_value_idx = int(input("Select a value to filter by number: ")) - 1
if selected_value_idx not in range(len(distinct_values)):
    raise ValueError("Invalid selection")
selected_value = distinct_values[selected_value_idx]

# Fetch chunks from the database with filtering
chunked_data = fetch_chunks_from_db(filter_column=metadata_column, filter_value=selected_value)



embedding_model = SentenceTransformer("all-MiniLM-L6-v2")



chunked_data = fetch_chunks_from_db()
print(chunked_data["text"])

# Extract embeddings and metadata
embeddings = np.array([chunk["embedding"] for chunk in chunked_data])
#document_metadata = [chunk["Název_článku"] for chunk in chunked_data]

for chunk in chunked_data[:1]:
    print(embeddings)
"""
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
print(indices)
# Retrieve the top-k results and their metadata
#results = [document_metadata[idx] for idx in indices[0]]
#print(results)"""