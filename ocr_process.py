import fitz
from PIL import Image
import pytesseract

def extract_text_with_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = {}

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        if not text.strip():  # Perform OCR if no text layer is found
            print(f"Performing OCR on page {page_number + 1}...")
            pix = page.get_pixmap()  # Render the page as an image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)

        extracted_text[f"Page {page_number + 1}"] = text.strip()
    return extracted_text


