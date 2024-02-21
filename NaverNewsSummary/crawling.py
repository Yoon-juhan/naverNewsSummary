from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import re
import time
import datetime
from tqdm.notebook import tqdm
import threading

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--log-level=3')  # 로그 레벨을 "INFO" 이상의 레벨로 설정
browser = webdriver.Chrome(options=options)

n = [5, 7] # 2~5, 1~7

# 기사 링크 크롤링
class UrlCrawling:
    def __init__(self):
        self.category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
        self.url_df_list = [None] * 8
        self.lock = threading.Lock()

    # "정치", "경제", "사회", "생활/문화", "세계", "IT/과학"
    def getUrl(self, category_num):
        a_tag_list = []
        urls = []
        category_list = []
        browser = webdriver.Chrome(options=options)

        url = f'https://news.naver.com/section/{category_num}'
        browser.get(url)

        # 기사 더보기 두 번 클릭
        browser.find_element(By.CLASS_NAME, "_CONTENT_LIST_LOAD_MORE_BUTTON").click()
        time.sleep(1)
        browser.find_element(By.CLASS_NAME, "_CONTENT_LIST_LOAD_MORE_BUTTON").click()
        time.sleep(1)

        soup = BeautifulSoup(browser.page_source, "html.parser")

        a_tag_list.extend(soup.select(".section_latest ._TEMPLATE .sa_thumb_link"))

        for a in a_tag_list:
            urls.append(a["href"])
            category_list.append(self.category_names[category_num-100])
        
        url_df = pd.DataFrame({'category' : category_list,
                               'url' : urls})

        with self.lock:
            self.url_df_list[category_num-100] = url_df

        browser.quit()


    # 연예
    def getEntertainmentUrl(self):
        a_tag_list = []
        urls = []
        category_list = []
        today = datetime.date.today()
        browser = webdriver.Chrome(options=options)

        for page in range(1, n[0]):  # (1, 5)
            url = f'https://entertain.naver.com/now#sid=106&date={today}&page={page}'
            browser.get(url)

            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")

            a_tag_list.extend(soup.select(".news_lst li>a"))


        for a in a_tag_list:
            urls.append("https://entertain.naver.com" + a["href"])
            category_list.append("연예")

        url_df = pd.DataFrame({'category' : category_list,
                               'url' : urls})

        with self.lock:
            self.url_df_list[6] = url_df
        
        browser.quit()


    # 스포츠
    def getSportsUrl(self):      
        a_tag_list = []
        urls = []
        category_list = []
        today = str(datetime.date.today()).replace('-', '')
        browser = webdriver.Chrome(options=options)
        category = ["kfootball", "wfootball", "kbaseball", "wbaseball", "basketball", "volleyball", "golf"]

        for i in range(n[1]):  # 7
            url = f'https://sports.news.naver.com/{category[i]}/news/index?isphoto=N&date={today}&page=1'
            browser.get(url)

            time.sleep(0.5)

            soup = BeautifulSoup(browser.page_source, "html.parser")
            a_tag_list.extend(soup.select(".news_list li>a"))


        for i in range(len(a_tag_list)):
            urls.append("https://sports.news.naver.com/news" + re.search('\?.+', a_tag_list[i]["href"]).group())
            category_list.append("스포츠")

        url_df = pd.DataFrame({'category' : category_list,
                               'url' : urls})
        
        with self.lock:
            self.url_df_list[7] = url_df

        browser.quit()

