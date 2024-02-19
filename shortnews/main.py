# coding: utf-8

import schedule
import time

from crawling import startCrawling
from clustering import startClustering
from summary import startSummary
from remove import startRemove

def start():
    news_df = startCrawling()                                   # 크롤링

    startRemove(news_df)                                        # 필요없는 기사 삭제

    cluster_counts_df = startClustering(news_df)                # 군집화

    summary_news = startSummary(news_df, cluster_counts_df)     # 요약

start()

# # n분 마다 호출  
# schedule.every(10).minutes.do(start)

# # n시간마다 호출  
# schedule.every(1).hour.do(start)

# while True:
#     schedule.run_pending()
#     time.sleep(1)