from sklearn.cluster import DBSCAN
import pandas as pd

# 카테고리 별로 군집화
# cluster_number 열에 군집 번호 생성

def getClusteredArticle(df, vector_list):
    category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
    cluster_number_list = []

    for vector in vector_list:
        model = DBSCAN(eps=0.1, min_samples=1, metric='cosine')
        result = model.fit_predict(vector)
        cluster_number_list.extend(result)

    df['cluster_number'] = cluster_number_list

    # 카테고리 별로 군집의 개수를 센다.
    # 코드 수정하기

    cluster_counts_df = pd.DataFrame({'category' : [""],
                                    'cluster_number' : [0],
                                    'cluster_count' : [0]})

    for i in range(7):
        t = df[df['category'] == category_names[i]]['cluster_number'].value_counts().reset_index()
        t.columns = ['cluster_number', 'cluster_count']
        t['category'] = [category_names[i]] * len(t)

        cluster_counts_df = pd.concat([cluster_counts_df, t])

    cluster_counts_df = cluster_counts_df[cluster_counts_df['cluster_count'] != 0]