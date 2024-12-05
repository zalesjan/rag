import re

def extract_text(ocr_text):
    """
    Extracts text, chapters, sections, and paragraphs from a PDF file.
    Args:
        file_path (str): Path to the PDF file.
    Returns:
        List[Dict]: List of structured data including chapters, sections, and paragraphs.
    """
    
    structured_data = []

    # Loop through pages
    for page_number , page_text in ocr_text.items():
        
        # Ensure page_number is a string for concatenation
        page_number_str = str(page_number)

        # Split into paragraphs based on blank lines
        paragraphs = re.split(r'\n\s*\n', page_text)

        for para in paragraphs:
            # Assume paragraphs with headings follow a pattern (e.g., bold or numbered)
            heading_match = re.match(r'^\s*(\d+\.\d+|\d+)?\s*(.*?):', para)
            if heading_match:
                chapter_id = heading_match.group(1) or f"page_{page_number_str}"
                chapter_name = heading_match.group(2)
                paragraph_text = para.replace(heading_match.group(0), "").strip()

                structured_data.append({
                    "text": paragraph_text,
                    "metadata": {"chapter_id": chapter_id,
                    "chapter_name": chapter_name,
                    "paragraph_id": f"{chapter_id}_para_{len(structured_data) + 1}",
                    "page_number": page_number_str}
                })
            else:
                # Non-heading paragraphs are treated as standalone
                structured_data.append({
                    "text": para.strip(),
                    "metadata": {"chapter_id": f"page_{page_number_str}",
                    "chapter_name": f"Page {page_number_str}",
                    "paragraph_id": f"page_{page_number_str}_para_{len(structured_data) + 1}",
                    "page_number": page_number_str}
                })

    return structured_data

