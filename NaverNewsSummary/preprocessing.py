import re
from collections import Counter
from konlpy.tag import Okt, Komoran
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from bareunpy import Tagger


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


# 본문 명사 추출
def getNouns(news_df):
    okt = Okt()
    nouns_list = []                                 # 명사 리스트

    for content in news_df["content"]:
        nouns_list.append(okt.nouns(content))       # 명사 추출 (리스트 반환)

    news_df["nouns"] = nouns_list                   # 데이터 프레임에 추가

# 카테고리 번호 변환 (정치 -> 100)
def convertCategory(news_df):    
    category = [("정치", "100"), ("경제", "101"), ("사회", "102"), ("생활/문화", "103"), ("세계", "104"), ("IT/과학", "105"), ("연예", "106"), ("스포츠", "107")]

    for name, num in category:
        news_df["category"][news_df["category"] == name] = num


# 키워드 추출
def getKeyword(summary_content):
    tagger = Tagger(apikey='koba-MBTOTZI-CRPEEBI-SRDUSVI-FPSMISA')
    result = []
    res = tagger.tags([summary_content])
    pa = res.pos()
    for word, type in pa:
        if type == 'NNP' and len(word) >= 2:
            result.append(word)

    return " ".join(result)