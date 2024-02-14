from fastapi import FastAPI, Request
from SearchService import *
from http import HTTPStatus
from fastapi.middleware.cors import CORSMiddleware

#127.0.0.1:8000/main/recommend
app = FastAPI()
origins = ["*"]
# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/main/search/{keyword}')
async def search(keyword : str) -> dict:
    result = {"query" : await query(keyword)}

    return result


# uvicorn main2:app --reload