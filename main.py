from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uvicorn
import boto3
import requests
import time
from utils impor ChunkSpliter

app = FastAPI()



# Инициализация клиента S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

# Модель для результата обработки
class ProcessingResult(BaseModel):
    status: str
    result: dict

@app.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    # Загрузка файла в S3
    try:
        s3_client.upload_fileobj(file.file, S3_BUCKET, file.filename)
        # Отправка запроса на обработку в другой сервис
        response = requests.post("https://other-service.com/process", json={"file_name": file.filename})
        return {"message": "File uploaded and processing started.", "response": response.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check-result/{file_name}")
async def check_result(file_name: str):
    # Проверка результата обработки
    response = requests.get(f"https://other-service.com/results/{file_name}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching result.")
    
    result = response.json()
    
    if result['status'] == 'processed':
        return result['result']
    
    raise HTTPException(status_code=202, detail="Processing still in progress.")

@app.post("/extract-tags/")
async def extract_tags(text: str):
    # Простой пример обработки текста для извлечения тегов
    tags = text.split()  # Здесь можно использовать более сложную логику обработки текста
    return {"tags": list(set(tags))}  # Возвращаем уникальные теги
    chunk_spliter = ChunkSpliter(model=model)
    chunks = chunk_spliter.split(text)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)