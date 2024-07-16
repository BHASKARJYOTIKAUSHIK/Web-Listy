from flask import Flask, request, render_template, jsonify, g
import requests
from datetime import datetime
import settings
from filter import Filter
from storage import DBStorage, get_db, close_db
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

def fetch_results(query, start_index=1):
    url = settings.SEARCH_URL.format(key=settings.SEARCH_KEY, cx=settings.SEARCH_ID, query=query, start=start_index)
    response = requests.get(url)
    results = response.json().get('items', [])
    return results

def fetch_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    platform = request.form['platform']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    code_snippet = request.form['code_snippet']
    
    full_query = query
    if platform:
        full_query += f" {platform}"
    if code_snippet:
        full_query += f" {code_snippet}"
    if start_date and end_date:
        full_query += f" daterange:{start_date.replace('-', '')}-{end_date.replace('-', '')}"
    
    results = []
    for start_index in range(1, settings.RESULT_COUNT, 10):
        results.extend(fetch_results(full_query, start_index))

    results = results[:settings.RESULT_COUNT]
    ranked_results = []
    for i, result in enumerate(results):
        html_content = fetch_html_content(result['link'])
        ranked_results.append({
            'query': query,  # Ensure 'query' key exists
            'rank': i + 1,
            'title': result.get('title', ''),
            'snippet': result.get('snippet', ''),
            'link': result.get('link', ''),
            'html': html_content
        })

    results_df = pd.DataFrame(ranked_results)
    filter_instance = Filter(results_df)
    filtered_results = filter_instance.filter()

    print(filtered_results)  # Debugging: print the filtered results

    storage = DBStorage()
    for _, row in filtered_results.iterrows():
        row_dict = row.to_dict()
        row_dict['created'] = datetime.now().isoformat()
        storage.insert_row(row_dict)

    return render_template('result.html', query=query, results=filtered_results.to_dict(orient='records'))

@app.route('/api/get_list')
def get_list():
    storage = DBStorage()
    list_data = storage.get_list()
    return jsonify(list_data)

@app.route('/relevant', methods=['POST'])
def mark_relevant():
    data = request.json
    query = data['query']
    link = data['link']
    storage = DBStorage()
    storage.update_relevance(query, link, relevance_score=10)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
