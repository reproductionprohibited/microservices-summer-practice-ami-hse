FROM python:3.11-slim

WORKDIR /code

COPY restaurant-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY restaurant-service/main.py /code/main.py
COPY common /code/common

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]