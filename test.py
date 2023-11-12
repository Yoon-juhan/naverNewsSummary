# coding: utf-8
from gensim.summarization.summarizer import summarize

txt = """기사"""

result = summarize(txt, ratio=0.1)

# text (String, 필수) : 요약하고자하는 텍스트 원문
# ratio (Float, 선택적) : 텍스트 원문에 대한 요약 비율
# word_count (Int, 선택적) : 요약문에 포함될 단어의 수. ratio 인자와 같이 사용시 word_count 인자 우선함
# spilt (Bool, 선택적) : True로 전달하면 list 형태로 반환, False로 전달하면 String으로 반환

print(result)