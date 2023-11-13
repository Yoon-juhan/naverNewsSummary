import re

def clean(article):   # 전처리
    article = re.sub('\[.{1,15}\]','',article)
    article = re.sub('\w{2,4} 온라인 기자','',article)
    article = re.sub('\w+ 기자','',article)
    article = re.sub('\w{2,4}기자','',article)
    article = re.sub('\w+ 기상캐스터','',article)
    article = re.sub('사진','',article)
    article = re.sub('포토','',article)

    article = re.sub('\S+@[a-z.]+','',article)          # 이메일 삭제

    article = re.sub('\n','',article)
    article = re.sub('\t','',article)
    article = re.sub('\u200b','',article)
    article = re.sub('\xa0','',article)
    article = re.sub('[ㄱ-ㅎㅏ-ㅣ]+','',article)
    # article = re.sub('([a-zA-Z])','',article)   # 영어 삭제
    # article = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘’“”|\(\)\[\]\<\>`\'…》]','',article)   # 특수문자 삭제

    return article