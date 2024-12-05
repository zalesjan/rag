from typing import List, Dict

def extract_text_with_ocr(pdf_path, language='ces', config="--psm 2"): 
    doc = fitz.open(pdf_path)
    extracted_text = {}

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        if not text.strip():  # Perform OCR if no text layer is found
            print(f"Performing OCR on page {page_number + 1}...")
            pix = page.get_pixmap()  # Render the page as an image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang=language)

        extracted_text[f"Page {page_number + 1}"] = text.strip()
    return extracted_text


def chunk_text(document_metadata, data: List[Dict], max_chunk_size: int = 200) -> List[Dict]:
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
                "page_metadata": {
                    "chapter_id": entry["metadata"]["chapter_id"],
                    "chapter_name": entry["metadata"]["chapter_name"],
                    "paragraph_id": entry["metadata"]["paragraph_id"],
                    "chunk_id": f"{entry['metadata']['paragraph_id']}_chunk_{len(chunks) + 1}"
                },
                "document_metadata": {
                    "atuor_1": document_metadata["Autor 1"],
                    "Autor 2": document_metadata["Autor 2"],
                    "Název článku": document_metadata["Název článku"],
                    "Subjekt": document_metadata["Subjekt"],
                    "Druh": document_metadata["Druh"],
                    "Portál": document_metadata["Portál"],
                    "Datum vydání": document_metadata["Datum vydání"],
                    "Dostupné z": document_metadata["Dostupné z"],
                    "Odkaz": document_metadata["Odkaz"],
                    "Kategorie": document_metadata["Kategorie"],
                }
            })

    return chunks

import re
import fitz
from PIL import Image
import pytesseract


def extract_metadata(pdf_path, language='ces', config="--psm 2"):
    """
    Extracts text, chapters, sections, and paragraphs from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        List[Dict]: List of structured data including text, headings, and metadata.
    """

    doc = fitz.open(pdf_path)
    structured_data = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        if not text.strip():  # Perform OCR if no text layer is found
            print(f"Performing OCR on page {page_number + 1}...")
            pix = page.get_pixmap()  # Render the page as an image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang=language, config=config)

        # Ensure page_number is a string
        page_number_str = str(page_number+1)

        # Split into paragraphs based on blank lines
        paragraphs = re.split(r'\n\s*\n', text)

        current_heading = None
        chapter_id = None

        for para in paragraphs:
            # Match headings
            heading_match = re.match(r'^\s*(\d+\.\d+|\d+)?\s*([A-ZČŘŠŽŤÁÉÍÓÚÝŘ\s]{3,}(?:\n[A-ZČŘŠŽŤÁÉÍÓÚÝŘ\s]*)?)', para)

            if heading_match:
                # Detected a new heading
                chapter_id = heading_match.group(1) or f"page_{page_number_str}"
                current_heading = heading_match.group(2).strip()
                paragraph_text = para[len(heading_match.group(0)):].strip()

                structured_data.append({
                    "text": paragraph_text,
                    "metadata": {
                        "chapter_id": chapter_id,
                        "chapter_name": current_heading,
                        "paragraph_id": f"{chapter_id}_para_{len(structured_data) + 1}",
                        "page_number": page_number_str,
                    }
                })
            else:
                # Non-heading paragraphs belong to the current heading
                structured_data.append({
                    "text": para.strip(),
                    "metadata": {
                        "chapter_id": chapter_id or f"page_{page_number_str}",
                        "chapter_name": current_heading or f"Page {page_number_str}",
                        "paragraph_id": f"{chapter_id or f'page_{page_number_str}'}_para_{len(structured_data) + 1}",
                        "page_number": page_number_str,
                    }
                })

    return structured_data
