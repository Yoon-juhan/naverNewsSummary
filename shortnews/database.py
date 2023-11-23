import cx_Oracle as cx
import pandas as pd

id = "c##2201058"
pw = "p2201058"
url = "10.30.3.95:1521/orcl"

conn = cx.connect(id, pw, url)

cur = conn.cursor()
cur.execute("select * from tab")

for c in cur:
    print(c)

cur.close()
conn.close()