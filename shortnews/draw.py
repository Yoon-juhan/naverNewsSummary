from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
from math import pi
import numpy as np
from database import selectToDay
plt.rcParams['font.family'] = 'HYkanB'
plt.rcParams['axes.unicode_minus'] = False

def drawKeyword():

    toDay_df = selectToDay()

    category_names = ["정치", "경제", "사회", "생활/문화", "세계", "IT/과학", "연예", "스포츠"]

    for cate_id in range(100, 108):
    
        toDay_keyword = toDay_df['KEYWORD'][toDay_df['CATE_ID'] == str(cate_id)].str.split(',').explode().tolist()
        count = Counter(toDay_keyword).most_common(10)

        x = [data[0] for data in count] # 키워드
        y = [data[1] for data in count] # 개수

        df = pd.DataFrame(y, x)
        df = df.T
        max_keyword = df.iloc[0][0]

        # 순서를 랜덤으로 섞어서 그림 (안 섞으면 항상 같은 모양에 크기만 다름)
        random_columns = np.random.permutation(df.columns)
        random_df = df[random_columns]
        
        y_ticks = np.linspace(0, max_keyword, 6)
        y_ticks_name = [str(int(i)) for i in y_ticks]

        labels = random_df.columns         # 키워드들
        num_labels = len(labels)    # 키워드 개수 (10개)

        angles = [x / float(num_labels) * (2 * pi) for x in range(num_labels)]    # 각 등분점
        angles.append(angles[0])    # 시작점으로 다시 돌아와야하므로 시작점 추가

        # my_palette = plt.cm.get_cmap("Set2", 8)   # 색상
        my_color = ["#ff7373", "#ffa570", "#fdf250", "#50fd50", "#58ecff", "#5599ff", "#ac79ff", "#ff79f4"] # 무지개 색상

        fig = plt.figure(figsize=(8, 10))
        fig.set_facecolor('white') 

        color = my_color[cate_id - 100]
        data = random_df.iloc[0].tolist()
        data.append(data[0])

        ax = plt.subplot(polar=True)
        ax.set_theta_offset(pi / 2)     # 시작점
        ax.set_theta_direction(-1)      # 그려지는 방향 시계방향
        plt.xticks(angles[:-1], labels, fontsize=13)    # x축 눈금 라벨
        ax.tick_params(axis='x', which='major', pad=15) # x축과 눈금 사이에 여백을 준다.

        ax.set_rlabel_position(0)       # y축 각도 설정(degree 단위)

        plt.yticks(y_ticks, y_ticks_name, fontsize=10)  # y축 눈금 설정
        plt.ylim(0, max_keyword)

        ax.plot(angles, data, color=color, linewidth=1, linestyle='solid')  # 레이더 차트 출력
            
        ax.fill(angles, data, color=color, alpha=0.4)   # 도형 안쪽에 색을 채우기
        plt.title(category_names[cate_id-100], size=20, color="black",x=0.5, y=1.2, ha='center')  # 타이틀은 카테고리

        plt.savefig(f'keyword_img/test{cate_id}.png')