from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from s3 import MinIO
from transcribe import Transcribe
import uvicorn
import boto3
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
MINIO_USER = os.getenv('MINIO_USER')
MINIO_PASS = os.getenv('MINIO_PASS')
MINIO_SERVER_PORT = os.getenv('MINIO_SERVER_PORT')
MINIO_HOST = os.getenv('MINIO_HOST')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
FIREFLIES_API_KEY = os.getenv('FIREFLIES_API_KEY')
app = FastAPI()
minio = MinIO(
    key = MINIO_USER,
    secret_key=MINIO_PASS,
    endpoint_url=f"http://{MINIO_HOST}:{MINIO_SERVER_PORT}"
)
transcribe = Transcribe('https://api.fireflies.ai/graphql', FIREFLIES_API_KEY)
# Модель для результата обработки
class ProcessingResult(BaseModel):
    status: str
    result: dict

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    # Загрузка файла в S3
    try:
        file_content = file.file.read()
        filename = file.filename
        minio.upload_file(file_content, filename)
        public_url = f"http://{MINIO_HOST}:{MINIO_SERVER_PORT}/{MINIO_BUCKET_NAME}/{filename}"
        id = transcribe.upload_audio(public_url, filename)
        return id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-result/{file_name}")
async def check_result(audio_id: int):
    response = transcribe.get_transcription_result(audio_id=audio_id)
    return response

@app.post("/extract-tags/")
async def extract_tags(text: str):
    # Простой пример обработки текста для извлечения тегов
    tags = text.split()  # Здесь можно использовать более сложную логику обработки текста
    return {"tags": list(set(tags))}  # Возвращаем уникальные теги
    chunk_spliter = ChunkSpliter(model=model)
    chunks = chunk_spliter.split(text)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)