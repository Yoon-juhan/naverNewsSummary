import pandas as pd
import re
from tqdm.notebook import tqdm
from summa.summarizer import summarize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bareunpy import Tagger
from bareunpy_api_key import key

def summary(news_df, cluster_counts_df):
    summary_news = pd.DataFrame()
    
    for i in tqdm(range(len(cluster_counts_df)), desc="요약"):
        category_name, cluster_number = cluster_counts_df.iloc[i, 0:2]    # 카테고리 이름, 군집 번호

        # 군집내 기사들 df
        temp_df = news_df[(news_df['category'] == category_name) & (news_df['cluster_number'] == cluster_number)]

        # 카테고리
        category = temp_df["category"].iloc[0]

        # 뉴스 제목
        title = cleanTitle(temp_df["title"].iloc[0])

        # 본문 요약
        summary_content = multiDocumentSummarization(temp_df["content"])

        # 링크
        url = ",".join(list(temp_df["url"]))

        # 이미지
        img = list(temp_df["img"])
        if any(img):
            img = ",".join(list(temp_df["img"]))        
        else:
            img = ""
        
        # 키워드
        keyword = getKeyword(title + " " +  summary_content)
            
        # 데이터프레임 생성
        summary_news = summary_news.append({
            "category" : category,
            "title" : title,
            "content" : summary_content,
            "img" : img,
            "url" : url,
            "keyword" : keyword
        }, ignore_index=True)

    summary_news.drop(summary_news[summary_news.content == ""].index, inplace=True)
    
    return summary_news


def multiDocumentSummarization(content):

    # 군집된 기사들을 하나의 문서로 합치고 문장 단위로 나눈다.
    sentence_list = "\n".join(content)
    sentence_list = sentence_list.split("다.\n")
    if sentence_list[-1] == "":
        sentence_list.pop()

    # split 할 때 사라진 '다.' 를 다시 붙여준다.
    sentence_list = [sentence + "다." for sentence in sentence_list if sentence[-2:] != "다."]

    # 문장간 유사도 측정
    idx = []
    n = 60
    for i in range(len(sentence_list)):
        for j in range(i+1, len(sentence_list)):
            cosine_similarity = cosine(sentence_list[i], sentence_list[j])
            jaccard_similarity = jaccard(sentence_list[i], sentence_list[j])
            if cosine_similarity >= n or jaccard_similarity >= n:
                idx.append(j)
    
    content = []
    for i, sentence in enumerate(sentence_list):
        if i not in idx:
            content.append(sentence)

    content = "\n".join(content)
    summary_content = summarize(content, words=60) # 단어 수
    summary_content = re.sub('다\.\n', '다.\n\n', summary_content)

    return summary_content


# 코사인 유사도
def cosine(x, y):
    data = (x, y)
    try:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(data)
        similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
    except:
        return 0
    return round(similarity[0][0] * 100, 2)


# 자카드 유사도
def jaccard(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    similarity = intersection_cardinality / float(union_cardinality)

    return round(similarity * 100, 2)


# 제목 전처리
def cleanTitle(text):
    title = text

    title = re.sub('\([^)]+\)', '', title)
    title = re.sub('\[[^\]]+\]', '',title)
    title = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',title)
    title = re.sub('[“”]','"',title)
    title = re.sub('[‘’]','\'',title)
    title = re.sub('\.{2,3}','...',title)
    title = re.sub('…','...',title)
    title = re.sub('\·{3}','...',title)
    title = re.sub('[=+#/^$@*※&ㆍ!』\\|\<\>`》■□ㅁ◆◇▶◀▷◁△▽▲▼○●━]','',title)

    if not title:   # 제목이 다 사라졌으면 원래 제목으로
        title = text

    return title.strip()


# 키워드 추출
def getKeyword(summary_content):
    tagger = Tagger(apikey=key)
    result = []
    res = tagger.tags([summary_content])
    pa = res.pos()
    for word, type in pa:
        if type == 'NNP' and len(word) >= 2:
            result.append(word)

    return " ".join(result)


def startSummary(news_df, cluster_counts_df):
    summary_news = summary(news_df, cluster_counts_df)
    
    return summary_news