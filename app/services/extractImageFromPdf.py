import os
import sys
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image


def find_poppler_path():
    common_paths = [
        r"C:\Users\rakshithas\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin",
        r"C:\Program Files\poppler\bin",
        r"C:\Program Files (x86)\poppler\bin",
        r"C:\poppler\bin",
        os.path.expanduser(r"~\AppData\Local\poppler\bin"),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"[OK] Found poppler at: {path}")
            return path
    
    return None


def extract_images_from_pdf(pdf_path, output_folder="extracted_images", poppler_path=None):
    
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Converting PDF to images: {pdf_path}")
    
    if not poppler_path:
        poppler_path = find_poppler_path()
        if not poppler_path:
            print("Poppler not found in common locations")
    
    try:
        if poppler_path and os.path.exists(poppler_path):
            images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
        else:
            images = convert_from_path(pdf_path, dpi=300)
        
        extracted_files = []
        
        for i, image in enumerate(images):
            output_path = os.path.join(output_folder, f"page_{i+1:03d}.png")
            image.save(output_path, "PNG")
            extracted_files.append(output_path)
            print(f"  [OK] Extracted: {output_path}")
        
        print(f"\nTotal images extracted: {len(extracted_files)}")
        return extracted_files
        
    except Exception as e:
        print(f"Error extracting images from PDF: {e}")
        print("  1. Make sure poppler is installed: https://github.com/oschwartz10612/poppler-windows/releases/")
        print("  2. Add poppler/bin to your system PATH")
        print("  3. Or provide the explicit path to poppler bin directory")
        return []


if __name__ == "__main__":
    pdf_file = "../data/example.pdf"
    
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file '{pdf_file}' not found.")
    else:
        extracted_images = extract_images_from_pdf(pdf_file)
        
        if extracted_images:
            print(f"\nSuccessfully extracted {len(extracted_images)} images")
            print("Images saved to: extracted_images/")
        else:
            print("Failed to extract images from PDF")
