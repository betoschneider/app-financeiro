# Dockerfile
FROM python:3.12.3-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ /app/src/

EXPOSE 8501

CMD ["streamlit", "run", "src/principal.py"]
