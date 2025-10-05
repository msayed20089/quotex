FROM selenium/standalone-chrome:latest

# تثبيت بايثون والمتطلبات
USER root

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملفات المشروع
WORKDIR /app
COPY . .

# تثبيت متطلبات البايثون
RUN pip3 install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python3", "main.py"]
