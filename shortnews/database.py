import cx_Oracle as cx
import pandas as pd
import datetime

# 테스트 DB
# id = "c##2201058"
# pw = "p2201058"
# url = "10.30.3.95:1521/orcl"

# 우리 프로젝트 DB
id = "snews"
pw = "snews"
url = "13.209.75.71:1521/xe"

def insert(summary_article):
    conn = cx.connect(id, pw, url)

    now = datetime.datetime.now()
    now = str(now.year) + str(now.month) + str(now.day) + str(now.hour)

    # 테스트
    # sql = f"""insert into news(news_id, cate_id, title, content, img, link, views)
    #           values({now} || news_id_seq.nextval, :1, :2, :3, :4, :5, 0)"""

    # 우리 프로젝트
    sql = f"""insert into news(news_id, cate_id, title, content, imgs, link, views)
              values({now} || news_seq.nextval, :1, :2, :3, :4, :5, 0)"""

    cur = conn.cursor()
    cur.executemany(sql, summary_article)
    
    print("insert 성공")

    cur.close()
    conn.commit()
    conn.close()

def select():
    conn = cx.connect(id, pw, url)

    try:
        sql = """select * from news
                order by to_number(news_id) desc"""
        
        cur = conn.cursor()
        cur.execute(sql)

        df = pd.read_sql(sql, con = conn)
        df["CONTENT"] = df["CONTENT"].astype("string")      # CLOB 데이터 타입을 string로 변경해야 df로 가져올 수 있음

        return df
    
    except:
        print("뭔가 잘못됨")
    finally:
        cur.close()
        conn.close()

        
# class DB:

#     def __init__(self) :
#         self.id = "c##2201058"
#         self.pw = "p2201058"
#         self.url = "10.30.3.95:1521/orcl"

#     def insert(self, summary_article):
#         conn = cx.connect(self.id, self.pw, self.url)

#         now = datetime.datetime.now()
#         now = str(now.year) + str(now.month) + str(now.day) + str(now.hour)

#         sql = """insert into news(news_id, cate_id, title, content, img, link, views)
#                 values(news_id_seq.nextval, :1, :2, :3, :4, :5, 0)"""

#         cur = conn.cursor()
#         cur.executemany(sql, summary_article)

#         cur.close()
#         conn.commit()
#         conn.close()

#     def select(self):
#         conn = cx.connect(self.id, self.pw, self.url)

#         try:
#             sql = """select * from news
#                     order by to_number(news_id)"""
            
#             cur = conn.cursor()
#             cur.execute(sql)

#             df = pd.read_sql(sql, con = conn)
#             df["CONTENT"] = df["CONTENT"].astype("string")      # CLOB 데이터 타입을 string로 변경해야 df로 가져올 수 있음

#             return df
        
#         except:
#             print("뭔가 잘못됨")
#         finally:
#             cur.close()
#             conn.close()

        