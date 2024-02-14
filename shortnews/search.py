from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import re
import time
from datetime import datetime, timedelta
from tqdm.notebook import tqdm
from summa.summarizer import summarize
import threading

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--log-level=3')  # 로그 레벨을 "INFO" 이상의 레벨로 설정
browser = webdriver.Chrome(options=options)

def getUrl(query):
    a_tag_list = []
    urls = []
    url = f'https://search.naver.com/search.naver?where=news&ie=utf8&sm=nws_hty&query={query}'
    browser.get(url)
    browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(1)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    a_tag_list.extend(soup.find_all(attrs={"class" : "info"}, string="네이버뉴스"))
    # print(a_tag_list)
    for a in a_tag_list:
        urls.append(a["href"])
    return urls
# 제목, 본문, 날짜, 카테고리, 이미지, url

# 기사 본문 크롤링
class SearchContentCrawling:
    def __init__(self):
        self.category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
        self.category = []
        self.title = []
        self.content = []
        self.img = []
        self.date = []
        self.url = []
        self.lock = threading.Lock()

    def getContent(self, url, category_num, browser):  # 정치, 경제, 사회, 생활/문화, 세계, IT/과학

        img_list = []
        
        flag = False
        browser.get(url)
        time.sleep(0.5)
        soup = BeautifulSoup(browser.page_source, "html.parser")

        try:
            title = soup.select("#title_area span")[0]
            content = soup.find(attrs={"id" : "dic_area"})
            date = soup.select(".media_end_head_info_datestamp_time")[0]
            self.getImg(soup, img_list)
            flag = True

        except IndexError:
            print("삭제된 기사 :", url)

        with self.lock:
            if flag:
                self.category.append(self.category_names[category_num-100])
                self.title.append(cleanTitle(title.text))
                self.content.append(cleanContent(self.removeTag(content).text))
                self.img.append(img_list)
                self.date.append(dateFormat(date.text))
                self.url.append(url)

            

    def getEntertainmentContent(self, url, browser):    # 연예

        img_list = []

        flag = False
        browser.get(url)
        time.sleep(0.5)
        soup = BeautifulSoup(browser.page_source, "html.parser")

        try:
            title = soup.select(".end_tit")[0]
            content = soup.find(attrs={"class" : "article_body"})
            date = soup.select(".author em")[0]
            self.getImg(soup, img_list)
            flag = True

        except IndexError:
            print("삭제된 기사 :", url)


        with self.lock:
            if flag:
                self.category.append("연예")
                self.title.append(cleanTitle(title.text))
                self.content.append(cleanContent(self.removeTag(content).text))
                self.img.append(img_list)
                self.date.append(dateFormat(date.text))
                self.url.append(url)

    def getSportsContent(self, url, browser):   # 스포츠

        img_list = []

        flag = False
        browser.get(url)                                                    
        time.sleep(0.5)
        soup = BeautifulSoup(browser.page_source, "html.parser")

        try:
            title = soup.select(".news_headline .title")[0]
            content = soup.find(attrs={"class" : "news_end"})
            date = soup.select(".info span")[0]
            self.getImg(soup, img_list)
            flag = True

        except IndexError:
            print("삭제된 기사 :", url)

                
        with self.lock:
            if flag:
                self.category.append("스포츠")
                self.title.append(cleanTitle(title.text))
                self.content.append(cleanContent(self.removeTag(content).text))
                self.img.append(img_list)
                self.date.append(dateFormat(date.text))
                self.url.append(url)

    # 데이터프레임 생성
    def makeDataFrame(self):    # 수집한 데이터를 데이터프레임으로 변환

        data = {"category" : pd.Series(self.category),
                "date" : pd.Series(self.date),
                "title" : pd.Series(self.title),
                "content" : pd.Series(self.content),
                "img" : pd.Series(self.img),
                "url" : pd.Series(self.url)}
        
        news_df = pd.DataFrame(data)

        # news_df.drop(news_df[news_df['content'].isna()].index, inplace=True)
        # news_df.drop(news_df[news_df['title'].str.contains('사진|포토|영상|움짤|헤드라인|라이브|정치쇼')].index, inplace=True)
        # news_df.drop(news_df[news_df['content'].str.contains('방송 :|방송:|진행 :|진행:|출연 :|출연:|앵커|[앵커]')].index, inplace=True)

        return news_df
    
    # 이미지 추출
    def getImg(self, soup, img_list):
        img_tag = soup.select(".end_photo_org img")                     # 이미지 가져오기

        if img_tag:                                                     # 이미지 있으면 이미지 주소만 추출해서 리스트로 만든다.
            img_src_list = []
            for img in img_tag:
                if len(img_src_list) <= 10:                             # 최대 이미지 10개
                    if '.gif' not in img['src']:
                        img_src_list.append(img['src'])
            img_list.append(",".join(img_src_list))
        else:
            img_list.append("")

        # 필요없는 태그 삭제
    def removeTag(self, content):

        while content.find("strong"): content.find("strong").decompose()
        while content.find("small"): content.find("small").decompose()
        while content.find("table"): content.find("table").decompose()
        while content.find("b"): content.find("b").decompose()
        while content.find(attrs={"class" : "end_photo_org"}): content.find(attrs={"class" : "end_photo_org"}).decompose()        # 본문 이미지에 있는 글자 없애기
        while content.find(attrs={"class" : "vod_player_wrap"}): content.find(attrs={"class" : "vod_player_wrap"}).decompose()    # 본문 영상에 있는 글자 없애기
        while content.find(attrs={"id" : "video_area"}): content.find(attrs={"id" : "video_area"}).decompose()                    # 본문 영상 없애기
        while content.find(attrs={"name" : "iframe"}): content.find(attrs={"name" : "iframe"}).decompose()
        while content.find(attrs={"class" : "image"}): content.find(attrs={"class" : "image"}).decompose()
        while content.find(attrs={"class" : "vod_area"}): content.find(attrs={"class" : "vod_area"}).decompose()                  # 본문 영상 없애기

        if content.find(attrs={"class" : "artical-btm"}): content.find(attrs={"class" : "artical-btm"}).decompose()               # 하단에 제보하기 칸 있으면 삭제
        if content.find(attrs={"class" : "caption"}): content.find(attrs={"class" : "caption"}).decompose()                       # 이미지 설명 없애기
        if content.find(attrs={"class" : "source"}): content.find(attrs={"class" : "source"}).decompose()
        if content.find(attrs={"class" : "byline"}): content.find(attrs={"class" : "byline"}).decompose()
        if content.find(attrs={"class" : "reporter_area"}): content.find(attrs={"class" : "reporter_area"}).decompose()
        if content.find(attrs={"class" : "copyright"}): content.find(attrs={"class" : "copyright"}).decompose()
        if content.find(attrs={"class" : "categorize"}): content.find(attrs={"class" : "categorize"}).decompose()
        if content.find(attrs={"class" : "promotion"}): content.find(attrs={"class" : "promotion"}).decompose()

        return content

