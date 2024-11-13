from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
import re
from transformers import BartForConditionalGeneration, BartTokenizer

tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
nltk.download('punkt')

model_namebart = "facebook/bart-large-cnn"
tokenizer_bart = BartTokenizer.from_pretrained(model_namebart)
modelbart= BartForConditionalGeneration.from_pretrained(model_namebart)

def generate_sentence_embeddings(sentences, tokenizer, model, max_length=512):
    sentence_embeddings = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt", truncation=True, padding=True, max_length=max_length)
        with torch.no_grad():
            outputs = model(**inputs)
        sentence_embedding = outputs.last_hidden_state[:, 0, :].numpy()
        sentence_embeddings.append(sentence_embedding)
    return np.vstack(sentence_embeddings)

def count_words(text):
    return len(text.split())

def hybrid_extractive_summary(text, target_sentences=5, min_words=500, max_words=700):
    sentences = sent_tokenize(text)
    sentence_embeddings = generate_sentence_embeddings(sentences, tokenizer, model)
    similarity_matrix = cosine_similarity(sentence_embeddings)

    ranked_indices = np.argsort(-similarity_matrix.sum(axis=1))

    summary_sentences = []
    current_word_count = 0

    for idx in ranked_indices:
        if len(summary_sentences) >= target_sentences and current_word_count >= min_words:
            break

        sentence = sentences[idx]
        sentence_word_count = count_words(sentence)

        if current_word_count + sentence_word_count <= max_words:
            summary_sentences.append(sentence)
            current_word_count += sentence_word_count

    if current_word_count < min_words:
        remaining_indices = [idx for idx in ranked_indices if sentences[idx] not in summary_sentences]

        for idx in remaining_indices:
            sentence = sentences[idx]
            sentence_word_count = count_words(sentence)

            if current_word_count + sentence_word_count <= max_words:
                summary_sentences.append(sentence)
                current_word_count += sentence_word_count

            if current_word_count >= min_words:
                break

    while current_word_count > max_words and len(summary_sentences) > 1:
        removed_sentence = summary_sentences.pop()
        current_word_count -= count_words(removed_sentence)

    summary = ' '.join(summary_sentences)

    stats = {
        'num_sentences ': len(summary_sentences),
        'word_count': current_word_count,
        'original_sentences': len(sentences),
        'original_words': count_words(text)
    }

    return summary, stats

def generate_research_summary(text, model_name=model_namebart, max_length=150, min_length=50,
                              length_penalty=2.0, num_beams=4, no_repeat_ngram_size=2,
                              do_sample=False, top_k=50, top_p=0.95, temperature=0.9):

    # Load the pre-trained BART model and tokenizer
    tokenizer = tokenizer_bart
    model = modelbart

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)

    # Generate summary
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        length_penalty=length_penalty,
        num_beams=num_beams,
        early_stopping=True,
        no_repeat_ngram_size=no_repeat_ngram_size,
        do_sample=do_sample,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature
    )

    # Decode the summary
    abstractivesummary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return abstractivesummary




