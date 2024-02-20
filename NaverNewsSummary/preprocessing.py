import re
from bareunpy import Tagger
from bareunpy_api_key import key

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


# 카테고리 번호 변환 (정치 -> 100)
def convertCategory(news_df):    
    category = [("정치", "100"), ("경제", "101"), ("사회", "102"), ("생활/문화", "103"), ("세계", "104"), ("IT/과학", "105"), ("연예", "106"), ("스포츠", "107")]

    for name, num in category:
        news_df["category"][news_df["category"] == name] = num


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