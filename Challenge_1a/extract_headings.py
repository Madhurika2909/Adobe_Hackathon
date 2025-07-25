import fitz  # PyMuPDF
import json
import os

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    title = doc.metadata.get('title', '')

    if not title:
        # fallback to first large text as title
        first_page = doc[0]
        blocks = first_page.get_text("dict")['blocks']
        max_size = 0
        for b in blocks:
            for l in b.get('lines', []):
                for s in l.get('spans', []):
                    if s['size'] > max_size:
                        max_size = s['size']
                        title = s['text']

    headings = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            for l in b.get('lines', []):
                for s in l.get('spans', []):
                    text = s['text'].strip()
                    if len(text) > 3 and s['flags'] == 20:  # bold text
                        level = classify_heading_level(s['size'])
                        if level:
                            headings.append({
                                'level': level,
                                'text': text,
                                'page': page_num
                            })
    return {
        'title': title,
        'outline': headings
    }

def classify_heading_level(font_size):
    if font_size >= 20:
        return 'H1'
    elif font_size >= 16:
        return 'H2'
    elif font_size >= 13:
        return 'H3'
    return None

def process_pdfs(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            result = extract_outline(pdf_path)

            json_path = os.path.join(output_folder, filename.replace('.pdf', '.json'))
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=4)

if __name__ == "__main__":
    input_folder = "./input"
    output_folder = "./output"
    os.makedirs(output_folder, exist_ok=True)
    process_pdfs(input_folder, output_folder)
