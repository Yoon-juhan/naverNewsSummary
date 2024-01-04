from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time
import datetime
from pytz import timezone

# 전처리 클래스
from preprocessing import Preprocessing
from database import selectToDay

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--log-level=3')  # 로그 레벨을 "INFO" 이상의 레벨로 설정
browser = webdriver.Chrome(options=options)
# ------------------------------------------- 준비 ------------------------------------------- #


# 기사 링크 크롤링
class UrlCrawling:
    def __init__(self):
        self.category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]

    def getSixUrl(self):    # 정치, 경제, 사회, 생활/문화, 세계, IT/과학
        six_url = []
        category_list = []

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
                category_list.append(self.category_names[category])
        
        six_url_df = pd.DataFrame({'category' : category_list,
                                   'six_url' : six_url})

        return six_url_df


    def getEntertainmentUrl(self):   # 연예
        # today = str(datetime.datetime.now(KST))[:11]  # 서울 기준 시간
        entertainment_url = []
        category_list = []
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
            category_list.append("연예")

        entertainment_url_df = pd.DataFrame({'category' : category_list,
                            'entertainment_url' : entertainment_url})

        return entertainment_url_df

    def getSportsUrl(self):    # 스포츠  (페이지마다 개수가 달라서 6페이지를 이동)
        # today = str(datetime.datetime.now(KST))[:11].replace('-', '')  # 서울 기준 시간
        sports_url = []
        category_list = []
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
            category_list.append("스포츠")

        sports_url_df = pd.DataFrame({'category' : category_list,
                                    'sports_url' : sports_url})
        
        return sports_url_df
    

# 기사 본문 크롤링
class ContentCrawling:
    def __init__(self):
        self.title = []
        self.content = []
        self.img = []
        self.summary = []          # 네이버 요약봇이 요약한 내용

    def getSixContent(self, url_list):  # 정치, 경제, 사회, 생활/문화, 세계, IT/과학
        title_list = []
        content_list = []
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
                print(cnt, end=", ")
            
            cnt+=1
            
            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            try:
                title_list.extend(soup.select("#title_area span"))              # 제목 추가

                content = soup.find_all(attrs={"id" : "dic_area"})              # 본문 가져오기

                # 요약봇
                if summary_btn:
                    summary_content = soup.find(attrs={"class" : "_SUMMARY_CONTENT_BODY"})
                    try:
                        summary_content.find("strong").decompose()
                        self.summary.append(re.sub('다\.', '다.\n', summary_content.text))
                    except:
                        self.summary.append("")

                else:
                    self.summary.append("")
                
                self.getImg(soup, img_list)     # 이미지 추출

                content_list.extend(self.removeTag(content))                         # 본문 추가

            except IndexError:
                print("삭제된 기사")

        print()

        for i in range(len(title_list)):
            self.title.append(title_list[i].text)
            self.content.append(Preprocessing.clean(content_list[i].text))
            self.img.append(img_list[i])

    def getEntertainmentContent(self, url_list):    # 연예
        title_list = []
        content_list = []
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

                content = soup.find_all(attrs={"class" : "article_body"})             # 본문 가져오기

                self.getImg(soup, img_list)     # 이미지 추출

                content_list.extend(self.removeTag(content))                         # 본문 추가

            except IndexError:
                print("삭제된 기사")

        print()

        for i in range(len(title_list)):
            self.title.append(title_list[i].text)
            self.content.append(Preprocessing.clean(content_list[i].text))
            self.img.append(img_list[i])
            self.summary.append("")


    def getSportsContent(self, url_list):   # 스포츠
        title_list = []
        content_list = []
        img_list = []
        cnt = 1

        for url in url_list:

            browser.get(url)                                                    
            
            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            print(cnt, end=", ")
            cnt+=1
            try:
                title_list.extend(soup.select(".news_headline .title"))             # 제목 추가 

                content = soup.find_all(attrs={"class" : "news_end"})                     # 본문 가져오기

                self.getImg(soup, img_list)     # 이미지 추출

                content_list.extend(self.removeTag(content))                         # 본문 추가

            except IndexError:
                print("삭제된 기사")
        
        print()

        for i in range(len(title_list)):
            self.title.append(title_list[i].text)
            self.content.append(Preprocessing.clean(content_list[i].text))
            self.img.append(img_list[i])
            self.summary.append("")

    # 데이터프레임 생성
    def makeDataFrame(self, all_url, category):    # 수집한 데이터를 데이터프레임으로 변환

        data = {"category" : pd.Series(category),
                "title" : pd.Series(self.title),
                "content" : pd.Series(self.content),
                "img" : pd.Series(self.img),
                "url" : pd.Series(all_url),
                "summary" : pd.Series(self.summary)}

        news_df = pd.DataFrame(data)

        return news_df
    
    # 이미지 추출
    def getImg(self, soup, img_list):
        img_tag = soup.select(".end_photo_org img")                     # 이미지 가져오기

        if img_tag:                                                     # 이미지 있으면 이미지 주소만 추출해서 리스트로 만든다.
            img_src_list = []
            for img in img_tag:
                img_src_list.append(img['src'])
            img_list.append(",".join(img_src_list))
        else:
            img_list.append("")

    # 필요없는 태그 삭제
    def removeTag(self, content):

        while content[0].find("strong"): content[0].find("strong").decompose()
        while content[0].find("b"): content[0].find("b").decompose()
        while content[0].find(attrs={"class" : "end_photo_org"}): content[0].find(attrs={"class" : "end_photo_org"}).decompose()        # 본문 이미지에 있는 글자 없애기
        while content[0].find(attrs={"class" : "vod_player_wrap"}): content[0].find(attrs={"class" : "vod_player_wrap"}).decompose()    # 본문 영상에 있는 글자 없애기
        while content[0].find(attrs={"id" : "video_area"}): content[0].find(attrs={"id" : "video_area"}).decompose()                    # 본문 영상 없애기
        while content[0].find(attrs={"name" : "iframe"}): content[0].find(attrs={"name" : "iframe"}).decompose()
        while content[0].find(attrs={"class" : "image"}): content[0].find(attrs={"class" : "image"}).decompose()
        while content[0].find(attrs={"class" : "vod_area"}): content[0].find(attrs={"class" : "vod_area"}).decompose()                  # 본문 영상 없애기

        if content[0].find(attrs={"class" : "artical-btm"}): content[0].find(attrs={"class" : "artical-btm"}).decompose()               # 하단에 제보하기 칸 있으면 삭제
        if content[0].find(attrs={"class" : "caption"}): content[0].find(attrs={"class" : "caption"}).decompose()                       # 이미지 설명 없애기
        if content[0].find(attrs={"class" : "source"}): content[0].find(attrs={"class" : "source"}).decompose()
        if content[0].find(attrs={"class" : "byline"}): content[0].find(attrs={"class" : "byline"}).decompose()
        if content[0].find(attrs={"class" : "reporter_area"}): content[0].find(attrs={"class" : "reporter_area"}).decompose()
        if content[0].find(attrs={"class" : "copyright"}): content[0].find(attrs={"class" : "copyright"}).decompose()
        if content[0].find(attrs={"class" : "categorize"}): content[0].find(attrs={"class" : "categorize"}).decompose()
        if content[0].find(attrs={"class" : "promotion"}): content[0].find(attrs={"class" : "promotion"}).decompose()

        return content