from gensim.summarization.summarizer import summarize
import pandas as pd
# from summa.summarizer import summarize

def getSummaryArticle(article_df, cluster_counts_df):
    category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
    summary_article = pd.DataFrame(columns=["category", "title", "content", "url"])

    for i in range(len(cluster_counts_df)):
        category_name, cluster_number = cluster_counts_df.iloc[i, 0:2]    # 카테고리 이름, 군집 번호

        temp_df = article_df[(article_df['category'] == category_name) & (article_df['cluster_number'] == cluster_number)]

        category = temp_df["category"].iloc[0]          # 카테고리
        title = temp_df["title"].iloc[0]                # 일단은 첫 번째 뉴스 제목
        content = "".join(temp_df["content"])     # 본문 내용 여러개를 하나의 문자열로 합쳐서 요약

        url = ",".join(list(temp_df["url"]))                      # 전체 링크

        try:
            summary_content = summarize(content, ratio=0.1)
            if not summary_content:     # 요약문이 비어있으면 (너무 짧아서?)
                summary_content = "어떻게 고칠까?"
        except:
            summary_content = content
        finally:
            summary_article = summary_article.append({
                "category": category,
                "title": title,
                "content": summary_content,
                "url": url
            }, ignore_index=True)

    return summary_article