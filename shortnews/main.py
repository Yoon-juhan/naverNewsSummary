import pandas as pd

# coding: utf-8
from gensim.summarization.summarizer import summarize


# 내가 만든 기능 임포트
from crawling import UrlCrawling, ContentCrawling
from preprocessing import clean, getNouns, getVector
from clustering import getClusteredArticle

'''
# 링크 크롤링하는 객체 생성
url_crawler = UrlCrawling([], [], [], [], ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"])
# url_crawler.getSixLink()
url_crawler.getEntertainmentLink()
# url_crawler.getSportsLink()

# 본문 크롤링하는 객체 생성
content_crawler = ContentCrawling([], [], [])
# content_crawler.getSixContent(url_crawler.six_url)
content_crawler.getEntertainmentContent(url_crawler.entertainment_url)
# content_crawler.getSportsContent(url_crawler.sports_url)

article_df = content_crawler.makeDataFrame(url_crawler)     # 본문 데이터프레임 생성

article_df = getNouns(article_df)                           # 명사 뽑아서 데이터프레임에 추가

print(article_df)
'''

# 명사까지 추출한 파일 불러오기, 1400개 기사

test_df = pd.read_csv("https://raw.githubusercontent.com/Yoon-juhan/naverNewsCrawling/main/article_2.csv")
test_df['nouns'] = test_df['nouns'].apply(lambda x: eval(x))        # 명사 열을 다시 리스트 형식으로 변환
test_df.drop(['Unnamed: 0'], axis=1, inplace=True)  # 파일 불러왔을 때 필요없이 생기는 열 삭제

vector_list = getVector(test_df)    # 명사를 벡터화한 리스트

getClusteredArticle(test_df, vector_list)