# app.py

from flask import Flask, render_template, request
from nlp_processor import process_query
from database import create_table, get_db_connection
import scraper

app = Flask(__name__)

# Create the database table and populate it with scraped data
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
    response = search_database(user_query, entities)
    return response

def search_database(user_query, entities):
    conn = get_db_connection()
    cursor = conn.cursor()
    results = []


    # 1. Prioritize exact matches on form names (if entities are found)
    if entities:
        for entity, label in entities:
            if label == "ORG":
                cursor.execute("SELECT * FROM uscis_info WHERE question = ?", (entity,))
                result = cursor.fetchone()
                if result:
                    conn.close()
                    return format_result(result)

    # 2. Keyword-based search (if no exact match or no entities)
    keywords = user_query.split()  # Use the entire query as keywords if no entities
    if keywords:
        query = "SELECT * FROM uscis_info WHERE " + " OR ".join(["question LIKE ? OR answer LIKE ?" for _ in keywords])
        params = tuple(['%' + keyword + '%' for keyword in keywords] * 2) 
        cursor.execute(query, params)
        results = cursor.fetchall()

        if results:
            conn.close()
            return format_results(results)

    # 3. Category-based suggestions (if no keyword matches)
    if not results:
        categories = ["Employment Authorization", "Green Cards", "Citizenship"]
        category_prompt = "Please select a category:\n" + "\n".join([f"{i+1}. {category}" for i, category in enumerate(categories)]) + "\n"
        conn.close()
        return category_prompt 

    conn.close()
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