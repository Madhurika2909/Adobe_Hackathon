
# Adobe India Hackathon 2025

## "Connecting the Dots" Challenge

### [Challenge 1a: PDF Structure Extraction Engine](./Challenge_1a/README.md)

This challenge focuses on **structured extraction** from raw PDF documents:

- Hierarchical **headings** (H1, H2, H3)
- An intelligently **inferred title**
- A JSON-based **document outline**
- All of this, driven by smart font-size heuristics, regular expressions, and similarity-based de-duplication

---

### ⚙️ Prerequisites & Run Instructions

Make sure you have **Docker** installed and running in background . Then run:

```bash
# Build the Docker container
docker build -f Dockerfile_1A -t pdf_outline_extractor .

# Run the extractor (input PDFs should be in ./input, results saved in ./output)
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" pdf_outline_extractor

```

## 📁 Folder Structure

```text
Challenge_1a/
├── Dockerfile_1A
├── pdf_outline_extractor.py
├── input/
│   └── file.pdf
├── output/
│   └── file.json
├── README.md

```


## Methodology:
---
The goal of this challenge is to parse a PDF document and reconstruct its logical structure by extracting its title and hierarchical headings (e.g., H1, H2, H3). The solution employs a rule-based structural analysis approach, which is highly efficient and operates without machine learning models or internet access.

The solution uses the PyMuPDF library to deconstruct the PDF into text "spans", which include:
- Text content
- Font size
- Font name
- Coordinates on the page

### Extraction Process (Heuristic Strategy)

### 1. Title Detection
- Identify the text with the *largest font size* on the first few pages.
- Filter out common non-title elements (e.g., "Page 1", "Copyright").
- Fallback: use the *document filename* if no clear title is found.

### 2. Heading Identification
A combination of techniques is used:
- *Pattern Matching*: Search for numbered headings (e.g., "2.1.3 Section Title") and keywords like "Introduction", "Conclusion", etc.
- *Font Size Analysis*: Calculate dynamic thresholds for H1, H2, and H3 using max and average font sizes.
- *Style Filtering*: Ensure heading candidates follow title-like formatting (e.g., "Title Case", "ALL CAPS").

### Deduplication and Ordering
- Use *Levenshtein distance* to eliminate repeated headers/footers.
- Sort headings by:
  - Page number
  - Vertical position on the page

>  Lightweight solution, runs efficiently on a *single CPU core* with minimal memory.

---


## Sample File01 Output :
<img width="827" height="343" alt="Image" src="https://github.com/user-attachments/assets/3272fa06-2d64-4d07-955f-143a6c190f3d" />





### [Challenge 1b: Persona Extractor from Multiple Document Collections](./Challenge_1b/README.md)

This challenge focuses on **persona extraction** from diverse document collections:

- Input grouped into **Collection 1**, **Collection 2**, and **Collection 3**
- Intelligent identification of **user personas**
- Extraction of **themes**, **interests**, and **entity patterns**
- Output in structured **JSON format**
- Powered by NLP techniques, keyword analysis, and frequency heuristics

---

### ⚙️ Prerequisites & Run Instructions

Make sure you have **Docker** installed and running in background. Then run:

```bash
- pip install scikit-learn
- python -m pip install sentence-transformers
- python Challenge_1b/persona_extractor.py --collection_path Challenge_1b/"Collection 1"
- python Challenge_1b/persona_extractor.py --collection_path Challenge_1b/"Collection 2"
- python Challenge_1b/persona_extractor.py --collection_path Challenge_1b/"Collection 3"

```

## 📁 Folder Structure

```text
Challenge_1b/
├── Collections
│   └── PDFs
│   └── Challenge1b_input.json
│   └── Challenge1b_output.json
├── persona_extractor.py
├── Dockerfile_1B


```
## Methodology:
This challenge focuses on identifying the *most relevant sections* from a collection of PDFs based on a user's query (persona + task). The solution uses *semantic search* to understand meaning rather than just keyword matches.

### Technical Approach

### Model Selection
- Model used: all-MiniLM-L6-v2 from sentence-transformers
- Optimized for semantic similarity tasks
- Lightweight (~80MB) and within the 200MB limit

### Document Processing
- Process each PDF *page by page*
- Treat each page as a *self-contained chunk*

### Embedding Generation
- Combine *persona + task* into a single *query string*
- Use the model to generate an *embedding vector* for:
  - The user query
  - Each page in the document set

### Relevance Ranking
- Use *cosine similarity* between query and page embeddings
- Rank based on *contextual alignment*
- Select *top 5 pages* with the highest similarity scores

### Output Format
- Final output is a *JSON file* with:
  - Ranked list of pages
  - Source document
  - Page number
  - Text snippet for context

>  Fully offline, CPU-based semantic analysis completes within *10 seconds*

---

## Sample Collection 1 Input:

```bash
"persona": {
        "role": "Tourist"
    },
    "job_to_be_done": {
        "task": "I am a tourist, suggest me the History of South of France"
    }
```

## Sample Collection 1 Output:

```bash
"subsection_analysis": [
        {
            "document": "South of France - History.pdf",
            "refined_text": "A Historical Journey Through the South of France \nIntroduction \nThe South of France, renowned for its picturesque landscapes, charming villages, and \nstunning coastline, is also steeped in history. From ancient Roman ruins to medieval \nfortresses and Renaissance architecture, this region o\ufb00ers a fascinating glimpse into the past. \nThis guide will take you through the histories of major cities, famous historical sites, and other \npoints of interest to help you plan an enriching and unforgettable trip. \n \n \n",
            "page_number": 1
        },
        {
            "document": "South of France - History.pdf",
            "refined_text": "Conclusion \nThe South of France o\ufb00ers a rich tapestry of history, culture, and architecture that is sure to \ncaptivate any traveler. From the ancient Roman ruins of N\u00eemes and Arles to the medieval \nfortresses of Carcassonne and Avignon, each city and town has its own unique story to tell. \nWhether you're exploring the vibrant streets of Marseille, the elegant boulevards of Aix-en-\nProvence, or the charming squares of Montpellier, you'll find a wealth of historical treasures \nwaiting to be discovered. Use this guide to plan your journey through the South of France and \nimmerse yourself in the fascinating history of this beautiful region. \n \n",
            "page_number": 12
        },
```
###  Team:


```text
Team Name:3bits
Team leader: Khushi singh Tanwar
Team Member1: Madhurika Priya
Team member2: Pushpa kumari Pandey

```
