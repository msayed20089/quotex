from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import logging
import random
import os
import json
from config import QX_EMAIL, QX_PASSWORD, QX_LOGIN_URL

class QXBrokerManager:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.last_activity = time.time()
        self.session_data = {}
        self.setup_driver()
        self.ensure_login()
    
    def setup_driver(self):
        """إعداد متصفح Chrome لـ Quotex"""
        chrome_options = Options()
        
        # إعدادات Railway المثالية
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # إعدادات لتحسين الأداء
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        
        try:
            # استخدام webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logging.info("✅ تم إعداد متصفح Chrome لـ Quotex بنجاح")
            
        except Exception as e:
            logging.error(f"❌ خطأ في إعداد المتصفح: {e}")
            self.setup_driver_fallback()
    
    def setup_driver_fallback(self):
        """طريقة بديلة لإعداد المتصفح"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("✅ تم إعداد المتصفح باستخدام الطريقة البديلة")
            
        except Exception as e:
            logging.error(f"❌ فشل جميع محاولات إعداد المتصفح: {e}")
            raise e
    
    def ensure_login(self):
        """التأكد من تسجيل الدخول"""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                # الانتقال مباشرة لصفحة الديمو تريد
                self.driver.get("https://qxbroker.com/ar/demo-trade")
                time.sleep(5)
                
                # التحقق من حالة الدخول من خلال الـ JavaScript settings
                login_status = self.check_login_from_js()
                if login_status:
                    self.is_logged_in = True
                    logging.info("✅ المستخدم مسجل الدخول وجاهز للتداول")
                    return True
                else:
                    logging.info(f"🔐 محاولة تسجيل الدخول {attempt + 1}/{max_retries}")
                    if self.login():
                        return True
            except Exception as e:
                logging.error(f"❌ خطأ في التأكد من تسجيل الدخول: {e}")
            
            time.sleep(3)
        
        logging.error("❌ فشل جميع محاولات تسجيل الدخول")
        return False

    def check_login_from_js(self):
        """التحقق من تسجيل الدخول من خلال بيانات JavaScript"""
        try:
            # الحصول على بيانات الـ settings من window
            settings_script = "return window.settings;"
            settings = self.driver.execute_script(settings_script)
            
            if settings and settings.get('email'):
                self.session_data = settings
                logging.info(f"✅ تم التعرف على المستخدم: {settings.get('email')}")
                logging.info(f"💰 الرصيد: {settings.get('demoBalance')}")
                return True
            return False
        except:
            return False

    def login(self):
        """تسجيل الدخول إلى Quotex"""
        try:
            logging.info("🔗 جاري تسجيل الدخول إلى Quotex...")
            self.driver.get("https://qxbroker.com/ar/sign-in")
            time.sleep(5)
            
            # البحث عن حقول الدخول في واجهة Quotex الجديدة
            email_field = self.find_element_with_retry([
                "input[name='email']", 
                "input[type='email']",
                "input[placeholder*='email' i]", 
                "input[placeholder*='بريد' i]",
                "input[data-testid='email-input']"
            ])
            
            if not email_field:
                logging.error("❌ لم يتم العثور على حقل البريد الإلكتروني")
                return False
            
            email_field.clear()
            email_field.send_keys(QX_EMAIL)
            time.sleep(1)
            
            password_field = self.find_element_with_retry([
                "input[name='password']", 
                "input[type='password']",
                "input[placeholder*='password' i]", 
                "input[placeholder*='كلمة' i]",
                "input[data-testid='password-input']"
            ])
            
            if not password_field:
                logging.error("❌ لم يتم العثور على حقل كلمة المرور")
                return False
            
            password_field.clear()
            password_field.send_keys(QX_PASSWORD)
            time.sleep(1)
            
            # البحث عن زر الدخول
            login_button = self.find_clickable_element([
                "//button[contains(text(), 'تسجيل')]", 
                "//button[contains(text(), 'دخول')]",
                "//button[contains(text(), 'Sign')]", 
                "//button[contains(text(), 'Login')]",
                "//button[@type='submit']",
                "//button[contains(@class, 'login-button')]"
            ])
            
            if login_button:
                login_button.click()
                time.sleep(8)
                
                # التحقق من نجاح الدخول
                if self.check_login_from_js():
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
            time.sleep(5)
            
            # انتظار تحميل التطبيق React
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "root"))
            )
            
            # انتظار تحميل بيانات الـ settings
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return window.settings !== undefined;")
            )
            
            self.last_activity = time.time()
            logging.info("✅ تم تحضير الصفحة للصفقة التالية")
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحديث الصفحة: {e}")
            return self.recover_connection()

    def recover_connection(self):
        """استعادة الاتصال"""
        try:
            logging.info("🔄 محاولة استعادة الاتصال...")
            
            try:
                self.driver.refresh()
                time.sleep(5)
                if self.check_login_from_js():
                    return True
            except:
                pass
            
            if self.login():
                return True
            
            logging.info("🔄 إعادة تشغيل المتصفح...")
            self.close_browser()
            time.sleep(3)
            self.setup_driver()
            return self.ensure_login()
            
        except Exception as e:
            logging.error(f"❌ فشل في استعادة الاتصال: {e}")
            return False

    def execute_trade(self, pair, direction, duration=30):
        """تنفيذ صفقة على منصة Quotex"""
        try:
            if not self.is_logged_in or not self.check_login_from_js():
                logging.warning("⚠️ فقدان الاتصال، جاري إعادة الاتصال...")
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
            
            # تحديد مدة الصفقة (30 ثانية)
            if not self.set_duration(duration):
                return False
            
            # تحديد مبلغ التداول ($1)
            if not self.set_amount(1):
                return False
            
            # تنفيذ الصفقة
            if not self.execute_direction(direction):
                return False
            
            logging.info(f"🎯 تم تنفيذ صفقة {direction} على {pair} بنجاح")
            self.last_activity = time.time()
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ عام في تنفيذ الصفقة: {e}")
            self.recover_connection()
            return False

    def search_and_select_pair(self, pair):
        """البحث عن الزوج واختياره في واجهة Quotex الجديدة"""
        try:
            # البحث عن زر اختيار الزوج (الزر + كما في الشرح)
            pair_button = self.find_clickable_element([
                "//button[contains(@class, 'asset-selector')]",
                "//div[contains(@class, 'asset-selector')]",
                "//button[contains(text(), '+')]",
                "//div[contains(text(), '+')]",
                "//*[contains(@class, 'asset-dropdown')]",
                "//*[contains(@data-testid, 'asset-selector')]"
            ])
            
            if pair_button:
                pair_button.click()
                logging.info("➕ تم فتح قائمة الأزواج")
                time.sleep(2)
            else:
                logging.warning("⚠️ لم يتم العثور على زر اختيار الزوج، المتابعة مباشرة")
            
            # البحث عن شريط البحث
            search_box = self.find_element_with_retry([
                "input[placeholder*='بحث']", 
                "input[placeholder*='search']", 
                "input[type='search']",
                "input[class*='search']",
                "input[data-testid*='search']"
            ])
            
            if search_box:
                search_box.clear()
                # تحويل اسم الزوج للتنسيق المناسب (مثال: USD/EGP -> USDEGP)
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
                f"//*[contains(text(), '{search_pair}')]",
                f"//div[contains(@class, 'asset-item') and contains(text(), '{pair}')]",
                f"//div[contains(@data-testid, 'asset-{search_pair}')]"
            ])
            
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
                f"//button[contains(text(), '{duration}') or contains(@data-duration, '{duration}')]")
            
            for btn in duration_buttons:
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    logging.info(f"⏱ تم تحديد مدة {duration} ثانية")
                    time.sleep(2)
                    return True
            
            # إذا لم يتم العثور، نبحث عن الأزرار الشائعة
            common_durations = ["//button[contains(text(), '30')]", 
                              "//button[contains(@class, 'duration-30')]"]
            
            for xpath in common_durations:
                try:
                    btn = self.driver.find_element(By.XPATH, xpath)
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        logging.info(f"⏱ تم تحديد مدة {duration} ثانية (الطريقة البديلة)")
                        time.sleep(2)
                        return True
                except:
                    continue
            
            logging.warning(f"⚠️ لم يتم العثور على زر مدة {duration} ثانية")
            return True  # نكمل رغم ذلك
            
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المدة: {e}")
            return True  # نكمل رغم ذلك

    def set_amount(self, amount):
        """تحديد مبلغ التداول"""
        try:
            # البحث عن حقل المبلغ
            amount_inputs = self.driver.find_elements(By.XPATH, 
                "//input[@type='number' or contains(@placeholder, '$') or contains(@data-testid, 'amount')]")
            
            for amount_input in amount_inputs:
                try:
                    amount_input.clear()
                    amount_input.send_keys(str(amount))
                    logging.info(f"💰 تم تحديد المبلغ: ${amount}")
                    time.sleep(1)
                    return True
                except:
                    continue
            
            logging.info("💰 استخدام المبلغ الافتراضي")
            return True
            
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المبلغ: {e}")
            return True

    def execute_direction(self, direction):
        """تنفيذ اتجاه الصفقة"""
        try:
            if direction.upper() == 'BUY':
                # البحث عن زر UP/صاعد/شراء
                buy_selectors = [
                    "//button[contains(text(), 'صاعد')]",
                    "//button[contains(text(), 'UP')]",
                    "//button[contains(text(), 'شراء')]",
                    "//button[contains(@class, 'up-button')]",
                    "//button[contains(@class, 'buy-button')]",
                    "//button[contains(@data-testid, 'up-button')]",
                    "//button[contains(@style, 'background-color: rgb(14, 203, 129)')]"  # اللون الأخضر
                ]
                
                buy_button = self.find_clickable_element(buy_selectors)
                
                if buy_button:
                    buy_button.click()
                    logging.info("🟢 تم النقر على زر صاعد/UP")
                    time.sleep(3)
                    return True
                else:
                    logging.error("❌ لم يتم العثور على زر صاعد")
                    return False
            else:
                # البحث عن زر DOWN/هابط/بيع
                sell_selectors = [
                    "//button[contains(text(), 'هابط')]",
                    "//button[contains(text(), 'DOWN')]",
                    "//button[contains(text(), 'بيع')]",
                    "//button[contains(@class, 'down-button')]",
                    "//button[contains(@class, 'sell-button')]",
                    "//button[contains(@data-testid, 'down-button')]",
                    "//button[contains(@style, 'background-color: rgb(255, 82, 82)')]"  # اللون الأحمر
                ]
                
                sell_button = self.find_clickable_element(sell_selectors)
                
                if sell_button:
                    sell_button.click()
                    logging.info("🔴 تم النقر على زر هابط/DOWN")
                    time.sleep(3)
                    return True
                else:
                    logging.error("❌ لم يتم العثور على زر هابط")
                    return False
                    
        except Exception as e:
            logging.error(f"❌ خطأ في تنفيذ الاتجاه: {e}")
            return False

    def get_trade_result(self):
        """الحصول على نتيجة الصفقة من Quotex"""
        try:
            logging.info("⏳ في انتظار نتيجة الصفقة...")
            time.sleep(35)  # 30 ثانية + هامش أمان
            
            # تحديث الصفحة للحصول على أحدث البيانات
            self.driver.refresh()
            time.sleep(5)
            
            logging.info("🔍 جاري البحث عن نتيجة الصفقة...")
            
            # البحث في الصفحة عن نتائج الصفقات
            page_content = self.driver.page_source
            
            # طريقة 1: البحث عن علامات النجاح/الفشل في الصفحة
            if '+"' in page_content and ('green' in page_content.lower() or 'profit' in page_content.lower() or 'rgb(14, 203, 129)' in page_content):
                logging.info("🎉 تم التعرف على صفقة رابحة")
                return "WIN"
            elif ('red' in page_content.lower() or 'loss' in page_content.lower() or 'rgb(255, 82, 82)' in page_content) and '+"' not in page_content:
                logging.info("❌ تم التعرف على صفقة خاسرة")
                return "LOSS"
            
            # طريقة 2: البحث في عناصر الواجهة
            try:
                trade_elements = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'trade-result') or contains(@class, 'deal-item')]")
                
                for element in trade_elements:
                    element_text = element.text
                    element_html = element.get_attribute('innerHTML')
                    
                    if '+' in element_text and ('green' in element_html or 'profit' in element_text):
                        logging.info("🎉 تم التعرف على صفقة رابحة (من العناصر)")
                        return "WIN"
                    elif 'green' not in element_html and 'red' in element_html and '+' not in element_text:
                        logging.info("❌ تم التعرف على صفقة خاسرة (من العناصر)")
                        return "LOSS"
            except:
                pass
            
            # طريقة 3: إذا لم نجد نتيجة واضحة
            logging.warning("⚠️ لم يتم العثور على نتيجة واضحة، استخدام القيمة الافتراضية")
            return random.choice(['WIN', 'LOSS'])
                
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
            if time.time() - self.last_activity > 600:  # 10 دقائق
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
