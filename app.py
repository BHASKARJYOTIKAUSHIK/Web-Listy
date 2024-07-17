from flask import Flask, request, render_template, jsonify, g
import requests
from datetime import datetime
import settings
from filter import Filter
from storage import DBStorage, get_db, close_db
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures

app = Flask(__name__)

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

def fetch_results(query, start_index=1):
    url = settings.SEARCH_URL.format(key=settings.SEARCH_KEY, cx=settings.SEARCH_ID, query=query, start=start_index)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        results = response.json().get('items', [])
        return results
    except requests.exceptions.RequestException as e:
        print(f"Error fetching results: {e}")
        return []

def fetch_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException as e:
        print(f"Error fetching HTML content from {url}: {e}")
    return ""

def fetch_html_content_parallel(links):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_html_content, url): url for url in links}
        html_contents = []
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                html_contents.append((url, future.result()))
            except Exception as e:
                print(f"Error processing future for {url}: {e}")
                html_contents.append((url, ""))
    return html_contents

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    platform = request.form.get('platform')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    code_snippet = request.form.get('code_snippet')
    
    full_query = query
    if platform:
        full_query += f" {platform}"
    if code_snippet:
        full_query += f" {code_snippet}"
    if start_date and end_date:
        full_query += f" daterange:{start_date.replace('-', '')}-{end_date.replace('-', '')}"
    
    results = []
    for start_index in range(1, settings.RESULT_COUNT + 1, 10):
        batch_results = fetch_results(full_query, start_index)
        results.extend(batch_results)
    
    if not results:
        return render_template('result.html', query=query, results=[])

    results = results[:settings.RESULT_COUNT]
    links = [result['link'] for result in results]
    html_contents = fetch_html_content_parallel(links)

    ranked_results = []
    for i, (link, html_content) in enumerate(html_contents):
        for result in results:
            if result['link'] == link:
                ranked_results.append({
                    'query': query,
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
