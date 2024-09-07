# scraper.py

import requests
from bs4 import BeautifulSoup
from database import get_db_connection
import sqlite3


def scrape_uscis_forms():
    url = 'https://www.uscis.gov/forms/all-forms'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all form rows
    form_rows = soup.find_all('div', class_='views-row')

    conn = get_db_connection() 
    cursor = conn.cursor()

    for row in form_rows:
        # Extract form name
        form_name_element = row.find('div', class_='views-field-title').find('a')
        if form_name_element:
            form_name = form_name_element.text.strip()
        else:
            form_name = "N/A"

        # Extract description
        description_element = row.find('div', class_='views-field-body').find('div')
        if description_element:
            description = description_element.text.strip()
        else:
            description = "N/A"

        try:
            cursor.execute('INSERT INTO uscis_info (question, answer, source_url) VALUES (?, ?, ?)',
                           (form_name, description, url))
        except sqlite3.Error as e:
            print(f"Error inserting data into the database: {e}")
            conn.rollback()

    conn.commit()
    conn.close()

if __name__ == "__main__":
    scrape_uscis_forms()