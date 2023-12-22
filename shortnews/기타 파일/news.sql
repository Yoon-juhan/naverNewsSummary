drop table news;

CREATE TABLE NEWS(
NEWS_ID VARCHAR2(50),
CATE_ID VARCHAR2(10),
TITLE VARCHAR2(100),
CONTENT VARCHAR2(1000),
VIEWS NUMBER,
URL VARCHAR2(1000),
IMGS VARCHAR2(1000),
CONSTRAINT NEWS_NEWSID_PK PRIMARY KEY(NEWS_ID),
CONSTRAINT NEWS_CATEID_FK FOREIGN KEY(CATE_ID) REFERENCES CATE (CATE_ID)
);

drop sequence news_seq;

create sequence news_seq
increment by 1
start with 1
maxvalue 1920
cycle;

select * from news
order by to_number(news_id);