# 기사 본문 크롤링
class ContentCrawling:
    def __init__(self):
        self.category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]
        self.title = [[] for _ in range(8)]
        self.content = [[] for _ in range(8)]
        self.img = [[] for _ in range(8)]
        self.lock = threading.Lock()

    def getContent(self, url_list, category_num):  # 정치, 경제, 사회, 생활/문화, 세계, IT/과학
        title_list = []
        content_list = []
        img_list = []
        browser = webdriver.Chrome(options=options)

        for url in tqdm(url_list, desc=f"{self.category_names[category_num]} CONTENT"):
            flag = False
            browser.get(url)
            time.sleep(0.5)
            soup = BeautifulSoup(browser.page_source, "html.parser")

            try:
                title = soup.select("#title_area span")[0]
                content = soup.find_all(attrs={"id" : "dic_area"})
                self.getImg(soup, img_list)
                flag = True

            except IndexError:
                print("삭제된 기사")
                continue
            
            if flag:
                title_list.extend(title)
                content_list.extend(self.removeTag(content))
                
        with self.lock:
            for i in range(len(title_list)):
                try:
                    self.title[category_num].append(title_list[i].text)
                    self.content[category_num].append(cleanContent(content_list[i].text).strip())
                    self.img[category_num].append(img_list[i])
                except IndexError:
                    print(i, category_num)
                    print(content_list[i])
                    print(content[category_num])

        browser.quit()


    def getEntertainmentContent(self, url_list):    # 연예
        title_list = []
        content_list = []
        img_list = []
        browser = webdriver.Chrome(options=options)

        for url in tqdm(url_list, desc="연예 CONTENT"):
            flag = False
            browser.get(url)
            time.sleep(0.5)
            soup = BeautifulSoup(browser.page_source, "html.parser")

            try:
                title = soup.select(".end_tit")
                content = soup.find_all(attrs={"class" : "article_body"})
                self.getImg(soup, img_list)
                flag = True

            except IndexError:
                print("삭제된 기사")
                continue

            if flag:
                title_list.extend(title)
                content_list.extend(self.removeTag(content))
                
        with self.lock:
            for i in range(len(title_list)):
                self.title[6].append(title_list[i].text)
                self.content[6].append(cleanContent(content_list[i].text).strip())
                self.img[6].append(img_list[i])

        browser.quit()

    def getSportsContent(self, url_list):   # 스포츠
        title_list = []
        content_list = []
        img_list = []
        browser = webdriver.Chrome(options=options)

        for url in tqdm(url_list, desc="스포츠 CONTENT"):
            flag = False
            browser.get(url)                                                    
            time.sleep(0.5)
            soup = BeautifulSoup(browser.page_source, "html.parser")

            try:
                title = soup.select(".news_headline .title")
                content = soup.find_all(attrs={"class" : "news_end"})
                self.getImg(soup, img_list)
                flag = True

            except IndexError:
                print("삭제된 기사")
                continue
                
            if flag:
                title_list.extend(title)
                content_list.extend(self.removeTag(content))

        with self.lock:
            for i in range(len(title_list)):
                self.title[7].append(title_list[i].text)
                self.content[7].append(cleanContent(content_list[i].text).strip())
                self.img[7].append(img_list[i])

        browser.quit()

    # 데이터프레임 생성
    def makeDataFrame(self, all_url, category):    # 수집한 데이터를 데이터프레임으로 변환
        
        title, content, img = [], [], []
        for i in self.title:
            title.extend(i)
        for i in self.content:
            content.extend(i)
        for i in self.img:
            img.extend(i)

        data = {"category" : pd.Series(category),
                "title" : pd.Series(title),
                "content" : pd.Series(content),
                "img" : pd.Series(img),
                "url" : pd.Series(all_url)}

        news_df = pd.DataFrame(data)

        news_df.drop(news_df[news_df['content'].isna()].index, inplace=True)

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

        while content[0].find("strong"): content[0].find("strong").decompose()
        while content[0].find("small"): content[0].find("small").decompose()
        while content[0].find("table"): content[0].find("table").decompose()
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
    text = re.sub('\s{2,}',' ',text)
    text = re.sub('다\.(?=(?:[^"]*"[^"]*")*[^"]*$)', '다.\n', text)
    text = re.sub('[\t\xa0]','', text)
    text = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',text)
    text = re.sub('[=+#/^$@*※&ㆍ!』\\|\[\]\<\>`…》■□ㅁ◆◇▶◀▷◁△▽▲▼○●━]','',text)
    
        
    return text
    

# url 스레드
def urlThread(url_crawler):

    url_threads = []
    for category_num in range(100, 108):
        if category_num <= 105:
            url_thread = threading.Thread(target=url_crawler.getUrl, args=(category_num,))
        elif category_num == 106:
            url_thread = threading.Thread(target=url_crawler.getEntertainmentUrl)
        else:
            url_thread = threading.Thread(target=url_crawler.getSportsUrl)

        url_threads.append(url_thread)
        url_thread.start()

    for url_thread in url_threads:
        url_thread.join()


# 본문 스레드
def contentThread(url_crawler, content_crawler):

    url_list = []
    all_url_list = np.array([])
    category_list = np.array([])

    for i in range(8):
        url_list.append(list(url_crawler.url_df_list[i]['url']))
        all_url_list = np.append(all_url_list, url_crawler.url_df_list[i]['url'])
        category_list = np.append(category_list, url_crawler.url_df_list[i]['category'])

    content_threads = []
    for i in range(8):
        if i <= 5:
            content_thread = threading.Thread(target=content_crawler.getContent, args=(url_list[i], i))
        elif i == 6:
            content_thread = threading.Thread(target=content_crawler.getEntertainmentContent, args=(url_list[i],))
        else:
            content_thread = threading.Thread(target=content_crawler.getSportsContent, args=(url_list[i],))
        content_threads.append(content_thread)
        content_thread.start()

    for content_thread in content_threads:
        content_thread.join()

    news_df = content_crawler.makeDataFrame(all_url_list, category_list)                      # 본문 데이터프레임 생성

    return news_df


# 크롤링 시작
def startCrawling():
    url_crawler = UrlCrawling()
    content_crawler = ContentCrawling()

    urlThread(url_crawler)

    news_df = contentThread(url_crawler, content_crawler)

    return news_df