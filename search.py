import pandas as pd
from datetime import datetime
from storage import DBStorage
import requests
from requests.exceptions import RequestException
from urllib.parse import quote_plus
from settings import SEARCH_URL, SEARCH_KEY, SEARCH_ID, RESULT_COUNT

def search_api(query, pages=int(RESULT_COUNT/10)):
    results = []
    for i in range(0, pages):
        start = i*10+1
        url = SEARCH_URL.format(
            key=SEARCH_KEY,
            cx=SEARCH_ID,
            query=quote_plus(query),
            start=start
        )
        response = requests.get(url)
        data = response.json()
        results += data["items"]
    res_df = pd.DataFrame.from_dict(results)
    res_df["rank"] = list(range(1, res_df.shape[0] + 1))
    res_df = res_df[["link", "rank", "snippet", "title"]]
    return res_df

def scrape_page(links):
    html = []
    for link in links:
        print(link)
        try:
            data = requests.get(link, timeout=5)
            html.append(data.text)
        except RequestException:
            html.append("")
    return html

def filter_by_platform_and_date(results, platform, start_date, end_date):
    if platform:
        results = results[results['link'].str.contains(platform, case=False)]
    if start_date:
        start_date = pd.to_datetime(start_date)
        results = results[results['created'] >= start_date]
    if end_date:
        end_date = pd.to_datetime(end_date)
        results = results[results['created'] <= end_date]
    return results

def search(query, platform=None, start_date=None, end_date=None):
    columns = ["query", "rank", "link", "title", "snippet", "html", "created"]
    storage = DBStorage()

    stored_results = storage.query_results(query)
    if stored_results.shape[0] > 0:
        stored_results["created"] = pd.to_datetime(stored_results["created"])
        stored_results["rank"] = pd.to_numeric(stored_results["rank"], errors='coerce')
        stored_results = filter_by_platform_and_date(stored_results, platform, start_date, end_date)
        return stored_results[columns]

    print("No results in database. Using the API.")
    results = search_api(query)
    html = scrape_page(results["link"])
    results["html"] = html
    results = results[results["html"].str.len() > 0].copy()
    results["query"] = query
    results["created"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    results["rank"] = pd.to_numeric(results["rank"], errors='coerce')
    results = results[columns]
    results.apply(lambda x: storage.insert_row(x), axis=1)
    print(f"Inserted {results.shape[0]} records.")
    results = filter_by_platform_and_date(results, platform, start_date, end_date)
    return results
