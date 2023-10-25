from bs4 import BeautifulSoup            
from selenium import webdriver           
import time                              
from selenium.webdriver.common.by import By

# 브라우저 켜기
browser = webdriver.Chrome()

url_list = []
for i in range(1, 3):

    url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105#&date=%2000:00:00&page=' + str(i)
    browser.get(url)

    time.sleep(1)

    soup = BeautifulSoup(browser.page_source, "html.parser")

    a_list = soup.select(".type06_headline dt+dt a")
    a_list.extend(soup.select(".type06 dt+dt a"))

    
    for a in a_list:
        if "href" in a.attrs:
            if ("article" in a["href"]) and ("sid=105" in a["href"]):
                url_list.append((a["href"], a.text))

print(url_list)
print(len(url_list))