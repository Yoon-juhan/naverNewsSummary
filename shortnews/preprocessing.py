import re
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 전처리 클래스
class Preprocessing:

    # 필요없는 내용 삭제 함수
    def clean(text):    # .으로 마치는 문장들을 리스트로 받음

        text = re.sub('\([^)]*기자*\)', '', text)
        text = re.sub('\w{2,4}기자','',text)
        text = re.sub('\w{2,4} 온라인 기자','',text)
        text = re.sub('\[.{1,15}\]','',text)
        text = re.sub('\w+ 기상캐스터','',text)
        # text = re.sub('\([^)]*\)', '', text)      # 괄호 내용 삭제
        text = re.sub('포토','',text)
        text = re.sub('\(.*뉴스.{0,3}\)','', text)  # (~뉴스~) 삭제
        text = re.sub('\S+@[a-z.]+','',text)          # 이메일 삭제
        text = re.sub('(\s=\s)','', text)

        text = re.sub('※ 우울감 등 .* 있습니다.','', text)
        
        text = re.sub('[\t\n\u200b\xa0]','',text)
        text = re.sub('다\.', '다.\n', text)
        text = re.sub('요\.', '요.\n', text)
        text = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',text)
        # text = re.sub('([a-zA-Z])','',text)   # 영어 삭제
        text = re.sub('[-=+#/:^$@*※&ㆍ!』\\|\[\]\<\>`…》■□ㅁ◆◇▶◀▷◁△▽▲▼○●━]','',text)   # 특수문자 삭제
            
        return text
    
    def cleanTitle(text):
        title = text
        title = re.sub('\[.+\]','',title)
        title = re.sub('\(.+\)','',title)
        title = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',title)
        title = re.sub('\.{3}',' ',title)
        title = re.sub('…',' ',title)
        title = re.sub('\·{3}',' ',title)
        
        title = re.sub('[-=+#/:^$@*※&ㆍ!』\\‘’“”|\[\]\<\>`》\(\)■□ㅁ◆◇▶◀▷◁△▽▲▼○●━]','',title)   # 특수문자 삭제

        if not title:   # 제목이 다 사라졌으면 원래 제목으로
            title = text

        return title.strip()


    # 본문 명사 추출 함수
    def getNouns(news_df):
        okt = Okt()
        nouns_list = []                               # 명사 리스트

        for content in news_df["content"]:
            nouns_list.append(okt.nouns(content))     # 명사 추출 (리스트 반환)

        news_df["nouns"] = nouns_list              # 데이터 프레임에 추가

    # 명사 벡터화 함수
    def getVector(news_df):    # 카테고리 별로 벡터 생성
        category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
        vector_list = []

        for i in range(8):
            try:
                text = [" ".join(noun) for noun in news_df['nouns'][news_df['category'] == category_names[i]]]    # 명사 열을 하나의 리스트에 담는다.
                 
                tfidf_vectorizer = TfidfVectorizer(min_df = 3, ngram_range=(1, 5))
                tfidf_vectorizer.fit(text)
                vector = tfidf_vectorizer.transform(text).toarray()                         # vector list 반환
                vector = np.array(vector)
                vector_list.append(vector)
            except:
                index = news_df[news_df['category'] == category_names[i]].index
                news_df.drop(index, inplace=True)
                print(f"{category_names[i]} 기사 수 10개 이하")

        return vector_list

    # 카테고리 번호 변환 함수 (정치 -> 100)
    def convertCategory(news_df):    
        category = [("정치", "100"), ("경제", "101"), ("사회", "102"), ("생활/문화", "103"), ("세계", "104"), ("IT/과학", "105"), ("연예", "106"), ("스포츠", "107")]

        for name, num in category:
            news_df["category"][news_df["category"] == name] = num

    # 요약 유사도 함수
    def similarity(x, y):

        # 코사인 유사도
        data = (x, y)
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(data)
        cos_similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

        # 자카드 유사도 (합집합과, 교집합 사이의 비율)
        intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
        union_cardinality = len(set.union(*[set(x), set(y)]))
        jaccard_similarity = intersection_cardinality / float(union_cardinality)

        return [round(cos_similarity[0][0] * 100, 2), round(jaccard_similarity * 100, 2)]