
### 애플 주가 정보 + 3대 지수 정보 2년치 긁어오는 코드입니다. ###
import pymysql
import schedule
import time
import yfinance as yf
from datetime import datetime

# MySQL 연결 설정 - 승엽님은 빅쿼리니까 맞춰서 변경하시면 됩니다.
conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='yfdb', charset='utf8')

# 애플 주식 정보와 주요 지수를 가져오는 함수
def fetch_data():
    # 애플 주식 정보 가져오기
    apple_stock = yf.Ticker("AAPL")
    apple_df = apple_stock.history(period="2y") # 최근 2년치 정보 가져오기 (알아서 조정)
    apple_df.reset_index(inplace=True)
    apple_df.drop(columns=['Dividends','Stock Splits'], inplace=True)

    # 주요 지수 가져오기
    indices = ['^DJI', '^IXIC', '^GSPC']  # 다우존스, 나스닥, S&P 500
    indices_df = yf.download(indices, period="2y")['Close'] # 종가 정보만 가져오기
    indices_df.reset_index(inplace=True) 
    indices_df.columns = ['Date', 'DJI_Close', 'IXIC_Close', 'GSPC_Close'] 

    return apple_df, indices_df


def store_data(df, table_name):
    cursor = conn.cursor()

    for i, row in df.iterrows():
       
        escaped_values = ["'" + conn.escape_string(str(value)) + "'" for value in row]
        sql = f"INSERT INTO {table_name} VALUES ({', '.join(escaped_values)})"
        cursor.execute(sql)

    conn.commit()


def job():
    apple_df, indices_df = fetch_data()

  
    store_data(apple_df, 'apple_stock')
    store_data(indices_df, 'indices')
job()
------------------------------------------------------------------------------------------------------------------------
### 네이버 뉴스 페이지에서 10페이지 분량의 기사 타이틀을 긁어오는 코드입니다. ###
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import pymysql
from konlpy.tag import Okt

# MySQL 연결 설정
conn = pymysql.connect(
    host='127.0.0.1',  
    user='root',       
    password='1234',
    db='yfdb',      
    charset='utf8'     
)
cursor = conn.cursor()

# Okt 객체 생성 형태소 분리 해주는 녀석
okt = Okt()

# 불용어 리스트 생성 <- 이 전처리 과정이 없으면 쓰잘데기 없는 단어들이 많이 추출됩니다. 시각화하면 지저분함
stopwords = ['막', '첫', '뭔', '은', '는', '이', '가', '을', '를', '와', '과', 
             '있', '없', '아니', '것', '들', '그', '되', '수', '이', '보', '않', 
             '없', '나', '사람', '주', '아니', '등', '같', '우리', '때', '년', '가', 
             '한', '지', '대하', '오', '말', '일', '그렇', '위하', '때문', '그것', '두', 
             '말하', '알', '그러나', '받', '못하', '일', '그런', '또', '문제', '더', 
             '사회', '많', '그리고', '좋', '크', '따르', '중', '나오', '가지', '씨', 
             '시키', '만들', '지금', '생각하', '그러', '속', '하나', '집', '살', '모르', 
             '적', '월', '데', '자신', '안', '어떤', '내', '내', '경우', '명', '생각', 
             '시간', '그녀', '다시', '이런', '앞', '보이', '번', '나', '다른', '어떻', 
             '여자', '개', '전', '들', '사실', '이렇', '점', '싶', '말', '정도', '좀', 
             '원', '잘', '통하', '소리', '놓']

# 뉴스 타이틀 긁어와주는 코드
def job(page_num):
    url = f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query=%EC%95%A0%ED%94%8C={page_num}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    news_titles = soup.select('.news_tit')

    titles = [title.get_text() for title in news_titles]
    return titles

news_titles = []
for i in range(1, 101, 10):
    news_titles.extend(job(i))

df = pd.DataFrame(news_titles, columns=['title'])

words = []
for title in df['title']:
    # 형태소 분리
    temp = okt.morphs(title)
    # 불용어 제거
    temp = [word for word in temp if word not in stopwords and len(word) > 1]
    words.extend(temp)

# 카운터 라이브러리 이용해서 단어 카운트
counter = Counter(words)

word_counts = pd.DataFrame.from_dict(counter, orient='index').reset_index()

# MySQL에 데이터 저장 - 이 부분도 사용하신다면 빅쿼리에 맞게 수정하시면 됩니다.
for row in word_counts.itertuples():
    word = row[1]
    count = row[2]
    sql = "INSERT INTO word_counts (word, count) VALUES (%s, %s)"
    cursor.execute(sql, (word, count))

# MySQL에 변경사항 반영
conn.commit()




