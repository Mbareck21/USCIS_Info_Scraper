# app.py

from flask import Flask, render_template, request
from nlp_processor import process_query
from database import create_table, get_db_connection
import scraper 

app = Flask(__name__)

# Create the database table and populate it with scraped data (once, outside the request context)
with app.app_context():
    create_table()
    scraper.scrape_uscis_forms()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    user_query = request.form['query']
    entities = process_query(user_query)
    print("Extracted entities:", entities) 
    response = search_database(entities)
    return response

def search_database(entities):
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Entities received:", entities)
    results = [] # Initialize results to an empty list

    # Prioritize exact matches on form names
    for entity, label in entities:
        if label == "ORG":
            cursor.execute("SELECT * FROM uscis_info WHERE question = ?", (entity,))
            result = cursor.fetchone()

            if result:
                conn.close()
                return format_result(result)

    # If no exact match, perform a keyword-based search
    keywords = [entity for entity, label in entities if label in ["ORG", "GPE"]] 
    if keywords:
        query = "SELECT * FROM uscis_info WHERE " + " OR ".join(["question LIKE ? OR answer LIKE ?" for _ in keywords])
        params = tuple(['%' + keyword + '%' for keyword in keywords] * 2) 
        cursor.execute(query, params)
        results = cursor.fetchall() # Now 'results' is assigned a value

        if results:
            conn.close()
            return format_results(results) 

    # If no exact match or keyword match, try a broader search
    if not results: # This check is now safe
        keywords = [entity for entity, _ in entities] 
        if keywords:
            query = "SELECT * FROM uscis_info WHERE " + " OR ".join(["question LIKE ? OR answer LIKE ?" for _ in keywords])
            params = tuple(['%' + keyword + '%' for keyword in keywords] * 2)
            cursor.execute(query, params)
            results = cursor.fetchall()

    conn.close()

    if results:
        return format_results(results)

    return "I couldn't find any information related to your query. Please try rephrasing or providing more details."

def format_result(result):
    return f"**Form Name:** {result['question']}\n**Description:** {result['answer']}\n**Source:** {result['source_url']}\n\n"

def format_results(results):
    formatted_response = ""
    for result in results:
        formatted_response += format_result(result)
    return formatted_response

if __name__ == '__main__':
    app.run(debug=True)