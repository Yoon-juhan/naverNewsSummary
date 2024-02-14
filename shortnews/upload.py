import boto3
import datetime
from database import selectHour

def s3_connection():
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id="AKIAXUNXPSJYGJOXT55C",
            aws_secret_access_key="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",
        )
    except Exception as e:
        print(e)
    else:
        print("연결 성공") 
        return s3

# 워드 클라우드 업로드
def upload_img():
    s3 = s3_connection()

    now = datetime.datetime.now()
    now = str(now.year) + str(now.month).zfill(2) + str(now.day).zfill(2)

    try:
        for i in range(100, 109):
            s3.upload_file(f"word_cloud/{now}_{i}.jpg", "snewsimgs", f"{now}_{i}.jpg") # "{로컬 파일 이름}, {버킷 이름}, {실제로 저장될 이름}"
        print("이미지 업로드 성공")
    except Exception as e:
        print("이미지 업로드 실패", e)

# TTS mp3 업로드
def upload_mp3():
    s3 = s3_connection()
    df = selectHour()

    # for i in range(len(df)):
    for i in range(2):  # 테스트용
        try:
            s3.upload_file(f"tts_mp3/{df['NEWS_ID'][i]}_female.mp3", "snewstts", f"{df['NEWS_ID'][i]}_female.mp3") # "{로컬 파일 이름}, {버킷 이름}, {실제로 저장될 이름}"
            s3.upload_file(f"tts_mp3/{df['NEWS_ID'][i]}_male.mp3", "snewstts", f"{df['NEWS_ID'][i]}_male.mp3") # "{로컬 파일 이름}, {버킷 이름}, {실제로 저장될 이름}"
        except Exception as e:
            print(f"{df['NEWS_ID'][i]} mp3 업로드 실패", e)
    
    print("mp3 업로드 성공")

# 가져오기
# obj = s3.get_object(Bucket="snewstts", Key = "test.html")
# print(obj)