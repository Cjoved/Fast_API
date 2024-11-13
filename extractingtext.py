# extractingtext.py
from docx import Document
import re

def extract_chapter_content(docx_path, chapter_pattern, next_chapter_pattern, paragraphs_per_page, start_page):
    doc = Document(docx_path)
    extracted_content = ""
    capture = False
    skip_count = 0
    total_paragraphs_to_skip = paragraphs_per_page * (start_page - 1)

    chapter_regex = re.compile(chapter_pattern, re.IGNORECASE)
    next_chapter_regex = re.compile(next_chapter_pattern, re.IGNORECASE)

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        if skip_count < total_paragraphs_to_skip:
            skip_count += 1
            continue

        if chapter_regex.match(text):
            capture = True
            extracted_content += text + "\n"

        if capture:
            if next_chapter_regex.match(text):
                break
            extracted_content += text + "\n"

    return extracted_content.strip()