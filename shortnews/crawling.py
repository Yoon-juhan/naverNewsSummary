from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time
import datetime
from pytz import timezone

# 전처리 클래스
from preprocessing import Preprocessing

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(options=options)
# ------------------------------------------- 준비 ------------------------------------------- #


# 기사 링크 크롤링
class UrlCrawling:
    def __init__(self):
        self.category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
        self.category = []

    def getSixUrl(self):    # 정치, 경제, 사회, 생활/문화, 세계, IT/과학
        six_url = []
        for category in range(6):     # 6
            a_list = []
            for page in range(1, 2):  # 1, 6
                url = f'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1={100 + category}#&date=%2000:00:00&page={page}'
                browser.get(url)

                time.sleep(0.5)

                soup = BeautifulSoup(browser.page_source, "html.parser")
                a_list.extend(soup.select(".type06_headline dt+dt a"))
                a_list.extend(soup.select(".type06 dt+dt a"))

                print(f"{self.category_names[category]} {page} 페이지")

            for a in a_list:
                six_url.append(a["href"])
                self.category.append(self.category_names[category])

        return six_url


    def getEntertainmentUrl(self):   # 연예
        # today = str(datetime.datetime.now(KST))[:11]  # 서울 기준 시간
        entertainment_url = []
        a_list = []
        today = datetime.date.today()

        for page in range(1, 2):  # 1, 5
            url = f'https://entertain.naver.com/now#sid=106&date={today}&page={page}'
            browser.get(url)

            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            a_list.extend(soup.select(".news_lst li>a"))


            print(f"연예 {page} 페이지")

        for a in a_list:
            entertainment_url.append("https://entertain.naver.com" + a["href"])
            self.category.append("연예")

        return entertainment_url

    def getSportsUrl(self):    # 스포츠  (페이지마다 개수가 달라서 6페이지를 이동)
        # today = str(datetime.datetime.now(KST))[:11].replace('-', '')  # 서울 기준 시간
        sports_url = []
        a_list = []
        today = str(datetime.date.today()).replace('-', '')

        for page in range(1, 2):  # 1, 7
            url = f'https://sports.news.naver.com/general/news/index?isphoto=N&type=latest&date={today}&page={page}'
            browser.get(url)

            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")
            a_list.extend(soup.select(".news_list li>a"))

            print(f"스포츠 {page} 페이지")

        for i in range(len(a_list)):
            if i == 100:  # 100개 링크 추가했으면 멈추기
                break
            sports_url.append("https://sports.news.naver.com/news" + re.search('\?.+', a_list[i]["href"]).group())
            self.category.append("스포츠")

        return sports_url



