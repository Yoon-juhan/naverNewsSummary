from bs4 import BeautifulSoup            
from selenium import webdriver           
import time                              
from selenium.webdriver.common.by import By
import csv
from newspaper import Article

def basic_clear(text) :
    text = text.replace('\n', '')
    text = text.replace('<dt><a href="', '')
    text = text.replace('">', ' ')
    text = text.replace('</a></dt>', '')
    text = text.replace('\t', '')
    text = text.replace('[', '')
    text = text.replace(']', '')
    return text

# 브라우저 켜기
url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105#&date=%2000:00:00&page=1'
browser = webdriver.Chrome()
browser.get(url)

# f = codecs.open("c:/crawler2/kyoboBest.txt", mode="w", encoding="utf-8")

# // 책 순위 표기를 위해 미리 으로 선언
book_rank = 0

# cvs 파일 저장
f1 = open(r'.\test.csv', 'w', newline='', encoding='utf-8')
wr = csv.writer(f1)
wr.writerow(['title', 'content', 'link'])

for i in range(1, 2):
    # 네이버 뉴스 -> 정치 -> 행정 페이지
    browser.get('https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105#&date=%2000:00:00&page=' + str(i))
    
    # // 1초마다 페이지 넘김, 안할시 로봇으로 간주되어 블락이 될수 있음
    time.sleep(1)
    
    image_list = []
    
    # // 소스코드 저장
    html = browser.text
    
    # // 소스코드 파싱
    soup = BeautifulSoup(html, "html.parser")
    
    #section_body > ul.type06_headline > li:nth-child(1) > dl > dt:nth-child(2) > a
    # 행정 페이지 class가 다음과 같은 블록 중 ul가져옴(?)
    ul_list = soup.find_all("ul", class_="type06_headline")
    
    ul_list = ul_list[0]
    
    # ul -> dt태그 의 두 번째 자식 태그
    div_image_list = ul_list.select("dt:nth-child(2)")
    for idx, item in enumerate(div_image_list):
        temp = basic_clear(str(item)) # 특수기호 및 공백 처리

        space = temp.index(' ')
        link = temp[:space]

        article = Article(link, language = "ko")
        article.download()
        article.parse()
        title = article.title
        text = article.text

        #title = temp[space + 1:].strip()
        
        wr.writerow([title, text, link])


    # 본문 가져오는 코드
    ul_list = soup.find_all("ul", class_="type06")
    
    ul_list = ul_list[0]
    
    # ul -> dt태그 의 두 번째 자식 태그
    div_image_list = ul_list.select("dt:nth-child(2)")
    for idx, item in enumerate(div_image_list):
        temp = basic_clear(str(item)) # 특수기호 및 공백 처리

        space = temp.index(' ')
        link = temp[:space]

        article = Article(link, language = "ko")
        article.download()
        article.parse()
        title = article.title
        text = article.text

        #title = temp[space + 1:].strip()
        
        wr.writerow([title, text, link])


f1.close()
f1 = open(r'.\test.csv', 'r', encoding='utf-8')
spamreader = csv.reader(f1)
for row in spamreader:
    print(row)
f1.close()


"""
###pandas code###

import pandas as pd
import numpy as np
df = pd.read_csv('./test.csv', encoding='utf-8')
for i in range(len(df) - 1):
  if df['title'][i][:8] == df['title'][i + 1][:8]:
    df['title'][i] = df['link'][i] = np.nan

tempDF = df.dropna(axis=0, how='all', inplace=False) # nan행 DELETE, 인덱스 번호 뒤죽박죽

"""