import fitz  # PyMuPDF
import json
import os
from collections import Counter
import re
import math # For math.isclose

def calculate_similarity(s1, s2):
    """
    Calculates the Levenshtein distance similarity between two strings.
    Returns a float between 0.0 (no similarity) and 1.0 (identical).
    """
    if not s1 or not s2:
        return 0.0
    
    s1 = s1.lower()
    s2 = s2.lower()

    rows = len(s1) + 1
    cols = len(s2) + 1
    
    # Initialize matrix
    dp = [[0 for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        dp[i][0] = i
    for j in range(cols):
        dp[0][j] = j

    # Fill the matrix
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # Deletion
                dp[i][j-1] + 1,      # Insertion
                dp[i-1][j-1] + cost  # Substitution
            )
            
    distance = dp[rows-1][cols-1]
    max_len = max(len(s1), len(s2))
    
    if max_len == 0: # Handle empty strings gracefully
        return 1.0
        
    return 1 - (distance / max_len)

def auto_detect_title(all_spans, filename):
    """
    Auto-detects the document title based on font size and patterns,
    similar to the JavaScript logic.
    """
    # Look for largest font size text in first few pages (e.g., up to page 3)
    first_page_spans = [span for span in all_spans if span['page'] <= 3]
    
    if not first_page_spans:
        return os.path.splitext(filename)[0]

    # Find the largest font size among first page items
    max_font_size = 0
    if first_page_spans:
        max_font_size = max(span['size'] for span in first_page_spans)
    
    title_candidates = [
        span for span in first_page_spans
        if math.isclose(span['size'], max_font_size, rel_tol=0.05) and # Allow a small tolerance for "largest"
           5 < len(span['text']) < 100 and
           not re.match(r'^\d+$|^Page\s+\d+', span['text'], re.IGNORECASE) and
           not re.match(r'^(Copyright|Version|Table\s+of\s+Contents|Abstract|Preface|Appendix|Index|Glossary|Executive\s+Summary)', span['text'], re.IGNORECASE)
    ]
    
    # Prioritize items appearing earlier on the page (lower y-coordinate)
    title_candidates.sort(key=lambda x: x['bbox'][1]) # Sort by top-left y-coordinate

    if title_candidates:
        # Take the first substantial text with max font size
        return title_candidates[0]['text']
    
    # Fallback: look for text patterns that look like titles
    title_patterns_candidates = [
        span for span in first_page_spans
        if 10 < len(span['text']) < 80 and
           re.match(r'^[A-Z]', span['text']) and # Starts with uppercase
           not re.match(r'^(Copyright|Version|Page|Table)', span['text'], re.IGNORECASE)
    ]
    
    title_patterns_candidates.sort(key=lambda x: x['bbox'][1]) # Sort by top-left y-coordinate

    if title_patterns_candidates:
        return title_patterns_candidates[0]['text']
        
    return os.path.splitext(filename)[0]


def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    
    # Collect all text spans with their font sizes, positions, and page numbers
    all_spans_details = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            for l in b.get('lines', []):
                for s in l.get('spans', []):
                    text = s['text'].strip()
                    if text and len(text) > 1:  # Skip empty or single character text
                        all_spans_details.append({
                            'text': text,
                            'size': round(s['size'], 1),
                            'page': page_num,
                            'fontName': s['font'],
                            'bbox': s['bbox'] # (x0, y0, x1, y1)
                        })

    print(f"Found {len(all_spans_details)} text spans in {pdf_path}")
    
    # Get unique font sizes and sort them
    font_sizes = sorted(list(set([span['size'] for span in all_spans_details])), reverse=True)
    print(f"Font sizes found: {font_sizes}")
    
    # Auto-detect title using the new, more robust logic
    title = auto_detect_title(all_spans_details, os.path.basename(pdf_path))
    
    # Calculate average and max font sizes for thresholding
    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
    max_overall_font_size = font_sizes[0] if font_sizes else 0
    
    # Define heading thresholds based on font sizes, similar to JS
    # Using relative thresholds for robustness across different PDFs
    h1_threshold = max_overall_font_size * 0.85 if max_overall_font_size else 0
    h2_threshold = avg_font_size * 1.2 if avg_font_size else 0
    h3_threshold = avg_font_size * 1.1 if avg_font_size else 0

    print(f"Calculated thresholds: H1={h1_threshold:.1f}, H2={h2_threshold:.1f}, H3={h3_threshold:.1f}")

    # Extract headings using combined logic
    extracted_headings = []
    processed_texts = set() # To help with duplicate filtering

    for span in all_spans_details:
        text = span['text'].strip()
        
        # Skip very short texts or purely numeric strings
        if len(text) < 3 or re.match(r'^\d+$', text):
            continue
        
        level = None
        is_heading = False
        
        # 1. Check for numbered headings (1., 1.1, 1.1.1, etc.)
        numbered_match = re.match(r'^(\d+\.(?:\d+\.))\s(.+)$', text)
        if numbered_match:
            dots = numbered_match.group(1).count('.')
            if dots == 1:
                level = 'H1'
            elif dots == 2:
                level = 'H2'
            else: # More than 2 dots, treat as H3+
                level = 'H3' 
            is_heading = True
        
        # 2. Check for common section names (Chapter, Introduction, Conclusion)
        elif re.match(r'^(Chapter|Section|Part)\s+\d+', text, re.IGNORECASE) or \
             re.match(r'^(Introduction|Overview|Conclusion|Summary|References|Bibliography|Acknowledgments?|Table\s+of\s+Contents|Abstract|Preface|Appendix|Index|Glossary|Executive\s+Summary|Background|Methodology|Results|Discussion|Recommendations)', text, re.IGNORECASE):
            level = 'H1'
            is_heading = True
        
        # 3. Font size based detection (prioritize larger fonts)
        elif span['size'] >= h1_threshold and 5 < len(text) < 100:
            level = 'H1'
            is_heading = True
        elif span['size'] >= h2_threshold and 5 < len(text) < 80:
            level = 'H2'
            is_heading = True
        elif span['size'] >= h3_threshold and 5 < len(text) < 60:
            level = 'H3'
            is_heading = True
            
        # 4. Additional filtering for title case and reasonable length
        if is_heading and re.match(r'^[A-Z][a-zA-Z0-9\s:,-_()&./\[\]]+$', text) and len(text) < 300: # Broaden regex for special chars
            
            # Check for duplicates using similarity
            is_duplicate = False
            for existing_text in processed_texts:
                if calculate_similarity(existing_text, text) > 0.85: # Use a threshold, e.g., 0.85 for high similarity
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                extracted_headings.append({
                    'level': level,
                    'text': text,
                    'page': span['page'],
                    'fontSize': span['size'] # Keep for potential future use or debugging
                })
                processed_texts.add(text) # Add original text for similarity comparison

    print(f"Extracted {len(extracted_headings)} headings after detailed analysis.")
    
    # Sort headings by page and then by their vertical position (y0)
    # This helps ensure correct order on a page for same-level headings
    # We'll re-extract full span details to sort by y-coordinate
    
    # Temporarily add bbox to headings for accurate sorting
    temp_headings_with_bbox = []
    for heading in extracted_headings:
        # Find the original span to get its y-coordinate
        found_span = next((s for s in all_spans_details if s['text'] == heading['text'] and s['page'] == heading['page'] and math.isclose(s['size'], heading['fontSize'], rel_tol=0.01)), None)
        if found_span:
            heading['y0'] = found_span['bbox'][1]
        else:
            heading['y0'] = 0 # Fallback
        temp_headings_with_bbox.append(heading)

    temp_headings_with_bbox.sort(key=lambda x: (x['page'], x['y0']))

    # Remove the temporary 'y0' before returning
    final_headings = [{k: v for k, v in h.items() if k != 'y0' and k != 'fontSize'} for h in temp_headings_with_bbox]


    return {
        'title': title,
        'outline': final_headings,
        'totalPages': doc.page_count
    }

def process_pdfs(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            print(f"\n--- Processing: {filename} ---")
            
            try:
                result = extract_outline(pdf_path)
                json_path = os.path.join(output_folder, filename.replace('.pdf', '.json'))
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                print(f"Successfully processed {filename}. Extracted {len(result['outline'])} headings. Output saved to {json_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    input_folder = "./input"
    output_folder = "./output"

    # Create dummy input folder and a placeholder PDF for testing if they don't exist
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        print(f"Created input folder: {input_folder}")
        # To run this code, you'll need to place actual PDF files inside the 'input' folder.
        # This example cannot create a dummy PDF with specific font structures.
        print("Please place your PDF files in the 'input' folder to process them.")
    
    process_pdfs(input_folder, output_folder)