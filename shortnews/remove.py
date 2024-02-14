from database import selectToDay
from preprocessing import getNouns
from similarity import cosine, jaccard

# 이미 요약한 기사 삭제
def original_duplication(six_url_df, entertainment_url_df, sports_url_df):   
    db_url_df = selectToDay()    # 오늘 날짜 기사 검색

    db_urls = []
    if not db_url_df.empty:
        db_url_df['URL'].apply(lambda x : db_urls.extend(x.split(",")))     # news 테이블 url컬럼에 있는 모든 url을 리스트로 생성

        six_url_df.drop(six_url_df['six_url'][six_url_df['six_url'].apply(lambda x : x in db_urls)].index, inplace=True)
        entertainment_url_df.drop(entertainment_url_df['entertainment_url'][entertainment_url_df['entertainment_url'].apply(lambda x : x in db_urls)].index, inplace=True)
        sports_url_df.drop(sports_url_df['sports_url'][sports_url_df['sports_url'].apply(lambda x : x in db_urls)].index, inplace=True)

# 이미 요약한 기사 삭제 (스레드용)
def duplication(url_df_list):
    db_url_df = selectToDay()    # 오늘 날짜 기사 검색

    db_urls = []
    if not db_url_df.empty:
        db_url_df['URL'].apply(lambda x : db_urls.extend(x.split(",")))     # news 테이블 url컬럼에 있는 모든 url을 리스트로 생성

        for df in url_df_list:
            df.drop(df['url'][df['url'].apply(lambda x : x in db_urls)].index, inplace=True)


# 3문장 이하 or 300자 이하 기사 삭제
def shortNews(news_df):
    news_df.drop(news_df[news_df['content'].apply(lambda x : len(x.split("다."))) <= 4].index, inplace=True)
    news_df.drop(news_df[news_df['content'].apply(len) <= 300].index, inplace=True)

# 영어 기사 삭제
def englishNews(news_df):   
    index = news_df[news_df["nouns"].apply(len) <= 5].index

    if len(index) >= 1:                        # 삭제할 기사 있으면 삭제
        news_df.drop(index, inplace=True)

# 포토, 영상, 인터뷰 기사 등 삭제
def News(news_df):
    news_df.drop(news_df[news_df['title'].str.contains('사진|포토|영상|움짤|헤드라인|라이브|정치쇼')].index, inplace=True)
    news_df.drop(news_df[news_df['content'].str.contains('방송 :|방송:|진행 :|진행:|출연 :|출연:|앵커|[앵커]')].index, inplace=True)


# 유사 기사 삭제
def similarNews(summary_news):
    index = []
    db_df = selectToDay()

    if not db_df.empty:
        for i in range(len(summary_news)):
            now_news = summary_news['content'].iloc[i]
            
            tmp = db_df[db_df['CATE_ID'] == summary_news['category'].iloc[i]]
            
            for j in range(len(tmp)):
                cosine_similarity = cosine(now_news, tmp['CONTENT'].iloc[j])
                jaccard_similarity = jaccard(now_news, tmp['CONTENT'].iloc[j])
                if cosine_similarity >= 70 or jaccard_similarity >= 70:    # 유사도 70% 이상이면 drop
                    index.append(i)
        
        summary_news.drop(index, inplace=True)


def startRemove(news_df):

    News(news_df)           # 포토, 영상, 인터뷰 기사 등 삭제
    shortNews(news_df)      # 3문장 or 300자 이하 기사 삭제
    getNouns(news_df)       # 명사 추출
    englishNews(news_df)    # 영어 기사 삭제
    news_df.drop_duplicates(subset=["url"], inplace=True)
