from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import time
import logging

class QXBrokerManager:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.setup_driver()
    
    def setup_driver(self):
        """إعداد متصفح Chrome للعمل على Railway"""
        chrome_options = Options()
        
        # إعدادات ضرورية للعمل على Railway
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # إعدادات خاصة بـ Railway
        chrome_options.binary_location = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
        
        try:
            # استخدام Chrome الموجود في النظام
            service = Service(executable_path="/usr/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("✅ تم إعداد ChromeDriver بنجاح على Railway")
        except Exception as e:
            logging.error(f"❌ خطأ في إعداد ChromeDriver: {e}")
            # محاولة بديلة
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logging.info("✅ تم إعداد ChromeDriver بالطريقة البديلة")
            except Exception as e2:
                logging.error(f"❌ فشل جميع محاولات إعداد ChromeDriver: {e2}")
                raise
    
    def login(self):
        """تسجيل الدخول إلى منصة QX Broker"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logging.info(f"🔄 محاولة الدخول {attempt + 1}/{max_retries}")
                
                self.driver.get(QX_CREDENTIALS['login_url'])
                
                # الانتظار لحين تحميل صفحة الدخول
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                
                # إدخال البريد الإلكتروني
                email_field = self.driver.find_element(By.NAME, "email")
                email_field.clear()
                email_field.send_keys(QX_CREDENTIALS['email'])
                
                # إدخال كلمة المرور
                password_field = self.driver.find_element(By.NAME, "password")
                password_field.clear()
                password_field.send_keys(QX_CREDENTIALS['password'])
                
                # النقر على زر الدخول
                login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                
                # الانتظار للتأكد من نجاح الدخول
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
                )
                
                self.is_logged_in = True
                logging.info("✅ تم تسجيل الدخول بنجاح إلى QX Broker")
                return True
                
            except Exception as e:
                logging.error(f"❌ فشل محاولة الدخول {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    logging.error("❌ فشل جميع محاولات الدخول")
                    return False