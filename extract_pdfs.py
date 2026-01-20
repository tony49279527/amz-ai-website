import os
import fitz  # PyMuPDF

def extract_text_from_pdfs(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Save to text file
            txt_filename = filename + ".txt"
            txt_path = os.path.join(output_dir, txt_filename)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Extracted: {txt_filename}")

if __name__ == "__main__":
    extract_text_from_pdfs("uploads", "temp_texts")
