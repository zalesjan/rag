import fitz
from PIL import Image
import pytesseract
import os
import fitz
from PIL import Image
import pytesseract
import cv2
import numpy as np


# Set custom temp directory
os.environ["TMP"] = "C:/Temp"
os.environ["TEMP"] = "C:/Temp"

# Make sure the folder exists
if not os.path.exists(r"C:\Temp"):
    os.makedirs(r"C:\Temp")

def enhance_image_for_ocr(image):
    """
    Enhance the image for better OCR accuracy by converting to grayscale,
    applying GaussianBlur, and binarizing the image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

def split_image_into_a5(image):
    """
    Split an A4 image into two A5 halves (left and right).
    """
    h, w = image.shape[:2]  # Get image height and width
    mid = w // 2            # Midpoint of the width
    left = image[:, :mid]   # Left half
    right = image[:, mid:]  # Right half
    return left, right

def extract_text_with_ocr_split(pdf_path, language='ces', config="--psm 6"):
    """
    Extract text from a PDF, splitting each A4 page into two A5 halves.
    """
    doc = fitz.open(pdf_path)
    extracted_text = {}

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        if not text.strip():  # Perform OCR if no text layer is found
            print(f"Performing OCR on page {page_number + 1}...")

            # Render the page as an image
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert PIL Image to OpenCV format
            cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Split the image into two halves
            left, right = split_image_into_a5(cv_image)

            # Process and OCR both halves
            #left_processed = enhance_image_for_ocr(left)
            #right_processed = enhance_image_for_ocr(right)

            # Perform OCR on both halves
            left_text = pytesseract.image_to_string(Image.fromarray(left), lang=language, config=config)
            right_text = pytesseract.image_to_string(Image.fromarray(right), lang=language, config=config)

            # Combine the text from both halves
            text = f"Left Page:\n{left_text.strip()}\n\nRight Page:\n{right_text.strip()}"

        extracted_text[f"Page {page_number + 1}"] = text.strip()

    return extracted_text


def extract_text_with_ocr_enhanced(pdf_path, language, config="--psm 2"):
    """
    Extract text from a PDF using OCR, with preprocessing for better accuracy.
    """
    doc = fitz.open(pdf_path)
    extracted_text = {}

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        if not text.strip():  # Perform OCR if no text layer is found
            print(f"Performing OCR on page {page_number + 1}...")

            # Render the page as an image
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert PIL Image to OpenCV format
            cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Preprocess the image
            processed_image = enhance_image_for_ocr(cv_image)

            # Perform OCR on the processed image
            text = pytesseract.image_to_string(Image.fromarray(processed_image), lang=language, config=config)

        extracted_text[f"Page {page_number + 1}"] = text.strip()

    return extracted_text




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


import cv2
import numpy as np

def correct_rotation(image):
    """
    Auto-detect and correct rotation in an image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def extract_text_with_ocr_rotated(pdf_path, language='ces'):
    """
    Extract text from a PDF, with OCR for pages without a text layer.
    Auto-corrects rotation for better OCR accuracy.
    """
    doc = fitz.open(pdf_path)
    extracted_text = {}

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        if not text.strip():  # Perform OCR if no text layer is found
            print(f"Performing OCR on page {page_number + 1}...")
            pix = page.get_pixmap()  # Render the page as an image

            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert PIL Image to OpenCV format for rotation correction
            cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            corrected_image = correct_rotation(cv_image)

            # Convert corrected OpenCV image back to PIL Image
            pil_image = Image.fromarray(corrected_image)

            # Perform OCR on the corrected image
            text = pytesseract.image_to_string(pil_image, lang=language)

        extracted_text[f"Page {page_number + 1}"] = text.strip()

    return extracted_text



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