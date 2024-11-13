import re

def rank_and_print_paragraphs_from_text(text, top_n=7):
    """
    Rank paragraphs based on their length (number of words) from a block of text and print them.

    Args:
        text (str): A block of text containing multiple paragraphs.
    """
    # Split the text into paragraphs based on newline characters
    paragraphs = text.strip().split('\n\n')

    # Create a list of tuples (index, paragraph, length)
    paragraph_lengths = [(index, paragraph, len(paragraph.split()))
                         for index, paragraph in enumerate(paragraphs) if paragraph.strip()]

    # Sort paragraphs by length (longest first)
    ranked_paragraphs = sorted(paragraph_lengths, key=lambda x: x[2], reverse=True)

    # Create a list to hold the original indices of the top ranked paragraphs
    top_paragraphs = ranked_paragraphs[:top_n]

    # Create a list to hold the paragraphs in their original order
    original_order = [None] * len(paragraphs)

    # Place the top paragraphs back in their original indices
    for index, paragraph, length in top_paragraphs:
        original_order[index] = (paragraph, length)

    # Print the paragraphs in their original order
    print(f"Top {top_n} Ranked Paragraphs in Original Order:")
    for i, item in enumerate(original_order):
        if item is not None:
            paragraph, length = item
            print(f"Original Index: {i} | {paragraph} (Length: {length} words)")

    if ranked_paragraphs:
        return ranked_paragraphs[0][1]  # Return the paragraph text of the longest paragraph
    else:
        return ""

#Function for getting the authors
def extract_authors_and_contributions(document):
    author_contributions = {}
    pattern = r'(\w+\s\w+)\s\((\d{4})\):\s(.+)'
    matches = re.findall(pattern, document)
    for author, year, contribution in matches:
        author_contributions[author] = f"{contribution} ({year})"
    return author_contributions
