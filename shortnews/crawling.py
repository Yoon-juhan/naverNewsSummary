from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import datetime
from pytz import timezone

from preprocessing import clean     # preprocessing파일에 전처리 함수 임포트

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(options=options)
# ------------------------------------------- 준비 ------------------------------------------- #


# 기사 링크 크롤링
class UrlCrawling:
    def __init__(self, six_url, entertainment_url, sports_url, category, category_names):
        self.six_url = six_url
        self.entertainment_url = entertainment_url
        self.sports_url = sports_url
        self.category = category
        self.category_names = category_names

    def getSixLink(self):    # 정치, 경제, 사회, 생활/문화, 세계, IT/과학

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
                self.six_url.append(a["href"])
                self.category.append(self.category_names[category])


    def getEntertainmentLink(self):   # 연예
        # today = str(datetime.datetime.now(KST))[:11]  # 서울 기준 시간
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
            self.entertainment_url.append("https://entertain.naver.com" + a["href"])
            self.category.append(self.category_names[6])


    def getSportsLink(self):    # 스포츠  (페이지마다 개수가 달라서 6페이지를 이동)
        # today = str(datetime.datetime.now(KST))[:11].replace('-', '')  # 서울 기준 시간
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
            self.sports_url.append("https://sports.news.naver.com/news" + re.search('\?.+', a_list[i]["href"]).group())
            self.category.append(self.category_names[7])

url_crawler = UrlCrawling([], [], [], [], ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"])
url_crawler.getEntertainmentLink()



# 기사 본문 크롤링
class ContentCrawling:                  
    def __init__(self, title, content, date):
        self.title = title
        self.content = content
        self.date = date

    def getSixContent(self, url_list):  # 정치, 경제, 사회, 생활/문화, 세계, IT/과학
        title_list = []
        content_list = []
        date_list = []
        
        for url in url_list:
            browser.get(url)

            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            try:
                title_list.extend(soup.select("#title_area span"))              # 제목

                c = soup.find_all(attrs={"id" : "dic_area"})                    # 본문

                while c[0].find(attrs={"class" : "end_photo_org"}):             # 이미지 있는 만큼
                    c[0].find(attrs={"class" : "end_photo_org"}).decompose()    # 본문 이미지에 있는 글자 없애기

                while c[0].find(attrs={"class" : "vod_player_wrap"}):           # 영상 있는 만큼
                    c[0].find(attrs={"class" : "vod_player_wrap"}).decompose()  # 본문 영상에 있는 글자 없애기

                if c[0].find(attrs={"class" : "artical-btm"}):                  # 하단에 제보하기 칸 있으면 삭제
                    c[0].find(attrs={"class" : "artical-btm"}).decompose()

                content_list.extend(c)

                date_list.extend(soup.select("._ARTICLE_DATE_TIME"))            # 날짜

            except IndexError:
                print("삭제된 기사")

        for t in title_list:
            self.title.append(clean(t.text))

        for c in content_list:
            self.content.append(clean(c.text))

        for d in date_list:
            self.date.append(d.text)


    def getEntertainmentContent(self, url_list):    # 연예
        title_list = []
        content_list = []
        date_list = []
        
        for url in url_list:
            browser.get(url)

            time.sleep(0.5)
            
            soup = BeautifulSoup(browser.page_source, "html.parser")

            try:
                title_list.extend(soup.select(".end_tit"))                      # 제목

                c = soup.find_all(attrs={"class" : "article_body"})             # 본문

                while c[0].find(attrs={"class" : "end_photo_org"}):             # 이미지 있는 만큼
                    c[0].find(attrs={"class" : "end_photo_org"}).decompose()    # 본문 이미지에 있는 글자 없애기

                if c[0].find(attrs={"class" : "caption"}):                      # 이미지 설명 없애기
                    c[0].find(attrs={"class" : "caption"}).decompose()

                while c[0].find(attrs={"class" : "video_area"}):                # 영상 있는 만큼
                    c[0].find(attrs={"class" : "video_area"}).decompose()       # 본문 영상에 있는 글자 없애기

                while c[0].find(attrs={"name" : "iframe"}):
                    c[0].find(attrs={"name" : "iframe"}).decompose()

                content_list.extend(c)

                date_list.extend(soup.select_one(".author em"))                 # 날짜

            except IndexError:
                print("삭제된 기사")

        for t in title_list:
            self.title.append(clean(t.text))

        for c in content_list:
            self.content.append(clean(c.text))

        for d in date_list:
            self.date.append(d.text)


    def getSportsContent(self, url_list):   # 스포츠
        title_list = []
        content_list = []
        date_list = []

        for url in url_list:

            browser.get(url)                                                    # 스포츠 기사만 여기서 넘어가는데 굉장히 진짜 대박 오래 걸림 왜 그럴까? 스포츠
            print(url)
            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            title_list.extend(soup.select(".news_headline .title"))             # 제목

            c = soup.find_all(attrs={"class" : "news_end"})                     # 본문

            while c[0].find(attrs={"class" : "end_photo_org"}):                 # 이미지 있는 만큼
                c[0].find(attrs={"class" : "end_photo_org"}).decompose()        # 본문 이미지에 있는 글자 없애기

            while c[0].find(attrs={"class" : "image"}):
                c[0].find(attrs={"class" : "image"}).decompose()

            while c[0].find(attrs={"class" : "vod_area"}):                      # 영상 있는 만큼
                c[0].find(attrs={"class" : "vod_area"}).decompose()             # 본문 영상에 있는 글자 없애기

            c[0].find(attrs={"class" : "source"}).decompose()
            c[0].find(attrs={"class" : "byline"}).decompose()
            c[0].find(attrs={"class" : "reporter_area"}).decompose()
            c[0].find(attrs={"class" : "copyright"}).decompose()
            c[0].find(attrs={"class" : "categorize"}).decompose()
            c[0].find(attrs={"class" : "promotion"}).decompose()

            content_list.extend(c)

            date_list.extend(soup.select_one(".info span"))               # 날짜

        for t in title_list:
            self.title.append(clean(t.text))

        for c in content_list:
            self.content.append(clean(c.text))

        for d in date_list:
            self.date.append(d.text)

    def makeDataFrame(self):    # 수집한 데이터를 데이터프레임으로 변환
        all_url = url_crawler.six_url + url_crawler.entertainment_url + url_crawler.sports_url

        article_df = pd.DataFrame({"category" : url_crawler.category,
                                   "date" : self.date,
                                   "title" : self.title,
                                   "content" : self.content,
                                   "url" : all_url})

        return article_df

content_crawler = ContentCrawling([], [], [])
content_crawler.getEntertainmentContent(url_crawler.entertainment_url)

article_df = content_crawler.makeDataFrame()
print(article_df)