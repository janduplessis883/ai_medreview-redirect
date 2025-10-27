FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD gunicorn -b 0.0.0.0:$PORT --workers 2 --threads 8 app:app
