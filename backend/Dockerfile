FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /app/data
ENV DATABASE_URL=sqlite:////app/data/tutor.db
ENV TEXTBOOK_INDEX=/textbooks/index.json
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

