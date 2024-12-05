import os
import pandas as pd
from metadata import chunk_text, extract_metadata
from db_utils import insert_chunks_to_db, get_db_connection
from sentence_transformers import SentenceTransformer

# Paths
documents_folder = r"C:\Users\zalesak\Documents\tenderix-dev\test_data"
excel_path = r"C:\Users\zalesak\Documents\tenderix-dev\data\cz\general_db_v4.xlsx"  # Replace with the path to your Excel file

# Load metadata from Excel
document_metadata_df = pd.read_excel(excel_path, sheet_name="Články k citaci")

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Process each PDF file
for pdf_file in os.listdir(documents_folder):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(documents_folder, pdf_file)
        print(f"Processing: {pdf_path}")

        # Match metadata row based on file name
        document_row = document_metadata_df[document_metadata_df["Název článku"].apply(lambda x: x in pdf_file)]
        if document_row.empty:
            print(f"No matching metadata found for: {pdf_file}")
            continue

        # Extract metadata fields
        document_metadata = document_row.iloc[0].to_dict()  # Convert matched row to dictionary

        # Extract text and metadata from the PDF
        structured_data = extract_metadata(pdf_path, 'ces', 2)

        # Add metadata to each paragraph
        for entry in structured_data:
            entry["document_metadata"] = {
                "Autor 1": document_metadata.get("Autor 1"),
                "Autor 2": document_metadata.get("Autor 2"),
                "Název článku": document_metadata.get("Název článku"),
                "Subjekt": document_metadata.get("Subjekt"),
                "Druh": document_metadata.get("Druh"),
                "Portál": document_metadata.get("Portál"),
                "Datum vydání": document_metadata.get("Datum vydání"),
                "Dostupné z": document_metadata.get("Dostupné z"),
                "Odkaz": document_metadata.get("Odkaz"),
                "Kategorie": document_metadata.get("Kategorie"),
            }

        # Chunk the document
        chunked_data = chunk_text(document_metadata, structured_data, max_chunk_size=100)

        # Generate embeddings and insert into the database
        for chunk in chunked_data:
            # Generate embeddings
            chunk["embedding"] = embedding_model.encode(chunk["text"])
            # Execute batch insert with execute_values
            conn = get_db_connection()
            cur = conn.cursor()
            insert_chunks_to_db(cur, chunk)
            conn.commit()
            cur.close()
            conn.close()
print("Processing complete.")
"""

import faiss
import numpy as np

# Extract embeddings and metadata
embeddings = np.array([chunk["embedding"] for chunk in chunked_data])
document_metadata = [chunk["document_metadata"]  for chunk in chunked_data]


# Initialize FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the index
index.add(embeddings)

# Now you have an index for your pre-chunks

# Generate a query embedding
query = "Find relevant information on chunk veřejné zakázky."
query_embedding = embedding_model.encode(query)


# Search the FAISS index
k = 3  # Number of results to retrieve
distances, indices = index.search(np.array([query_embedding]), k)

# Retrieve the top-k results and their metadata
results = [document_metadata[idx] for idx in indices[0]]
print(results)"""