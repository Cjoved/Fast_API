from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from extractingtext import extract_chapter_content  # Ensure this function is correctly implemented
from summarization import hybrid_extractive_summary, generate_research_summary  # Ensure these functions are correctly implemented
from grammar import autocorrect_text_by_sentence

app = FastAPI()

# Dictionary to store extracted content per chapter
extracted_content: Dict[int, str] = {}

# Define regex patterns for chapters
chapter_patterns = [
    r"\bCHAPTER\s+I\b",
    r"\bCHAPTER\s+II\b",
    r"\bCHAPTER\s+III\b",
    r"\bCHAPTER\s+IV\b",
    r"\bCHAPTER\s+V\b"
]

@app.get("/extract-all")
async def extract_all_chapters(start_page: int = 10):
    docx_file_path = "C:\\Users\\Crich Joved\\Downloads\\CS1-KASAKA-MANUSCRIPT-ECOPY_2.docx"
    
    extracted_content.clear()  # Clear previous data
    
    for chapter_number in range(1, len(chapter_patterns) + 1):
        chapter_pattern = chapter_patterns[chapter_number - 1]
        next_chapter_pattern = chapter_patterns[chapter_number] if chapter_number < len(chapter_patterns) else r"\bBIBLIOGRAPHY\b"
        
        content = extract_chapter_content(docx_file_path, chapter_pattern, next_chapter_pattern, paragraphs_per_page=10, start_page=start_page)
        extracted_content[chapter_number] = content  # Store extracted content
    
    return {"extracted_content": extracted_content}

class ChapterSummaryRequest(BaseModel):
    chapter_number: int
    target_sentences: Optional[int] = 70
    min_words: Optional[int] = 500
    max_words: Optional[int] = 700


class SummaryRequest(BaseModel):
    chapters: List[ChapterSummaryRequest]  # List of chapter-specific summarization requests

@app.post("/summarize-multiple")
async def summarize_multiple_chapters(request: SummaryRequest):
    summaries = {}
    
    for chapter_request in request.chapters:
        chapter_number = chapter_request.chapter_number
        
        # Retrieve the extracted content using the chapter number
        text = extracted_content.get(chapter_number)
        if not text:
            raise HTTPException(status_code=404, detail=f"Extracted content not found for chapter {chapter_number}.")

        # Generate the summary using the specified parameters
        summary, stats = hybrid_extractive_summary(
            text,
            target_sentences=chapter_request.target_sentences,
            min_words=chapter_request.min_words,
            max_words=chapter_request.max_words
        )
        corrected_summary = autocorrect_text_by_sentence(summary)
        
        # Store the summary in the dictionary
        summaries[chapter_number] = {"summary": corrected_summary, "stats": stats}
    
    return {"summaries": summaries}

class AbstractSummaryRequest(BaseModel):
    chapter_number: int
    max_length: Optional[int] = 400
    min_length: Optional[int] = 150
    length_penalty: Optional[float] = 2.0
    num_beams: Optional[int] = 4
    no_repeat_ngram_size: Optional[int] = 2
    do_sample: Optional[bool] = False
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.95
    temperature: Optional[float] = 0.9

@app.post("/abstract-summary")
async def create_abstract_summary(request: AbstractSummaryRequest):
    try:
        # Retrieve the extracted content using the chapter number
        text = extracted_content.get(request.chapter_number)
        if not text:
            raise HTTPException(status_code=404, detail="Extracted content not found for the specified chapter.")

        summary = generate_research_summary(
            text,
            max_length=request.max_length,
            min_length=request.min_length,
            length_penalty=request.length_penalty,
            num_beams=request.num_beams,
            no_repeat_ngram_size=request.no_repeat_ngram_size,
            do_sample=request.do_sample,
            top_k=request.top_k,
            top_p=request.top_p,
            temperature=request.temperature
        )
        corrected_summary = autocorrect_text_by_sentence(summary)
        return {"summary": corrected_summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating abstract summary: {str(e)}")


