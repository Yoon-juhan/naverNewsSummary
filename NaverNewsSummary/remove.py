from langdetect import detect

# 3문장 이하 or 300자 이하 기사 삭제
def shortNews(news_df):
    news_df.drop(news_df[news_df['content'].apply(lambda x : len(x.split("다."))) <= 4].index, inplace=True)
    news_df.drop(news_df[news_df['content'].apply(len) <= 300].index, inplace=True)

# 언어 감지
def isEnglish(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except:
        return False

# 영어 기사 삭제
def englishNews(news_df):
    news_df = news_df[~news_df['content'].apply(isEnglish)]

# 포토, 영상, 인터뷰 기사 등 삭제
def EtcNews(news_df):
    news_df.drop(news_df[news_df['title'].str.contains('사진|포토|영상|움짤|헤드라인|라이브|정치쇼')].index, inplace=True)
    news_df.drop(news_df[news_df['content'].str.contains('방송 :|방송:|진행 :|진행:|출연 :|출연:|앵커|[앵커]')].index, inplace=True)

def startRemove(news_df):

    EtcNews(news_df)        # 포토, 영상, 인터뷰 기사 등 삭제
    shortNews(news_df)      # 3문장 or 300자 이하 기사 삭제
    englishNews(news_df)    # 영어 기사 삭제
    news_df.drop_duplicates(subset=["url"], inplace=True)