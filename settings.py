SEARCH_KEY = "AIzaSyAiiFMaNAIZ__G6r4RJ-K7RkSvGwktugL4"
SEARCH_ID = "77f1876f51e5948c2"
COUNTRY = "us"
SEARCH_URL = "https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={query}&start={start}&num=10&gl=" + COUNTRY
RESULT_COUNT = 20

import os
if os.path.exists("private.py"):
    from private import *