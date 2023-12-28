import pandas as pd
import schedule
import time
# coding: utf-8

# 만든 기능 임포트
from crawling import UrlCrawling, ContentCrawling
from preprocessing import Preprocessing
from clustering import Clustering
from summary import Summary
from remove import Remove
from database import insert, select
from tts import tts

def start():
    # url 크롤링
    url_crawler = UrlCrawling()                                     # 기사 링크 크롤링 객체

    six_url_df = url_crawler.getSixUrl()                            # 6개 카테고리 (카테고리, url 데이터프레임)
    entertainment_url_df = url_crawler.getEntertainmentUrl()        # 연예 (카테고리, url 데이터프레임)
    sports_url_df = url_crawler.getSportsUrl()                      # 스포츠 (카테고리, url 데이터프레임)

    six_url_df, entertainment_url_df, sports_url_df = Remove.duplication(six_url_df, entertainment_url_df, sports_url_df)   # 이미 요약한 기사 제거

    # 본문 크롤링
    six_url, entertainment_url, sports_url = list(six_url_df['six_url']), list(entertainment_url_df['entertainment_url']), list(sports_url_df['sports_url'])
    all_url = six_url + entertainment_url + sports_url      # 전체 url
    category = list(six_url_df['category']) + list(entertainment_url_df['category']) + list(sports_url_df['category'])

    content_crawler = ContentCrawling()                           # 기사 크롤링 객체

    content_crawler.getSixContent(six_url)                                          # 6개 카테고리 기사 크롤링
    content_crawler.getEntertainmentContent(entertainment_url)                      # 연예 기사 크롤링
    content_crawler.getSportsContent(sports_url)                                    # 스포츠 기사 크롤링

    news_df = content_crawler.makeDataFrame(all_url, category)                   # 본문 데이터프레임 생성

    Remove.photoNews(news_df)                                                    # 포토 기사 삭제

    Preprocessing.getNouns(news_df)                                              # 명사 추출

    Remove.englishNews(news_df)                                                  # 영어 기사 삭제

    vector_list = Preprocessing.getVector(news_df)                               # 명사 벡터화

    Clustering.addClusterNumber(news_df, vector_list)                            # 군집 번호 열 생성
    cluster_counts_df = Clustering.getClusteredArticle(news_df)                  # 군집 개수 카운트한 df

    summary_article = Summary.getSummaryArticle(news_df, cluster_counts_df)      # 요약한 기사 데이터 프레임 반환
    Preprocessing.convertCategory(summary_article)

    # tts(summary_article)
    del summary_article['naver_summary']
    del summary_article['similarity']

    insert(summary_article.values.tolist())

start()

# n분 마다 호출  
# schedule.every(2).minutes.do(start)

# n시간마다 호출  
# schedule.every(1).hour.do(start)

# while True:
#     schedule.run_pending()
#     time.sleep(1)