import re
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 전처리 클래스
class Preprocessing:

    # 필요없는 내용 삭제 함수
    def clean(article): 
        article = re.sub('\w{2,4}기자','',article)
        article = re.sub('\w{2,4} 온라인 기자','',article)
        article = re.sub('\w+ 기자','',article)
        article = re.sub('\[.{1,15}\]','',article)
        article = re.sub('\w+ 기상캐스터','',article)
        # article = re.sub('사진','',article)
        article = re.sub('포토','',article)
        article = re.sub('\(.*뉴스.{0,3}\)','', article)  # (~뉴스~) 삭제
        article = re.sub('\S+@[a-z.]+','',article)          # 이메일 삭제
        article = re.sub('(\s=\s)','', article)

        article = re.sub('[\n\t\u200b\xa0]','',article)
        article = re.sub('다\.', '다.\n', article)
        article = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',article)
        # article = re.sub('([a-zA-Z])','',article)   # 영어 삭제
        # article = re.sub('[-=+#/\?:^$@*※~&%ㆍ!,\.』\\‘’“”|\(\)\[\]\<\>`\'…》■◆◇▶▷▲○●]','',article)   # 특수문자 삭제
        article = re.sub('[-=+#/:^$@*※&%ㆍ!』\\‘’“”|\[\]\<\>`…》■◆◇▶▷▲○●]','',article)   # 특수문자 삭제


        return article


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

        for i in range(8):
            try:
                text = [" ".join(noun) for noun in article_df['nouns'][article_df['category'] == category_names[i]]]    # 명사 열을 하나의 리스트에 담는다.

                tfidf_vectorizer = TfidfVectorizer(min_df = 3, ngram_range=(1, 5))
                tfidf_vectorizer.fit(text)
                vector = tfidf_vectorizer.transform(text).toarray()                         # vector list 반환
                vector = np.array(vector)
                vector_list.append(vector)
            except:
                print("크롤링 안 한 카테고리 :", category_names[i])

        return vector_list

    # 이름으로된 카테고리를 번호로 변환하는 함수
    def convertCategory(article_df):    
        category = [("정치", "100"), ("경제", "101"), ("사회", "102"), ("생활/문화", "103"), ("세계", "104"), ("IT/과학", "105"), ("연예", "106"), ("스포츠", "107")]

        for name, num in category:
            article_df["category"][article_df["category"] == name] = num

        return article_df

    # 영어 기사 삭제하는 함수
    def removeEnglishArticle(article_df):   
        index = article_df[article_df["nouns"].apply(len) <= 5].index

        if len(index) >= 1:                        # 삭제할 기사 있으면 삭제
            article_df.drop(index, inplace=True)

    # 요약 유사도 검사 함수
    def similarity(my, naver):

        # 코사인 유사도
        data = (my, naver)
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(data)
        cos_similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

        # 자카드 유사도
        intersection_cardinality = len(set.intersection(*[set(my), set(naver)]))
        union_cardinality = len(set.union(*[set(my), set(naver)]))
        jaccard_similarity = intersection_cardinality / float(union_cardinality)

        return [cos_similarity, jaccard_similarity]
