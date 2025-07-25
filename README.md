# Adobe_Hackathon

# Command for Challenge 1A:
- docker build -f Dockerfile_1A -t pdf_outline_extractor .
- docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" pdf_outline_extractor

# Command for Challenge 1B:
- python Challenge_1b/persona_extractor.py --collection_path Challenge_1b/"Collection 1"
- python Challenge_1b/persona_extractor.py --collection_path Challenge_1b/"Collection 2"
- python Challenge_1b/persona_extractor.py --collection_path Challenge_1b/"Collection 3"
