import fitz  # PyMuPDF
import json
import os
from collections import Counter
import re

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)

    # Get title from metadata or fallback
    title = doc.metadata.get('title', '').strip()
    if not title:
        first_page = doc[0]
        blocks = first_page.get_text("dict")['blocks']
        max_size = 0
        for b in blocks:
            for l in b.get('lines', []):
                for s in l.get('spans', []):
                    if s['size'] > max_size and s['text'].strip():
                        max_size = s['size']
                        title = s['text'].strip()

    # Collect all text spans with their font sizes
    all_spans = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            for l in b.get('lines', []):
                for s in l.get('spans', []):
                    text = s['text'].strip()
                    if text and len(text) > 1:  # Skip empty or single character text
                        all_spans.append({
                            'text': text,
                            'size': round(s['size'], 1),
                            'page': page_num
                        })

    print(f"Found {len(all_spans)} text spans in {pdf_path}")
    
    # Get unique font sizes and sort them
    font_sizes = sorted(list(set([span['size'] for span in all_spans])), reverse=True)
    print(f"Font sizes found: {font_sizes}")
    
    # Create font size to heading level mapping
    # Take the top 6 font sizes and map them to H1-H6
    heading_sizes = font_sizes[:6] if len(font_sizes) >= 6 else font_sizes + [0] * (6 - len(font_sizes))
    size_to_level = {}
    for i, size in enumerate(heading_sizes):
        if size > 0:
            size_to_level[size] = f'H{i+1}'
    
    print(f"Size to level mapping: {size_to_level}")
    
    # Extract headings
    headings = []
    for span in all_spans:
        if span['size'] in size_to_level:
            # Additional filtering to avoid very long text as headings
            if len(span['text']) < 300:  # Reasonable length for headings
                headings.append({
                    'level': size_to_level[span['size']],
                    'text': span['text'],
                    'page': span['page']
                })

    print(f"Extracted {len(headings)} headings")
    
    # Sort headings by page and then by level
    headings.sort(key=lambda x: (x['page'], x['level']))

    return {
        'title': title,
        'outline': headings
    }

def process_pdfs(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            print(f"Processing: {filename}")
            
            try:
                result = extract_outline(pdf_path)
                json_path = os.path.join(output_folder, filename.replace('.pdf', '.json'))
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                print(f"  Extracted {len(result['outline'])} headings")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    input_folder = "./input"
    output_folder = "./output"
    process_pdfs(input_folder, output_folder)
