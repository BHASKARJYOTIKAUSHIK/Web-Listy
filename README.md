# WebListy - A Mini Search Engine

WebListy is a simple mini search engine that allows users to search the web and get filtered and ranked results. The project uses the Google Custom Search JSON API for fetching search results, applies content and tracker filters, and stores the results in a SQLite database.

## Features

- Search the web using the Google Custom Search API
- Apply content and tracker filters to the search results
- Rank and display the filtered results
- Incremental loading of search results with a "Load More" button
- Mark results as relevant


## Requirements

- Python 3.6+
- Flask
- Requests
- BeautifulSoup4
- Pandas
- aiohttp

# install the required dependencies:

Python 3.9+
Required Python packages (pip install -r requirements.txt)

## Run
Run the project with:

flask --debug run --port 5001

