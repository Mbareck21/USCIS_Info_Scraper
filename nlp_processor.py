# nlp_processor.py

import spacy

nlp = spacy.load("en_core_web_md") 

def process_query(query):
    """Processes a user query using SpaCy's NLP pipeline and extracts named entities."""

    doc = nlp(query)

    entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ["ORG", "GPE", "LAW", "PERSON"]] 

    if not entities:
        keywords = [token.text for token in doc if token.is_stop == False and token.is_punct == False]
        entities = [(keyword, "KEYWORD") for keyword in keywords]

    return entities