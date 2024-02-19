from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd


# 명사 벡터화 (군집화에 사용)
def getVector(news_df):    # 카테고리 별로 벡터 생성
    category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
    vector_list = []

    for i in range(8):
        try:
            text = [" ".join(noun) for noun in news_df['nouns'][news_df['category'] == category_names[i]]]    # 명사 열을 하나의 리스트에 담는다.
            print(text)
            
            tfidf_vectorizer = TfidfVectorizer(min_df = 2, ngram_range=(1, 5))
            tfidf_vectorizer.fit(text)
            vector = tfidf_vectorizer.transform(text).toarray()                         # vector list 반환
            vector = np.array(vector)
            vector_list.append(vector)
        except:
            index = news_df[news_df['category'] == category_names[i]].index
            news_df.drop(index, inplace=True)

    return vector_list

# 카테고리 별로 군집화
# cluster_number 열에 군집 번호 생성
def addClusterNumber(news_df, vector_list):
    cluster_number_list = []

    for vector in vector_list:
        model = DBSCAN(eps=0.2, min_samples=1, metric='cosine')     # eps = Cluster를 구성하는 최소의 거리, min_samples = Cluster를 구성 시, 필요한 최소 데이터 포인트 수
        result = model.fit_predict(vector)
        cluster_number_list.extend(result)

    news_df['cluster_number'] = cluster_number_list  # 군집 번호 칼럼 추가


def getClusteredNews(news_df): # 카테고리 별로 군집의 개수를 센다.
    category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]

    cluster_counts_df = pd.DataFrame(columns=["category", "cluster_number", "cluster_count"])

    for i in range(8):
        tmp = news_df[news_df['category'] == category_names[i]]['cluster_number'].value_counts().reset_index()
        tmp.columns = ['cluster_number', 'cluster_count']
        tmp['category'] = [category_names[i]] * len(tmp)

        cluster_counts_df = pd.concat([cluster_counts_df, tmp])

    # 상위 군집 10개씩만 추출
    # cluster_counts_df = cluster_counts_df[cluster_counts_df.index < 10]
    cluster_counts_df = cluster_counts_df[cluster_counts_df.index < 20]
    
    return cluster_counts_df
    


def startClustering(news_df):
    vector_list = getVector(news_df)                                     # 명사 벡터화
    addClusterNumber(news_df, vector_list)                               # 군집 번호 열 생성
    cluster_counts_df = getClusteredNews(news_df)                        # 군집 개수 카운트한 df

    return cluster_counts_df