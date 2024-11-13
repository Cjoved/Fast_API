import requests
import re
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_ner(text):
    doc = nlp(text)
    ner_indices = []
    ner_texts = []

    for ent in doc.ents:
        ner_indices.append(ent.start_char)  # Start index of the entity
        ner_texts.append(ent.text)  # The entity text

    return ner_indices, ner_texts

def check_and_correct_grammar(text):
    url = "https://api.languagetool.org/v2/check"
    params = {
        'text': text,
        'language': 'en-US'
    }
    response = requests.post(url, data=params)
    result = response.json()

    # Create a list of corrections to apply
    corrections = []
    for match in result['matches']:
        start = match['offset']
        length = match['length']
        replacement = match['replacements'][0]['value'] if match['replacements'] else None
        if replacement:
            corrections.append((start, length, replacement))

    # Apply corrections in reverse order to avoid messing up offsets
    for start, length, replacement in sorted(corrections, key=lambda x: x[0], reverse=True):
        text = text[:start] + replacement + text[start + length:]

    return text

def autocorrect_text_by_sentence(text):
    # Extract NER
    ner_indices, ner_texts = extract_ner(text)

    # Replace NER with placeholders
    placeholders = []
    for i, ner in enumerate(ner_texts):
        placeholder = f"<NER{i}>"
        text = text.replace(ner, placeholder)
        placeholders.append(placeholder)

    # Split the text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    # Correct each sentence
    corrected_sentences = [check_and_correct_grammar(sentence) for sentence in sentences]

    # Join the corrected sentences back into a single string
    corrected_text = ' '.join(corrected_sentences)

    # Reinsert NER tags using placeholders
    for placeholder, ner in zip(placeholders, ner_texts):
        corrected_text = corrected_text.replace(placeholder, ner)  # Reinsert NER tag

    return corrected_text

# Example usage
