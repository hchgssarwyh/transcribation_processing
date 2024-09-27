FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install spacy==3.5.0 pydantic==1.10.7
RUN python -m spacy download ru_core_news_sm
COPY . .
CMD ["uvicorn", "main:app", "--host", "localhost", "--port", "8000"]