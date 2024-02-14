from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

# 자카드 유사도 (합집합과, 교집합 사이의 비율)
def jaccard(x, y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    similarity = intersection_cardinality / float(union_cardinality)

    return round(similarity * 100, 2)