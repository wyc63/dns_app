FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN pip install --no-cache-dir flask

EXPOSE 9090

CMD ["python", "app.py"]
