import fitz  # PyMuPDF
import os
import json
import time
import argparse
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')


def extract_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        sections.append({
            'document': os.path.basename(pdf_path),
            'page_number': page_num,
            'text': text
        })
    return sections


def rank_sections(sections, persona_desc, job_to_be_done):
    query = f"{persona_desc}. Task: {job_to_be_done}"
    query_embedding = model.encode([query])

    for section in sections:
        section_embedding = model.encode([section['text']])
        similarity = cosine_similarity([section_embedding[0]], [query_embedding[0]])[0][0]
        section['similarity'] = similarity

    ranked = sorted(sections, key=lambda x: x['similarity'], reverse=True)
    for idx, sec in enumerate(ranked):
        sec['importance_rank'] = idx + 1
    return ranked[:5]  # top 5


def process_documents(input_folder, persona, job_to_be_done):
    start_time = time.time()
    all_sections = []
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            sections = extract_sections(os.path.join(input_folder, filename))
            all_sections.extend(sections)

    ranked_sections = rank_sections(all_sections, persona, job_to_be_done)

    extracted_sections = []
    subsection_analysis = []

    for s in ranked_sections:
        extracted_sections.append({
            'document': s['document'],
            'section_title': s['text'].split('\n')[0][:80],  # crude title from first line
            'importance_rank': s['importance_rank'],
            'page_number': s['page_number']
        })
        subsection_analysis.append({
            'document': s['document'],
            'refined_text': s['text'][:1000],  # keep first 1000 chars
            'page_number': s['page_number']
        })

    output = {
        'metadata': {
            'input_documents': list(set(s['document'] for s in all_sections)),
            'persona': persona,
            'job_to_be_done': job_to_be_done,
            'processing_timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
        },
        'extracted_sections': extracted_sections,
        'subsection_analysis': subsection_analysis
    }

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection_path", required=True)
    args = parser.parse_args()

    collection_path = args.collection_path
    input_json_path = os.path.join(collection_path, "challenge1b_input.json")
    input_pdf_path = os.path.join(collection_path, "PDFs")
    output_json_path = os.path.join(collection_path, "challenge1b_output.json")

    with open(input_json_path, "r") as f:
        input_data = json.load(f)

    persona = input_data["persona"]["role"]
    job_to_be_done = input_data["job_to_be_done"]["task"]

    output = process_documents(input_pdf_path, persona, job_to_be_done)

    with open(output_json_path, "w") as f:
        json.dump(output, f, indent=4)


