# WebListy - A Mini Search Engine

WebListy is a simple mini search engine that allows users to search the web and get filtered and ranked results. The project uses the Google Custom Search JSON API for fetching search results, applies content and tracker filters, and stores the results in a SQLite database.

## Features

- Search the web using the Google Custom Search API
- Apply content and tracker filters to the search results
- Rank and display the filtered results
- Incremental loading of search results with a "Load More" button
- Mark results as relevant

## Project Steps

1. **Setup a Programmable Search Engine**: Follow the [Custom Search API instructions](https://developers.google.com/custom-search/v1/introduction) to set up your search engine.
   - You can create one [here](https://programmablesearchengine.google.com/controlpanel/all).
2. **Create an API Key**: Generate an API key for your search engine [here](https://console.cloud.google.com/apis/credentials).
3. **Create a Module**: Develop a module to search using the API.
4. **Create a Flask Application**: Set up a Flask application to perform searches and render results.
5. **Filter and Rank Results**: Implement filtering and ranking of the search results.

## Other Setup

You will need to create a programmable search engine and get an API key by following [these directions](https://developers.google.com/custom-search/v1/introduction). You will need a Google account, and as part of this, you may also need to sign up for Google Cloud.

## Additional Files

You'll need to download a list of ad and tracker URLs from [here](https://raw.githubusercontent.com/notracking/hosts-blocklists/master/dnscrypt-proxy/dnscrypt-proxy.blacklist.txt). We'll use this to filter out bad domains. Save it as `blacklist.txt`.

## Requirements

- Python 3.6+
- Flask
- Requests
- BeautifulSoup4
- Pandas
- aiohttp

## install the required dependencies:

- Python 3.9+
- Required Python packages (pip install -r requirements.txt)

## Run
- Run the project with:

* `pip install -r requirements.txt`
* `flask --debug run --port 5001`
-Open your web browser and go to http://127.0.0.1:5001.
