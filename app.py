from flask import Flask, request, render_template, jsonify, session, redirect, url_for, flash
import requests
import asyncio
import aiohttp
import settings
from filter import Filter
from storage import DBStorage, close_db
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

async def fetch_html_content_parallel(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def fetch_results(query, start_index=1):
    if not query:
        return []
    
    url = settings.SEARCH_URL.format(key=settings.SEARCH_KEY, cx=settings.SEARCH_ID, query=query, start=start_index)
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError for bad responses
    return response.json().get('items', [])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].strip()
    platform = request.form.get('platform')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    code_snippet = request.form.get('code_snippet')
    reset = request.form.get('reset')

    if not query:
        flash("Query cannot be empty.")
        return redirect(url_for('index'))

    if reset == '1':
        session['page'] = 1
    else:
        session['page'] = session.get('page', 1) + 1

    full_query = query
    if platform:
        full_query += f" {platform}"
    if code_snippet:
        full_query += f" {code_snippet}"
    if start_date and end_date:
        full_query += f" daterange:{start_date.replace('-', '')}-{end_date.replace('-', '')}"

    batch_size = 100
    results = []
    for i in range(0, settings.RESULT_COUNT, batch_size):
        batch_results = fetch_results(full_query, start_index=i + 1 + (session['page'] - 1) * settings.RESULT_COUNT)
        results.extend(batch_results)
    
    if not results:
        return render_template('result.html', query=query, results=[])

    results = results[:settings.RESULT_COUNT]
    links = [result['link'] for result in results]
    html_contents = asyncio.run(fetch_html_content_parallel(links))

    ranked_results = []
    for i, html_content in enumerate(html_contents):
        ranked_results.append({
            'query': query,
            'rank': i + 1,
            'title': results[i].get('title', ''),
            'snippet': results[i].get('snippet', ''),
            'link': results[i].get('link', ''),
            'html': html_content
        })

    results_df = pd.DataFrame(ranked_results)
    filter_instance = Filter(results_df)
    filtered_results = filter_instance.filter()

    storage = DBStorage()
    for _, row in filtered_results.iterrows():
        row_dict = row.to_dict()
        row_dict['created'] = datetime.now().isoformat()
        storage.insert_row(row_dict)

    return render_template('result.html', query=query, results=filtered_results.to_dict(orient='records'), platform=platform, start_date=start_date, end_date=end_date, code_snippet=code_snippet)

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
