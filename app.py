from ocr_process import extract_text_with_ocr
from metadata import chunk_text, ocr_to_dict

from sentence_transformers import SentenceTransformer

# Example Usage
#pdf_path = "didakticke_modifikace.pdf"
pdf_path = "CV.pdf"

ocr_text = extract_text_with_ocr(pdf_path)

# Print the extracted text for the first page
print(ocr_text.get("Page 1"))

data = ocr_to_dict(ocr_text)


# Example usage:
chunked_data = chunk_text(data, max_chunk_size=100)
#CHUNK OVERLAPS
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# Print the first 5 chunks
for chunk in chunked_data:
    print(chunk["text"])
    chunk["embedding"] = embedding_model.encode(chunk["text"])
    print(chunk)
    