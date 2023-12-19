drop table news;

create table news(
news_id VARCHAR2(50) PRIMARY KEY,
cate_id VARCHAR2(100),
title VARCHAR2(1000),
content CLOB,
img VARCHAR2(1000),
link VARCHAR2(1000),
views NUMBER
);

drop sequence news_id_seq;

create sequence news_id_seq
start with 1
increment by 1
maxvalue 1920
cycle;

select * from news
order by to_number(news_id);