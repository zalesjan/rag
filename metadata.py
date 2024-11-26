from typing import List, Dict

def ocr_to_dict(ocr_text):
    data = []
    for page_number, page_text in ocr_text.items():
        data.append({
            "text": page_text,
            "metadata": {"chapter_id": f"page_{page_number}",
            "chapter_name": f"Page {page_number}",
            "paragraph_id": f"{page_number}_1"}  # Assuming one paragraph per page initially
        })

    return data

def chunk_text(data: List[Dict], max_chunk_size: int = 200) -> List[Dict]:
    """
    Splits paragraphs into smaller chunks suitable for embedding generation.
    Args:
        data (List[Dict]): List of paragraphs with metadata.
        max_chunk_size (int): Maximum number of tokens (or words) per chunk.
    Returns:
        List[Dict]: List of chunks with updated metadata.
    """
    
    chunks = []

    for entry in data:
        paragraph = entry["text"]
        words = paragraph.split()
        
        # Break paragraph into chunks
        for i in range(0, len(words), max_chunk_size):
            chunk_words = words[i:i + max_chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "text": chunk_text,  # Change key to "text"
                "metadata": {
                    "chapter_id": entry["metadata"]["chapter_id"],
                    "chapter_name": entry["metadata"]["chapter_name"],
                    "paragraph_id": entry["metadata"]["paragraph_id"],
                    "chunk_id": f"{entry['metadata']['paragraph_id']}_chunk_{len(chunks) + 1}"
                }
            })

    return chunks



