import pypdf
import docx
import re
import logging

logging.basicConfig(level=logging.INFO)

def extract_text_from_upload(uploaded_file):
    # --- 1. SIZE GATEKEEPER (Hackathon Safety) ---
    MAX_FILE_SIZE = 5 * 1024 * 1024 

    if uploaded_file.size > MAX_FILE_SIZE:
        return "⚠️ File too large. Please upload a document smaller than 5MB."

    # --- 2. REST OF YOUR EXTRACTION LOGIC ---
    file_type = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_type == "pdf":
            reader = pypdf.PdfReader(uploaded_file)
            text_parts = []

            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text_parts.append(content)

            text = " ".join(text_parts)

        elif file_type == "docx":
            doc = docx.Document(uploaded_file)
            text = " ".join([para.text for para in doc.paragraphs])

        else:
            raw_data = uploaded_file.read()
            try:
                text = raw_data.decode("utf-8")
            except UnicodeDecodeError:
                text = raw_data.decode("latin-1")

    except Exception as e:
        logging.error(f"Error in file {uploaded_file.name}: {str(e)}")
        return f"Error processing file: {str(e)}"

    # Cleaning
    # 1. Remove extra whitespace/newlines
    text = re.sub(r'\s+', ' ', text).strip()

    if not text:
        return "⚠️ Alert: No readable text found. (Possibly scanned document)."

    logging.info(f"{uploaded_file.name}: Extracted {len(text)} characters.")
    return text