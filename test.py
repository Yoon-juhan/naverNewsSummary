from bs4 import BeautifulSoup            
from selenium import webdriver           
import time                              

browser = webdriver.Chrome()

url_list = []
for category in range(6):
    for page in range(1, 6):
        url = f'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={100 + category}#&date=%2000:00:00&page={page}'
        browser.get(url)

        time.sleep(1)

        soup = BeautifulSoup(browser.page_source, "html.parser")
        a_list = soup.select(".type06_headline dt+dt a")
        a_list.extend(soup.select(".type06 dt+dt a"))

        
        for a in a_list:
            if "href" in a.attrs:
                if ("article" in a["href"]) and (f"sid={100+category}" in a["href"]):
                    url_list.append((a["href"], a.text))

        print(category, page)

print(url_list)
print(len(url_list))