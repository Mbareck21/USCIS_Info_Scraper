import spacy

# Load a larger model for potentially better entity recognition
nlp = spacy.load("en_core_web_md") 

def process_query(query):
    """Processes a user query using SpaCy's NLP pipeline and extracts named entities."""

    doc = nlp(query)

    # Extract entities with relevant labels (expand as needed)
    entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ["ORG", "GPE", "LAW", "PERSON"]] 

    # If no entities are found, consider extracting keywords or noun chunks
    if not entities:
        keywords = [token.text for token in doc if token.is_stop == False and token.is_punct == False]
        entities = [(keyword, "KEYWORD") for keyword in keywords]

    return entities