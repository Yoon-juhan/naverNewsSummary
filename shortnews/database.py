import cx_Oracle as cx
import pandas as pd

# category, title, content, url
id = "c##2201058"
pw = "p2201058"
url = "10.30.3.95:1521/orcl"

conn = cx.connect(id, pw, url)

def insert(summary_article):

    sql = """insert into news(news_id, cate_id, title, content, img, link, views)
             values(news_id_seq.nextval, :1, :2, :3, :4, :5, 0)"""

    cur = conn.cursor()
    cur.executemany(sql, summary_article)

    cur.close()
    conn.commit()
    conn.close()

def select():

    sql = """select * from news
             order by to_number(news_id)"""
    
    cur = conn.cursor()
    cur.execute(sql)

    df = pd.read_sql(sql, con = conn)
    df["CONTENT"] = df["CONTENT"].astype("string")      # CLOB 데이터 타입을 string로 변경해야 df로 가져올 수 있음

    cur.close()
    conn.close()

    return df