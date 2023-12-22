from gensim.summarization.summarizer import summarize
from preprocessing import Preprocessing
import pandas as pd
import re
# from summa.summarizer import summarize

# 요약 클래스
class Summary:

    def getSummaryArticle(article_df, cluster_counts_df):
        summary_article = pd.DataFrame(columns=["category", "title", "content", "img", "url"])

        for i in range(len(cluster_counts_df)):
            category_name, cluster_number = cluster_counts_df.iloc[i, 0:2]    # 카테고리 이름, 군집 번호

            temp_df = article_df[(article_df['category'] == category_name) & (article_df['cluster_number'] == cluster_number)]

            category = temp_df["category"].iloc[0]          # 카테고리
            title = temp_df["title"].iloc[0]                # 일단은 첫 번째 뉴스 제목
            content = " ".join(temp_df["content"])           # 본문 내용 여러개를 하나의 문자열로 합쳐서 요약
            # content = temp_df["content"].iloc[0]            # 같은 군집 첫 번째 기사
            naver_summary = temp_df["summary"].iloc[0]

            try:
                img = ",".join(list(temp_df["img"]))            # 전체 이미지 (수정 필요)
            except:
                img = ""

            url = ",".join(list(temp_df["url"]))            # 전체 링크

            try:
                # summary_content = summarize(content, ratio=0.2)   # 비율
                summary_content = ""

                for i in range(60, 130, 10):
                    summary_content = summarize(content, word_count=i) # 단어 수
                    
                    if summary_content:     # 요약 됐으면 끝
                        break
                else:
                    summary_content = "본문 그대로 : " + content   # 단어수 130까지 해도 요약 안되면 본문 그대로

            except:
                summary_content = content
            finally:

                summary_content = re.sub('다\.', '다.\n', summary_content)
                summary_content = re.sub('요\.', '요.\n', summary_content)
                cos_similarity, jaccard_similarity = Preprocessing.similarity(summary_content, naver_summary)

                summary_article = summary_article.append({
                    "category": category,
                    "title": title,
                    "content": summary_content,
                    "naver_summary": naver_summary,
                    "similarity" : f"(코사인 유사도 : {round(cos_similarity[0][0] * 100, 2)}%) (자카드 유사도 : {round(jaccard_similarity * 100, 2)}%)",
                    "img": img,
                    "url": url
                }, ignore_index=True)

        return summary_article