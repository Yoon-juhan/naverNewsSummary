import requests
from bs4 import BeautifulSoup

category = "103"
date = "2000:00:00"
page_num = "1"

url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=" + category + "#&date=%" + date + "&page=" + page_num

# 접근정보
headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}


news = requests.get(url, headers=headers)   # url에 해당하는 html 코드를 가져옴

def make_urllist(category, date, page_num):

    url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105#&date=%2000:00:00&page=1"    
    html = requests.get(url, headers=headers)   # url에 해당하는 html 코드를 가져옴
    soup = BeautifulSoup(html.text, 'html.parser')
    a_list = soup.select("li")
    print(a_list)
    urllist = []
    # for a in a_list:
    #     if "href" in a.attrs:
    #         if ("article" in a["href"]) and ("sid=105" in a["href"]):
    #             urllist.append(a)

    print(urllist)

make_urllist(category, date, page_num)
