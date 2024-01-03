from gensim.summarization.summarizer import summarize
from preprocessing import Preprocessing
import pandas as pd
import re
from konlpy.tag import Okt
# from summa.summarizer import summarize

# 요약 클래스
class Summary:

    def getSummaryArticle(news_df, cluster_counts_df):
        summary_news = pd.DataFrame(columns=["category", "title", "content", "img", "url", "keyword"])

        for i in range(len(cluster_counts_df)):
            category_name, cluster_number = cluster_counts_df.iloc[i, 0:2]    # 카테고리 이름, 군집 번호

            # 군집내 기사들 df
            temp_df = news_df[(news_df['category'] == category_name) & (news_df['cluster_number'] == cluster_number)]

            # 카테고리
            category = temp_df["category"].iloc[0]

            # 첫 번째 뉴스 제목
            title = Preprocessing.cleanTitle(temp_df["title"].iloc[0])

            # 본문
            content = "\n".join(temp_df["content"])

            # 링크
            url = ",".join(list(temp_df["url"]))

            # 이미지
            img = list(temp_df["img"])
            if any(img):
                img = ",".join(list(temp_df["img"]))        
            else:
                img = ""

            # 네이버 요약 봇
            naver_summary = temp_df["summary"].iloc[0]
            
            # 본문 요약
            try:
                summary_content = ""

                for i in range(60, 130, 10):
                    summary_content = summarize(content, word_count=i) # 단어 수
                    
                    if summary_content:     # 요약 됐으면 끝
                        break
                else:
                    # summary_content = "요약 안된 기사 내용 : " + temp_df["content"].iloc[0]    # 단어수 130까지 해도 요약 안되면 본문 그대로
                    summary_content = "XXXXXXXXXX else XXXXXXXXXX"

            except:
                # summary_content =  "요약 안된 기사 내용 : " + temp_df["content"].iloc[0]
                summary_content = "XXXXXXXXXX except XXXXXXXXXX"
            finally:
                
                summary_content = re.sub('다\.', '다.\n', summary_content)
                summary_content = re.sub('요\.', '요.\n', summary_content)

                # 유사도
                cos_similarity, jaccard_similarity = Preprocessing.similarity(summary_content, naver_summary)

                # 키워드
                okt = Okt()
                nouns = []

                for n in okt.nouns(summary_content):
                    if len(n) >= 2:
                        nouns.append(n)

                # 데이터프레임 생성
                summary_news = summary_news.append({
                    "category" : category,
                    "title" : title,
                    "content" : summary_content,
                    "naver_summary" : naver_summary,
                    "similarity" : f"(코사인 유사도 : {cos_similarity}%) (자카드 유사도 : {jaccard_similarity}%)",
                    "img" : img,
                    "url" : url,
                    "keyword" : ",".join(nouns)
                }, ignore_index=True)

        return summary_news