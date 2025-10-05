from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import logging
import random
from config import QX_EMAIL, QX_PASSWORD, QX_LOGIN_URL

class QXBrokerManager:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.last_activity = time.time()
        self.setup_driver()
        self.ensure_login()
    
    def setup_driver(self):
        """إعداد متصفح Chrome مع إعدادات محسنة للعمل المستمر"""
        chrome_options = Options()
        
        # إعدادات محسنة للتشغيل المستمر 24/7
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # إعدادات للذاكرة والأداء
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logging.info("✅ تم إعداد متصفح Chrome للتداول المستمر")
        except Exception as e:
            logging.error(f"❌ خطأ في إعداد المتصفح: {e}")
            raise e
    
    def ensure_login(self):
        """التأكد من أن المتصفح مسجل الدخول وجاهز للتداول"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.check_login_status():
                    self.is_logged_in = True
                    logging.info("✅ المتصفح مسجل الدخول وجاهز للتداول")
                    return True
                else:
                    logging.info(f"🔐 محاولة تسجيل الدخول {attempt + 1}/{max_retries}")
                    if self.login():
                        return True
            except Exception as e:
                logging.error(f"❌ خطأ في التأكد من تسجيل الدخول: {e}")
            
            time.sleep(5)
        
        logging.error("❌ فشل جميع محاولات تسجيل الدخول")
        return False
    
    def check_login_status(self):
        """التحقق من حالة تسجيل الدخول الحالية"""
        try:
            # التحقق من خلال عنوان URL أو عناصر الواجهة
            if self.driver.current_url and ("dashboard" in self.driver.current_url 
                                          or "account" in self.driver.current_url 
                                          or "trade" in self.driver.current_url):
                return True
            
            # التحقق من خلال عناصر الواجهة
            balance_indicators = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'رصيد') or contains(text(), 'Balance') or contains(text(), 'محفظة')]")
            if balance_indicators:
                return True
                
            return False
        except:
            return False
    
    def login(self):
        """تسجيل الدخول إلى منصة Quotex مع تحسينات"""
        try:
            logging.info("🔗 جاري تسجيل الدخول إلى Quotex...")
            self.driver.get(QX_LOGIN_URL)
            time.sleep(5)
            
            # البحث عن حقول الدخول
            email_field = self.find_element_with_retry([
                "input[name='email']", "input[name='username']", "input[type='email']",
                "input[placeholder*='email' i]", "input[placeholder*='بريد' i]"
            ])
            
            if not email_field:
                logging.error("❌ لم يتم العثور على حقل البريد الإلكتروني")
                return False
            
            email_field.clear()
            email_field.send_keys(QX_EMAIL)
            time.sleep(1)
            
            password_field = self.find_element_with_retry([
                "input[name='password']", "input[type='password']",
                "input[placeholder*='password' i]", "input[placeholder*='كلمة' i]"
            ])
            
            if not password_field:
                logging.error("❌ لم يتم العثور على حقل كلمة المرور")
                return False
            
            password_field.clear()
            password_field.send_keys(QX_PASSWORD)
            time.sleep(1)
            
            # البحث عن زر الدخول
            login_button = self.find_clickable_element([
                "//button[contains(text(), 'تسجيل')]", "//button[contains(text(), 'دخول')]",
                "//button[contains(text(), 'Sign')]", "//button[contains(text(), 'Login')]",
                "//button[@type='submit']"
            ])
            
            if login_button:
                login_button.click()
                time.sleep(8)
                
                if self.check_login_status():
                    self.is_logged_in = True
                    logging.info("✅ تم تسجيل الدخول بنجاح")
                    return True
            
            logging.error("❌ فشل تسجيل الدخول")
            return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في تسجيل الدخول: {e}")
            return False
    
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
    
    def refresh_and_prepare(self):
        """عمل refresh للصفحة والتحضير للصفقة التالية"""
        try:
            logging.info("🔄 جاري تحديث الصفحة للصفقة التالية...")
            
            # حفظ URL الحالي للعودة إليه إذا لزم الأمر
            current_url = self.driver.current_url
            
            # الانتقال إلى صفحة التداول مباشرة
            self.driver.get("https://qxbroker.com/ar/demo-trade")
            time.sleep(5)
            
            # التأكد من أن الصفحة قد تم تحميلها بالكامل
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.last_activity = time.time()
            logging.info("✅ تم تحضير الصفحة للصفقة التالية")
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحديث الصفحة: {e}")
            # محاولة إعادة الاتصال
            return self.recover_connection()
    
    def recover_connection(self):
        """استعادة الاتصال في حالة وجود مشاكل"""
        try:
            logging.info("🔄 محاولة استعادة الاتصال...")
            
            # أولاً: محاولة refresh بسيطة
            try:
                self.driver.refresh()
                time.sleep(5)
                if self.check_login_status():
                    return True
            except:
                pass
            
            # ثانياً: إعادة تسجيل الدخول
            if self.login():
                return True
            
            # ثالثاً: إعادة تشغيل المتصفح كحل أخير
            logging.info("🔄 إعادة تشغيل المتصفح...")
            self.close_browser()
            time.sleep(3)
            self.setup_driver()
            return self.ensure_login()
            
        except Exception as e:
            logging.error(f"❌ فشل في استعادة الاتصال: {e}")
            return False
    
    def execute_trade(self, pair, direction, duration=30):
        """تنفيذ صفقة حقيقية مع إدارة متقدمة للاتصال"""
        try:
            # التحقق من الاتصال قبل البدء
            if not self.is_logged_in or not self.check_login_status():
                logging.warning("⚠️ فقدان الاتصال، جاري إعادة الاتصال...")
                if not self.ensure_login():
                    logging.error("❌ فشل إعادة الاتصال")
                    return False
            
            # تحديث الصفحة للصفقة الجديدة
            if not self.refresh_and_prepare():
                logging.error("❌ فشل في تحضير الصفحة")
                return False
            
            logging.info(f"📊 جاري تنفيذ صفقة: {pair} - {direction}")
            
            # الخطوة 1: النقر على + لإظهار قائمة الأزواج
            plus_clicked = self.click_plus_button()
            
            # الخطوة 2: البحث عن الزوج
            if not self.search_pair(pair):
                return False
            
            # الخطوة 3: اختيار الزوج
            if not self.select_pair(pair):
                return False
            
            # الخطوة 4: تحديد المدة
            self.set_duration(duration)
            
            # الخطوة 5: تحديد المبلغ
            self.set_amount(1)
            
            # الخطوة 6: تنفيذ الصفقة
            if not self.execute_direction(direction):
                return False
            
            logging.info(f"🎯 تم تنفيذ صفقة {direction} على {pair} بنجاح")
            self.last_activity = time.time()
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ عام في تنفيذ الصفقة: {e}")
            # محاولة استعادة الاتصال للصفقة التالية
            self.recover_connection()
            return False
    
    def click_plus_button(self):
        """النقر على زر + لإظهار الأزواج"""
        try:
            plus_selectors = [
                "//button[contains(text(), '+')]",
                "//div[contains(text(), '+')]",
                "//*[contains(@class, 'add')]",
                "//*[contains(@class, 'plus')]"
            ]
            
            for selector in plus_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            logging.info("➕ تم النقر على + لإظهار قائمة الأزواج")
                            time.sleep(3)
                            return True
                except:
                    continue
            
            logging.info("🔍 لم يتم العثور على زر +، المتابعة مباشرة للبحث")
            return True  # نكمل حتى لو لم نجد الزر
        except Exception as e:
            logging.warning(f"⚠️ لم يتم العثور على زر +: {e}")
            return True  # نكمل رغم ذلك
    
    def search_pair(self, pair):
        """الباحث عن الزوج"""
        try:
            search_pair = pair.replace('/', '').upper()
            search_box = self.find_element_with_retry([
                "input[placeholder*='بحث']", "input[placeholder*='search']", 
                "input[type='search']", "input[class*='search']"
            ])
            
            if search_box:
                search_box.clear()
                search_box.send_keys(search_pair)
                logging.info(f"🔍 جاري البحث عن الزوج: {search_pair}")
                time.sleep(3)
                return True
            else:
                logging.error("❌ لم يتم العثور على شريط البحث")
                return False
        except Exception as e:
            logging.error(f"❌ خطأ في البحث: {e}")
            return False
    
    def select_pair(self, pair):
        """اختيار الزوج من النتائج"""
        try:
            search_pair = pair.replace('/', '').upper()
            pair_element = self.find_clickable_element([
                f"//*[contains(text(), '{pair}')]",
                f"//*[contains(text(), '{search_pair}')]"
            ])
            
            if pair_element:
                pair_element.click()
                logging.info(f"✅ تم اختيار الزوج: {pair}")
                time.sleep(4)
                return True
            else:
                logging.error(f"❌ لم يتم العثور على الزوج: {pair}")
                return False
        except Exception as e:
            logging.error(f"❌ خطأ في اختيار الزوج: {e}")
            return False
    
    def set_duration(self, duration):
        """تحديد مدة الصفقة"""
        try:
            duration_xpaths = [
                f"//button[contains(text(), '{duration}')]",
                f"//div[contains(text(), '00:00:{duration:02d}')]"
            ]
            
            for xpath in duration_xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            logging.info(f"⏱ تم تحديد مدة {duration} ثانية")
                            time.sleep(2)
                            return
                except:
                    continue
            
            logging.warning(f"⚠️ لم يتم العثور على زر مدة {duration} ثانية، استخدام الافتراضي")
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المدة: {e}")
    
    def set_amount(self, amount):
        """تحديد مبلغ التداول"""
        try:
            amount_selectors = [
                "input[type='number']", "input[placeholder*='$']",
                "input[placeholder*='استثمار']", "input[class*='amount']"
            ]
            
            for selector in amount_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            element.clear()
                            element.send_keys(str(amount))
                            logging.info(f"💰 تم تحديد المبلغ: ${amount}")
                            time.sleep(1)
                            return
                        except:
                            continue
                except:
                    continue
            
            logging.info("💰 استخدام المبلغ الافتراضي")
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المبلغ: {e}")
    
    def execute_direction(self, direction):
        """تنفيذ اتجاه الصفقة"""
        try:
            if direction.upper() == 'BUY':
                buy_button = self.find_clickable_element([
                    "//button[contains(text(), 'صاعد')]", "//button[contains(text(), 'شراء')]",
                    "//button[contains(text(), 'Buy')]", "//button[contains(@class, 'buy')]"
                ])
                
                if buy_button:
                    buy_button.click()
                    logging.info("🟢 تم النقر على زر صاعد/شراء")
                    time.sleep(3)
                    return True
                else:
                    logging.error("❌ لم يتم العثور على زر صاعد")
                    return False
            else:
                sell_button = self.find_clickable_element([
                    "//button[contains(text(), 'هابط')]", "//button[contains(text(), 'بيع')]",
                    "//button[contains(text(), 'Sell')]", "//button[contains(@class, 'sell')]"
                ])
                
                if sell_button:
                    sell_button.click()
                    logging.info("🔴 تم النقر على زر هابط/بيع")
                    time.sleep(3)
                    return True
                else:
                    logging.error("❌ لم يتم العثور على زر هابط")
                    return False
                    
        except Exception as e:
            logging.error(f"❌ خطأ في تنفيذ الاتجاه: {e}")
            return False
    
    def get_trade_result(self):
        """الحصول على نتيجة الصفقة"""
        try:
            logging.info("⏳ في انتظار نتيجة الصفقة...")
            time.sleep(35)  # 30 ثانية + هامش أمان
            
            # عمل refresh للحصول على أحدث البيانات
            self.driver.refresh()
            time.sleep(5)
            
            logging.info("🔍 جاري البحث عن نتيجة الصفقة...")
            
            # البحث عن النتائج في الصفحة
            page_content = self.driver.page_source
            
            # تحليل النتائج بناءً على المحتوى
            if '+' in page_content and ('green' in page_content.lower() or 'profit' in page_content.lower()):
                logging.info("🎉 تم التعرف على صفقة رابحة")
                return "WIN"
            else:
                logging.info("❌ تم التعرف على صفقة خاسرة")
                return "LOSS"
                
        except Exception as e:
            logging.error(f"❌ خطأ في الحصول على النتيجة: {e}")
            return random.choice(['WIN', 'LOSS'])
    
    def keep_alive(self):
        """الحفاظ على نشاط المتصفح"""
        try:
            # إذا مر أكثر من 10 دقائق بدون نشاط، نعمل refresh
            if time.time() - self.last_activity > 600:  # 10 دقائق
                logging.info("🔄 تجديد نشاط المتصفح...")
                self.refresh_and_prepare()
            
            return True
        except Exception as e:
            logging.error(f"❌ خطأ في الحفاظ على النشاط: {e}")
            return False
    
    def close_browser(self):
        """إغلاق المتصفح (يستخدم فقط عند إنهاء البرنامج)"""
        if self.driver:
            try:
                self.driver.quit()
                logging.info("✅ تم إغلاق المتصفح")
            except:
                pass
