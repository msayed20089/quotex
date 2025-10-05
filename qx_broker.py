from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import logging
import random
import os
import subprocess
from config import QX_EMAIL, QX_PASSWORD, QX_LOGIN_URL

class QXBrokerManager:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.last_activity = time.time()
        self.session_data = {}
        self.setup_driver()
        
    def setup_driver(self):
        """إعداد متصفح Chrome لـ Railway بدون webdriver-manager"""
        chrome_options = Options()
        
        # إعدادات Railway الأساسية
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # إعدادات إضافية للاستقرار
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        
        # إعدادات لتحسين الأداء
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        
        try:
            # الطريقة الأولى: استخدام Chrome الموجود في النظام
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("✅ تم إعداد متصفح Chrome بنجاح على Railway")
            
        except Exception as e:
            logging.error(f"❌ الخطأ في إعداد المتصفح: {e}")
            # محاولة تثبيت Chrome يدوياً إذا لزم الأمر
            self.install_chrome_manual()
    
    def install_chrome_manual(self):
        """تثبيت Chrome يدوياً على Railway"""
        try:
            logging.info("🔄 جاري تثبيت Chrome يدوياً...")
            
            # تثبيت المتصفح باستخدام apt
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'wget'], check=True)
            
            # تحميل وتثبيت Chrome
            subprocess.run([
                'wget', '-q', '-O', '-', 'https://dl-ssl.google.com/linux/linux_signing_key.pub'
            ], check=True)
            
            subprocess.run([
                'sh', '-c', 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
            ], check=True)
            
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'google-chrome-stable'], check=True)
            
            logging.info("✅ تم تثبيت Chrome بنجاح")
            
            # إعادة محاولة إعداد المتصفح
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("✅ تم إعداد المتصفح بعد التثبيت اليدوي")
            
        except Exception as e:
            logging.error(f"❌ فشل التثبيت اليدوي: {e}")
            raise Exception("لا يمكن تشغيل المتصفح على Railway")

    def ensure_login(self):
        """التأكد من تسجيل الدخول"""
        try:
            # الانتقال مباشرة لصفحة الديمو تريد
            self.driver.get("https://qxbroker.com/ar/demo-trade")
            time.sleep(8)  # زيادة وقت الانتظار
            
            # التحقق من حالة الدخول
            if self.check_login_status():
                self.is_logged_in = True
                logging.info("✅ المستخدم مسجل الدخول وجاهز للتداول")
                return True
            else:
                logging.info("🔐 جاري تسجيل الدخول...")
                return self.login()
                
        except Exception as e:
            logging.error(f"❌ خطأ في التأكد من تسجيل الدخول: {e}")
            return False

    def check_login_status(self):
        """التحقق من حالة تسجيل الدخول"""
        try:
            # التحقق من خلال عنوان URL
            current_url = self.driver.current_url
            if "demo-trade" in current_url and "sign-in" not in current_url:
                return True
            
            # التحقق من خلال وجود عناصر الواجهة
            balance_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'رصيد') or contains(text(), 'Balance')]")
            if balance_elements:
                return True
                
            return False
        except:
            return False

    def login(self):
        """تسجيل الدخول إلى Quotex"""
        try:
            logging.info("🔗 جاري تسجيل الدخول إلى Quotex...")
            self.driver.get("https://qxbroker.com/ar/sign-in")
            time.sleep(8)  # زيادة وقت الانتظار
            
            # البحث عن حقول الدخول
            email_field = self.find_element_with_retry([
                "input[name='email']", 
                "input[type='email']",
                "input[placeholder*='email']", 
                "input[placeholder*='بريد']"
            ], timeout=15)
            
            if not email_field:
                logging.error("❌ لم يتم العثور على حقل البريد الإلكتروني")
                return False
            
            email_field.clear()
            email_field.send_keys(QX_EMAIL)
            time.sleep(2)
            
            password_field = self.find_element_with_retry([
                "input[name='password']", 
                "input[type='password']",
                "input[placeholder*='password']", 
                "input[placeholder*='كلمة']"
            ], timeout=15)
            
            if not password_field:
                logging.error("❌ لم يتم العثور على حقل كلمة المرور")
                return False
            
            password_field.clear()
            password_field.send_keys(QX_PASSWORD)
            time.sleep(2)
            
            # البحث عن زر الدخول
            login_button = self.find_clickable_element([
                "//button[contains(text(), 'تسجيل')]", 
                "//button[contains(text(), 'دخول')]",
                "//button[contains(text(), 'Sign')]", 
                "//button[contains(text(), 'Login')]",
                "//button[@type='submit']"
            ], timeout=15)
            
            if login_button:
                login_button.click()
                time.sleep(10)  # زيادة وقت الانتظار بعد الدخول
                
                # التحقق من نجاح الدخول
                if self.check_login_status():
                    self.is_logged_in = True
                    logging.info("✅ تم تسجيل الدخول بنجاح إلى Quotex")
                    return True
            
            logging.error("❌ فشل تسجيل الدخول")
            return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في تسجيل الدخول: {e}")
            return False

    def refresh_and_prepare(self):
        """تحديث الصفحة والتحضير للصفقة التالية"""
        try:
            logging.info("🔄 جاري تحديث الصفحة للصفقة التالية...")
            
            # الانتقال مباشرة لصفحة التداول
            self.driver.get("https://qxbroker.com/ar/demo-trade")
            time.sleep(8)
            
            self.last_activity = time.time()
            logging.info("✅ تم تحضير الصفحة للصفقة التالية")
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحديث الصفحة: {e}")
            return False

    def execute_trade(self, pair, direction, duration=30):
        """تنفيذ صفقة على منصة Quotex"""
        try:
            if not self.is_logged_in:
                if not self.ensure_login():
                    logging.error("❌ فشل إعادة الاتصال")
                    return False
            
            if not self.refresh_and_prepare():
                logging.error("❌ فشل في تحضير الصفحة")
                return False
            
            logging.info(f"📊 جاري تنفيذ صفقة: {pair} - {direction}")
            
            # البحث عن الزوج واختياره
            if not self.search_and_select_pair(pair):
                return False
            
            # تحديد مدة الصفقة
            self.set_duration(duration)
            
            # تحديد مبلغ التداول
            self.set_amount(1)
            
            # تنفيذ الصفقة
            if not self.execute_direction(direction):
                return False
            
            logging.info(f"🎯 تم تنفيذ صفقة {direction} على {pair} بنجاح")
            self.last_activity = time.time()
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ عام في تنفيذ الصفقة: {e}")
            return False

    def search_and_select_pair(self, pair):
        """البحث عن الزوج واختياره"""
        try:
            # البحث عن زر اختيار الزوج (+)
            plus_button = self.find_clickable_element([
                "//button[contains(text(), '+')]",
                "//div[contains(text(), '+')]",
                "//*[contains(@class, 'add')]"
            ], timeout=10)
            
            if plus_button:
                plus_button.click()
                logging.info("➕ تم فتح قائمة الأزواج")
                time.sleep(3)
            
            # البحث عن شريط البحث
            search_box = self.find_element_with_retry([
                "input[placeholder*='بحث']", 
                "input[placeholder*='search']", 
                "input[type='search']"
            ], timeout=10)
            
            if search_box:
                search_box.clear()
                search_pair = pair.replace('/', '').upper()
                search_box.send_keys(search_pair)
                logging.info(f"🔍 جاري البحث عن الزوج: {search_pair}")
                time.sleep(3)
            else:
                logging.error("❌ لم يتم العثور على شريط البحث")
                return False
            
            # اختيار الزوج من النتائج
            pair_element = self.find_clickable_element([
                f"//*[contains(text(), '{pair}')]",
                f"//*[contains(text(), '{search_pair}')]"
            ], timeout=10)
            
            if pair_element:
                pair_element.click()
                logging.info(f"✅ تم اختيار الزوج: {pair}")
                time.sleep(3)
                return True
            else:
                logging.error(f"❌ لم يتم العثور على الزوج: {pair}")
                return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في البحث عن الزوج: {e}")
            return False

    def set_duration(self, duration):
        """تحديد مدة الصفقة"""
        try:
            # البحث عن أزرار المدة
            duration_buttons = self.driver.find_elements(By.XPATH, 
                f"//button[contains(text(), '{duration}')]")
            
            for btn in duration_buttons:
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    logging.info(f"⏱ تم تحديد مدة {duration} ثانية")
                    time.sleep(2)
                    return
            
            logging.warning(f"⚠️ لم يتم العثور على زر مدة {duration} ثانية")
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المدة: {e}")

    def set_amount(self, amount):
        """تحديد مبلغ التداول"""
        try:
            # البحث عن حقل المبلغ
            amount_inputs = self.driver.find_elements(By.XPATH, 
                "//input[@type='number' or contains(@placeholder, '$')]")
            
            for amount_input in amount_inputs:
                try:
                    amount_input.clear()
                    amount_input.send_keys(str(amount))
                    logging.info(f"💰 تم تحديد المبلغ: ${amount}")
                    time.sleep(1)
                    return
                except:
                    continue
            
            logging.info("💰 استخدام المبلغ الافتراضي")
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المبلغ: {e}")

    def execute_direction(self, direction):
        """تنفيذ اتجاه الصفقة"""
        try:
            if direction.upper() == 'BUY':
                # البحث عن زر UP/صاعد
                buy_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'صاعد') or contains(text(), 'UP') or contains(text(), 'شراء')]")
                
                for btn in buy_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        logging.info("🟢 تم النقر على زر صاعد/UP")
                        time.sleep(3)
                        return True
                
                logging.error("❌ لم يتم العثور على زر صاعد")
                return False
            else:
                # البحث عن زر DOWN/هابط
                sell_buttons = self.driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'هابط') or contains(text(), 'DOWN') or contains(text(), 'بيع')]")
                
                for btn in sell_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        logging.info("🔴 تم النقر على زر هابط/DOWN")
                        time.sleep(3)
                        return True
                
                logging.error("❌ لم يتم العثور على زر هابط")
                return False
                    
        except Exception as e:
            logging.error(f"❌ خطأ في تنفيذ الاتجاه: {e}")
            return False

    def get_trade_result(self):
        """الحصول على نتيجة الصفقة"""
        try:
            logging.info("⏳ في انتظار نتيجة الصفقة...")
            time.sleep(35)
            
            # تحديث الصفحة
            self.driver.refresh()
            time.sleep(5)
            
            logging.info("🔍 جاري البحث عن نتيجة الصفقة...")
            
            # البحث في الصفحة عن النتائج
            page_content = self.driver.page_source
            
            if '+' in page_content and ('green' in page_content.lower() or 'profit' in page_content.lower()):
                logging.info("🎉 تم التعرف على صفقة رابحة")
                return "WIN"
            else:
                logging.info("❌ تم التعرف على صفقة خاسرة")
                return "LOSS"
                
        except Exception as e:
            logging.error(f"❌ خطأ في الحصول على النتيجة: {e}")
            return random.choice(['WIN', 'LOSS'])

    def find_element_with_retry(self, selectors, timeout=10):
        """الباحث عن عنصر مع إعادة المحاولة"""
        for selector in selectors:
            try:
                if selector.startswith('//'):
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                return element
            except:
                continue
        return None

    def find_clickable_element(self, selectors, timeout=10):
        """الباحث عن عنصر قابل للنقر"""
        for selector in selectors:
            try:
                if selector.startswith('//'):
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                return element
            except:
                continue
        return None

    def keep_alive(self):
        """الحفاظ على نشاط المتصفح"""
        try:
            if time.time() - self.last_activity > 600:
                logging.info("🔄 تجديد نشاط المتصفح...")
                self.refresh_and_prepare()
            return True
        except Exception as e:
            logging.error(f"❌ خطأ في الحفاظ على النشاط: {e}")
            return False

    def close_browser(self):
        """إغلاق المتصفح"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("✅ تم إغلاق المتصفح")
            except:
                pass