# 본문 전처리
def cleanContent(text):
    text = re.sub('\([^)]+\)', '', text)
    text = re.sub('\[[^\]]+\]','',text)
    text = re.sub('([^\s]*\s기자)','',text)
    text = re.sub('([^\s]*\온라인 기자)','',text)
    text = re.sub('([^\s]*\s기상캐스터)','',text)
    text = re.sub('포토','',text)
    text = re.sub('\S+@[a-z.]+','',text)
    text = re.sub('[“”]','"',text)
    text = re.sub('[‘’]','\'',text)
    text = re.sub('다\.(?=(?:[^"]*"[^"]*")*[^"]*$)', '다.\n', text)
    text = re.sub('\t\xa0','', text)
    text = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',text)
    text = re.sub('[=+#/^$@*※&ㆍ!』\\|\[\]\<\>`…》■□ㅁ◆◇▶◀▷◁△▽▲▼○●━]','',text)
    
    return text

# 제목 전처리
def cleanTitle(text):
    title = text
    title = re.sub('\([^)]+\)', '', title)
    title = re.sub('\[[^\]]+\]', '',title)
    title = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',title)
    title = re.sub('[“”]','"',title)
    title = re.sub('[‘’]','\'',title)
    title = re.sub('\.{2,3}','...',title)
    title = re.sub('…','...',title)
    title = re.sub('\·{3}','...',title)
    title = re.sub('[=+#/^$@*※&ㆍ!』\\|\<\>`》■□ㅁ◆◇▶◀▷◁△▽▲▼○●━]','',title)

    if not title:   # 제목이 다 사라졌으면 원래 제목으로
        title = text

    return title.strip()

def dateFormat(date):

    if "오전" in date:
        date = date.replace("오전", "")
        date_object = datetime.strptime(date, "%Y.%m.%d. %I:%M")
    elif "오후" in date:
        date = date.replace("오후", "")
        date_object = datetime.strptime(date, "%Y.%m.%d. %I:%M") + timedelta(hours=12)
    
    formatted_date = date_object.strftime("%Y%m%d%H")

    return formatted_date


# 검색 시작
async def query(query):
    urls = getUrl(query)
    urls = list(set(urls))
    crawler = SearchContentCrawling()

    # urls1 = urls[:len(urls) // 2]
    # urls2 = urls[len(urls) // 2:]

    urls1 = urls[:len(urls) // 3]
    urls2 = urls[len(urls) // 3:len(urls) // 3 + 3]
    urls3 = urls[len(urls) // 3 + 3:]

    def getContent(urls):
        browser = webdriver.Chrome(options=options)

        for url in urls:
            catgory = int(url[-3:])
            if catgory in [100, 101, 102, 103, 104, 105]:
                crawler.getContent(url, catgory, browser)
            elif catgory == 106:
                crawler.getEntertainmentContent(url, browser)
            else:
                crawler.getSportsContent(url, browser)
    
    # 여기서 스레드로 분리
    content_thread1 = threading.Thread(target=getContent, args=(urls1,))
    content_thread2 = threading.Thread(target=getContent, args=(urls2,))
    content_thread3 = threading.Thread(target=getContent, args=(urls3,))
    content_thread1.start()
    content_thread2.start()
    content_thread3.start()
    content_thread1.join()
    content_thread2.join()
    content_thread3.join()


    # 데이터프레임 생성
    news_df = crawler.makeDataFrame()
    news_df["content"] = news_df["content"].apply(lambda x : summarize(x, words=60))

    dict = news_df.to_dict(orient='records')

    return dict