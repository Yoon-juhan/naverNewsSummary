import cx_Oracle as cx
import pandas as pd
import datetime


id = "snews"
pw = "snews"
url = "13.209.75.71:1521/xe"

# 기사 삽입
def insert(summary_news):
    conn = cx.connect(id, pw, url)

    now = datetime.datetime.now()
    now = str(now.year) + str(now.month) + str(now.day) + str(now.hour)

    del summary_news['naver_summary']
    del summary_news['similarity']

    sql = f"""insert into news(news_id, cate_id, title, content, imgs, url, views)
              values({now} || news_seq.nextval, :1, :2, :3, :4, :5, 0)"""

    cur = conn.cursor()
    cur.executemany(sql, summary_news.values.tolist())
    
    print("insert 성공")

    cur.close()
    conn.commit()
    conn.close()

# 전체 기사 조회
def selectAll():
    conn = cx.connect(id, pw, url)

    sql = """select * from news
             order by to_number(news_id) desc"""
    
    cur = conn.cursor()
    cur.execute(sql)

    df = pd.read_sql(sql, con = conn)
    df["CONTENT"] = df["CONTENT"].astype("string")      # CLOB 데이터 타입을 string로 변경해야 df로 가져올 수 있음

    cur.close()
    conn.close()

    return df

# 오늘 날짜 기사 조회
def selectToDay():
    conn = cx.connect(id, pw, url)

    now = datetime.datetime.now()
    now = str(now.year) + str(now.month) + str(now.day)

    sql = f"""select * from news
             where news_id like '{now}%'"""
    
    cur = conn.cursor()
    cur.execute(sql)

    df = pd.read_sql(sql, con = conn)
    df["CONTENT"] = df["CONTENT"].astype("string")      # CLOB 데이터 타입을 string로 변경해야 df로 가져올 수 있음

    cur.close()
    conn.close()

    return df