# 기사 본문 크롤링
class ContentCrawling:
    def __init__(self, title, content, date, img, summary):
        self.title = title
        self.content = content
        self.date = date
        self.img = img
        self.summary = summary          # 네이버 요약봇이 요약한 내용

    def getSixContent(self, url_list):  # 정치, 경제, 사회, 생활/문화, 세계, IT/과학
        title_list = []
        content_list = []
        date_list = []
        img_list = []
        cnt = 1

        for url in url_list:
            browser.get(url)
            summary_btn = False

            try:
                browser.find_element(By.ID, "_SUMMARY_BUTTON").click()    # 요약봇 클릭
                browser.find_element(By.ID, "_SUMMARY_BUTTON").click()    # 요약봇 클릭

                summary_btn = True
                print(cnt, end=", ")
            except:
                print(cnt, "요약봇 X", end=", ")
            
            cnt+=1
            
            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            try:
                title_list.extend(soup.select("#title_area span"))              # 제목 추가

                c = soup.find_all(attrs={"id" : "dic_area"})                    # 본문 가져오기

                if summary_btn:
                    # summary_content = soup.select("._SUMMARY_CONTENT_BODY")
                    summary_content = soup.find(attrs={"class" : "_SUMMARY_CONTENT_BODY"})
                    try:
                        summary_content.find("strong").decompose()
                        # self.summary.append(summary_content.text)
                        self.summary.append(re.sub('다\.', '다.\n', summary_content.text))
                    except:
                        self.summary.append("x")

                else:
                    self.summary.append("x")
                

                img_tag = soup.select(".end_photo_org img")                     # 이미지 가져오기

                if img_tag:                                                     # 이미지 있으면 이미지 주소만 추출해서 리스트로 만든다.
                    img_src_list = []
                    for img in img_tag:
                        img_src_list.append(img['src'])
                    img_list.append(",".join(img_src_list))
                else:
                    img_list.append("x")

                while c[0].find("strong"):
                    c[0].find("strong").decompose()
                while c[0].find(attrs={"class" : "end_photo_org"}):             # 이미지 있는 만큼
                    c[0].find(attrs={"class" : "end_photo_org"}).decompose()    # 본문 이미지에 있는 글자 없애기

                while c[0].find(attrs={"class" : "vod_player_wrap"}):           # 영상 있는 만큼
                    c[0].find(attrs={"class" : "vod_player_wrap"}).decompose()  # 본문 영상에 있는 글자 없애기

                if c[0].find(attrs={"class" : "artical-btm"}):                  # 하단에 제보하기 칸 있으면 삭제
                    c[0].find(attrs={"class" : "artical-btm"}).decompose()

                content_list.extend(c)                                          # 본문 추가

                date_list.extend(soup.select("._ARTICLE_DATE_TIME"))            # 날짜 추가

            except IndexError:
                print("삭제된 기사")

        print()

        for t in title_list:
            self.title.append(Preprocessing.clean(t.text))

        for c in content_list:
            self.content.append(Preprocessing.clean(c.text))

        for d in date_list:
            self.date.append(d.text)

        for i in img_list:
            self.img.append(i)

    def getEntertainmentContent(self, url_list):    # 연예
        title_list = []
        content_list = []
        date_list = []
        img_list = []
        cnt = 1

        for url in url_list:
            browser.get(url)

            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            print(cnt, end=", ")
            cnt+=1

            try:
                title_list.extend(soup.select(".end_tit"))                      # 제목 추가

                c = soup.find_all(attrs={"class" : "article_body"})             # 본문 가져오기

                img_tag = soup.select(".end_photo_org img")                     # 이미지 가져오기

                if img_tag:                                                     # 이미지 있으면 이미지 주소만 추출해서 리스트로 만든다.
                    img_src_list = []
                    for img in img_tag:
                        img_src_list.append(img['src'])
                    img_list.append(",".join(img_src_list))
                else:
                    img_list.append("x")


                while c[0].find(attrs={"class" : "end_photo_org"}):             # 이미지 있는 만큼
                    c[0].find(attrs={"class" : "end_photo_org"}).decompose()    # 본문 이미지에 있는 글자 없애기

                if c[0].find(attrs={"class" : "caption"}):                      # 이미지 설명 없애기
                    c[0].find(attrs={"class" : "caption"}).decompose()

                while c[0].find(attrs={"id" : "video_area"}):                # 영상 있는 만큼
                    c[0].find(attrs={"id" : "video_area"}).decompose()       # 본문 영상 없애기

                while c[0].find(attrs={"name" : "iframe"}):
                    c[0].find(attrs={"name" : "iframe"}).decompose()

                content_list.extend(c)                                          # 본문 추가

                date_list.extend(soup.select_one(".author em"))                 # 날짜 추가

            except IndexError:
                print("삭제된 기사")

        print()

        for t in title_list:
            self.title.append(Preprocessing.clean(t.text))
            self.summary.append("x")

        for c in content_list:
            self.content.append(Preprocessing.clean(c.text))

        for d in date_list:
            self.date.append(d.text)
            
        for i in img_list:
            self.img.append(i)

    def getSportsContent(self, url_list):   # 스포츠
        title_list = []
        content_list = []
        date_list = []
        img_list = []
        cnt = 1

        for url in url_list:

            browser.get(url)                                                    
            
            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            print(cnt, end=", ")
            cnt+=1

            title_list.extend(soup.select(".news_headline .title"))             # 제목 추가 

            c = soup.find_all(attrs={"class" : "news_end"})                     # 본문 가져오기

            img_tag = soup.select(".end_photo_org img")                     # 이미지 가져오기

            if img_tag:                                                     # 이미지 있으면 이미지 주소만 추출해서 리스트로 만든다.
                img_src_list = []
                for img in img_tag:
                    img_src_list.append(img['src'])
                img_list.append(",".join(img_src_list))
            else:
                img_list.append("x")

            while c[0].find(attrs={"class" : "end_photo_org"}):                 # 이미지 있는 만큼
                c[0].find(attrs={"class" : "end_photo_org"}).decompose()        # 본문 이미지에 있는 글자 없애기

            while c[0].find(attrs={"class" : "image"}):
                c[0].find(attrs={"class" : "image"}).decompose()

            while c[0].find(attrs={"class" : "vod_area"}):                      # 영상 있는 만큼
                c[0].find(attrs={"class" : "vod_area"}).decompose()             # 본문 영상 없애기

            if c[0].find(attrs={"class" : "source"}): c[0].find(attrs={"class" : "source"}).decompose()
            if c[0].find(attrs={"class" : "byline"}): c[0].find(attrs={"class" : "byline"}).decompose()
            if c[0].find(attrs={"class" : "reporter_area"}): c[0].find(attrs={"class" : "reporter_area"}).decompose()
            if c[0].find(attrs={"class" : "copyright"}): c[0].find(attrs={"class" : "copyright"}).decompose()
            if c[0].find(attrs={"class" : "categorize"}): c[0].find(attrs={"class" : "categorize"}).decompose()
            if c[0].find(attrs={"class" : "promotion"}): c[0].find(attrs={"class" : "promotion"}).decompose()

            content_list.extend(c)                                        # 본문 추가

            date_list.extend(soup.select_one(".info span"))               # 날짜 추가

        for t in title_list:
            self.title.append(Preprocessing.clean(t.text))
            self.summary.append("x")

        for c in content_list:
            self.content.append(Preprocessing.clean(c.text))

        for d in date_list:
            d = (d.text)[5:]
            self.date.append(d)

        for i in img_list:
            self.img.append(i)

    def makeDataFrame(self, all_url, category):    # 수집한 데이터를 데이터프레임으로 변환

        article_df = pd.DataFrame({"category" : category,
                                   "date" : self.date,
                                   "title" : self.title,
                                   "content" : self.content,
                                   "img" : self.img,
                                   "url" : all_url,
                                   "summary" : self.summary})

        return article_df