import pandas as pd

# coding: utf-8

# 내가 만든 기능 임포트
from crawling import UrlCrawling, ContentCrawling
from preprocessing import clean, getNouns, getVector
from clustering import addClusterNumber, getClusteredArticle

'''
# 링크 크롤링하는 객체 생성
url_crawler = UrlCrawling()

# six_url = url_crawler.getSixUrl()                          # 6개 카테고리 url
entertainment_url = url_crawler.getEntertainmentUrl()      # 연예 url
# sports_url = url_crawler.getSportsUrl()                    # 스포츠 url
# all_url = six_url + entertainment_url + sports_url         # 전체 url
category = url_crawler.category                            # 카테고리 리스트

# 본문 크롤링하는 객체 생성
content_crawler = ContentCrawling([], [], [])

# content_crawler.getSixContent(six_url)
content_crawler.getEntertainmentContent(entertainment_url)
# content_crawler.getSportsContent(sports_url)

article_df = content_crawler.makeDataFrame(entertainment_url, category)     # 본문 데이터프레임 생성

article_df = getNouns(article_df)                                 # 명사 뽑아서 데이터프레임에 추가

print(article_df)
'''

# 명사까지 추출한 파일 불러오기, 1400개 기사
# test_df는 article_df임

test_df = pd.read_csv("https://raw.githubusercontent.com/Yoon-juhan/naverNewsCrawling/main/article_2.csv")
test_df['nouns'] = test_df['nouns'].apply(lambda x: eval(x))        # 명사 열을 다시 리스트 형식으로 변환
test_df.drop(['Unnamed: 0'], axis=1, inplace=True)  # 파일 불러왔을 때 필요없이 생기는 열 삭제

vector_list = getVector(test_df)         # 카테고리 별로 명사를 벡터화한 리스트

addClusterNumber(test_df, vector_list)   # 군집 번호 열 생성
clustered_article_df, cluster_counts_df = getClusteredArticle(test_df)      # 상위 군집 10개에 해당하는 기사 df, 군집 개수 카운트한 df

print(clustered_article_df)