import sqlite3
from datetime import datetime
import pandas as pd
from flask import g

DATABASE = 'results.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

class DBStorage:
    def __init__(self):
        self.conn = get_db()
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS search_results (
                    query TEXT,
                    rank INTEGER,
                    link TEXT,
                    title TEXT,
                    snippet TEXT,
                    html TEXT,
                    created TEXT
                )
            ''')

    def insert_row(self, row):
        with self.conn:
            self.conn.execute('''
                INSERT INTO search_results (query, rank, link, title, snippet, html, created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['query'], 
                row['rank'], 
                row['link'], 
                row['title'], 
                row['snippet'], 
                row['html'], 
                row['created']
            ))

    def query_results(self, query):
        with self.conn:
            result = self.conn.execute('SELECT * FROM search_results WHERE query = ?', (query,))
            df = pd.DataFrame(result.fetchall(), columns=['query', 'rank', 'link', 'title', 'snippet', 'html', 'created'])
            df['created'] = pd.to_datetime(df['created'])
            return df

    def get_list(self):
        query = "SELECT rank, title, snippet, link FROM search_results ORDER BY rank"
        df = pd.read_sql_query(query, self.conn)
        return df.to_dict(orient='records')

    def update_relevance(self, query, link, relevance_score):
        with self.conn:
            self.conn.execute('''
                UPDATE search_results
                SET rank = rank - ?
                WHERE query = ? AND link = ?
            ''', (relevance_score, query, link))
