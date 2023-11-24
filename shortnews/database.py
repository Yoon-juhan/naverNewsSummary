import cx_Oracle as cx
import pandas as pd
import datetime

# category, title, content, url
id = "c##2201058"
pw = "p2201058"
url = "10.30.3.95:1521/orcl"

conn = cx.connect(id, pw, url)

def insert(summary_article):

    sql = """insert into news(news_id, cate_id, title, content, link, views)
             values(news_id_seq.nextval, :1, :2, :3, :4, 0)"""

    cur = conn.cursor()
    cur.executemany(sql, summary_article)

    cur.close()
    conn.commit()
    conn.close()