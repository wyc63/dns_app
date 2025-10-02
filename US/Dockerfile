FROM python:3.9-slim

WORKDIR /app

COPY app.py .

RUN pip install --no-cache-dir flask requests

EXPOSE 8080

CMD ["python", "app.py"]
