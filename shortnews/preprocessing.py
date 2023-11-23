import re
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# 필요없는 내용 삭제 함수
def clean(article):
    text = re.sub('\[.{1,15}\]','',text)
    text = re.sub('\w{2,4} 온라인 기자','',text)
    text = re.sub('\w+ 기자','',text)
    text = re.sub('\w{2,4}기자','',text)
    text = re.sub('\w+ 기상캐스터','',text)
    text = re.sub('사진','',text)
    text = re.sub('포토','',text)

    text = re.sub('\S+@[a-z.]+','',text)          # 이메일 삭제

    text = re.sub('\n','',text)
    text = re.sub('\t','',text)
    text = re.sub('\u200b','',text)
    text = re.sub('\xa0','',text)
    text = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',text)
    # text = re.sub('([a-zA-Z])','',text)   # 영어 삭제
    # text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘’“”|\(\)\[\]\<\>`\'…》]','',text)   # 특수문자 삭제

    return text

# 본문에서 명사 뽑아내는 함수
def getNouns(article_df):
    okt = Okt()
    nouns_list = []                               # 명사 리스트

    for content in article_df["content"]:
        nouns_list.append(okt.nouns(content))     # 명사 추출 (리스트 반환)

    article_df["nouns"] = nouns_list              # 데이터 프레임에 추가
    
    return article_df

# 명사를 벡터화 하는 함수
def getVector(article_df):    # 카테고리 별로 벡터 생성
    category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
    vector_list = []

    for i in range(7):
        text = [" ".join(noun) for noun in article_df['nouns'][article_df['category'] == category_names[i]]]    # 명사 열을 하나의 리스트에 담는다.

        tfidf_vectorizer = TfidfVectorizer(min_df = 3, ngram_range=(1, 5))
        tfidf_vectorizer.fit(text)
        vector = tfidf_vectorizer.transform(text).toarray()                         # vector list 반환
        vector = np.array(vector)
        vector_list.append(vector)

    return vector_list