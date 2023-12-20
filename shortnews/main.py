import pandas as pd
import schedule
import time
# coding: utf-8

# 만든 기능 임포트
from crawling import UrlCrawling, ContentCrawling
from preprocessing import Preprocessing
from clustering import Clustering
from summary import Summary
from database import insert, select
from tts import tts

def start():
    # 링크 크롤링하는 객체 생성
    url_crawler = UrlCrawling()

    six_url = url_crawler.getSixUrl()                          # 6개 카테고리 url
    entertainment_url = url_crawler.getEntertainmentUrl()      # 연예 url
    sports_url = url_crawler.getSportsUrl()                    # 스포츠 url
    all_url = six_url + entertainment_url + sports_url        # 전체 url
    category = url_crawler.category                            # 카테고리 리스트

    # 본문 크롤링하는 객체 생성
    content_crawler = ContentCrawling([], [], [], [], [])

    content_crawler.getSixContent(six_url)
    content_crawler.getEntertainmentContent(entertainment_url)
    content_crawler.getSportsContent(sports_url)

    article_df = content_crawler.makeDataFrame(all_url, category)                   # 본문 데이터프레임 생성

    article_df = Preprocessing.getNouns(article_df)                                 # 명사 추출

    Preprocessing.removeEnglishArticle(article_df)                                  # 영어 기사 삭제

    vector_list = Preprocessing.getVector(article_df)                               # 명사 벡터화

    Clustering.addClusterNumber(article_df, vector_list)                            # 군집 번호 열 생성
    cluster_counts_df = Clustering.getClusteredArticle(article_df)                  # 군집 개수 카운트한 df

    summary_article = Summary.getSummaryArticle(article_df, cluster_counts_df)              # 요약한 기사 데이터 프레임 반환

    # tts(summary_article)

    insert(summary_article.values.tolist())

start()

# schedule.every(2).minutes.do(start)

# while True:
#     schedule.run_pending()
#     time.sleep(1)




"""
# csv 파일로 테스트

test_df = pd.read_csv("article.csv")
test_df['nouns'] = test_df['nouns'].apply(lambda x: eval(x))        # 명사 열을 다시 리스트 형식으로 변환

vector_list = getVector(test_df)         # 카테고리 별로 명사를 벡터화한 리스트

addClusterNumber(test_df, vector_list)   # 군집 번호 열 생성
cluster_counts_df = getClusteredArticle(test_df)      # 상위 군집 10개에 해당하는 기사 df, 군집 개수 카운트한 df

summary_article = getSummaryArticle(test_df, cluster_counts_df)     # 요약한 기사 데이터 프레임 반환

# print(summary_article)

# insert(summary_article.values.tolist())

"""