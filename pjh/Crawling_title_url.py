import requests
from bs4 import BeautifulSoup
import pandas as pd

def job(page_num):
    url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%EC%95%A0%ED%94%8C&start={page_num}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    news_items = soup.select('.news_area')

    news_info = [{'title': item.select_one('.news_tit').get_text(), 'url': item.select_one('.news_tit').get('href')} for item in news_items]
    return news_info

news_info = []
for i in range(1, 101, 10):
    news_info.extend(job(i))

df = pd.DataFrame(news_info)
