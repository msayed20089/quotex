FROM python:3.10-slim

# تثبيت المتطلبات النظامية
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# تثبيت متطلبات البايثون
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت Playwright والمتصفح
RUN playwright install chromium
RUN playwright install-deps

CMD ["python3", "main.py"]
