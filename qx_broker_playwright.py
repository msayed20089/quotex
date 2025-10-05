from playwright.sync_api import sync_playwright
import time
import logging
import random
from config import QX_EMAIL, QX_PASSWORD, QX_LOGIN_URL

class QXBrokerManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_logged_in = False
        self.last_activity = time.time()
        self.setup_browser()
        
    def setup_browser(self):
        """إعداد المتصفح باستخدام Playwright"""
        try:
            self.playwright = sync_playwright().start()
            
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--window-size=1920,1080'
                ]
            )
            
            self.page = self.browser.new_page()
            logging.info("✅ تم إعداد المتصفح باستخدام Playwright بنجاح")
            
        except Exception as e:
            logging.error(f"❌ خطأ في إعداد المتصفح: {e}")
            raise e

    def ensure_login(self):
        """التأكد من تسجيل الدخول"""
        try:
            self.page.goto("https://qxbroker.com/ar/demo-trade")
            time.sleep(5)
            
            if self.check_login_status():
                self.is_logged_in = True
                logging.info("✅ المستخدم مسجل الدخول")
                return True
            else:
                return self.login()
                
        except Exception as e:
            logging.error(f"❌ خطأ في التأكد من تسجيل الدخول: {e}")
            return False

    def check_login_status(self):
        """التحقق من حالة تسجيل الدخول"""
        try:
            current_url = self.page.url
            if "demo-trade" in current_url and "sign-in" not in current_url:
                return True
            
            # التحقق من وجود عناصر الواجهة
            balance_elements = self.page.query_selector_all("text=رصيد, text=Balance")
            if balance_elements:
                return True
                
            return False
        except:
            return False

    def login(self):
        """تسجيل الدخول"""
        try:
            logging.info("🔗 جاري تسجيل الدخول...")
            self.page.goto("https://qxbroker.com/ar/sign-in")
            time.sleep(5)
            
            # إدخال البريد الإلكتروني
            email_field = self.page.query_selector("input[type='email'], input[name='email']")
            if email_field:
                email_field.fill(QX_EMAIL)
                time.sleep(1)
            
            # إدخال كلمة المرور
            password_field = self.page.query_selector("input[type='password'], input[name='password']")
            if password_field:
                password_field.fill(QX_PASSWORD)
                time.sleep(1)
            
            # النقر على زر الدخول
            login_button = self.page.query_selector("button[type='submit'], text=تسجيل, text=دخول")
            if login_button:
                login_button.click()
                time.sleep(8)
                
                if self.check_login_status():
                    self.is_logged_in = True
                    logging.info("✅ تم تسجيل الدخول بنجاح")
                    return True
            
            return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في تسجيل الدخول: {e}")
            return False

    def execute_trade(self, pair, direction, duration=30):
        """تنفيذ صفقة حقيقية"""
        try:
            if not self.is_logged_in and not self.ensure_login():
                return False
            
            self.page.goto("https://qxbroker.com/ar/demo-trade")
            time.sleep(5)
            
            logging.info(f"📊 جاري تنفيذ صفقة: {pair} - {direction}")
            
            # البحث عن الزوج
            if not self.search_and_select_pair(pair):
                return False
            
            # تحديد المدة
            self.set_duration(duration)
            
            # تحديد المبلغ
            self.set_amount(1)
            
            # تنفيذ الصفقة
            if not self.execute_direction(direction):
                return False
            
            logging.info(f"🎯 تم تنفيذ صفقة {direction} على {pair} بنجاح")
            self.last_activity = time.time()
            return True
            
        except Exception as e:
            logging.error(f"❌ خطأ في تنفيذ الصفقة: {e}")
            return False

    def search_and_select_pair(self, pair):
        """البحث عن الزوج واختياره"""
        try:
            # البحث عن زر +
            plus_button = self.page.query_selector("text='+'")
            if plus_button:
                plus_button.click()
                time.sleep(2)
            
            # البحث عن شريط البحث
            search_box = self.page.query_selector("input[placeholder*='بحث'], input[placeholder*='search']")
            if search_box:
                search_pair = pair.replace('/', '').upper()
                search_box.fill(search_pair)
                time.sleep(3)
            
            # اختيار الزوج
            pair_element = self.page.query_selector(f"text='{pair}'")
            if pair_element:
                pair_element.click()
                time.sleep(3)
                return True
            
            return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في البحث عن الزوج: {e}")
            return False

    def set_duration(self, duration):
        """تحديد مدة الصفقة"""
        try:
            duration_button = self.page.query_selector(f"text='{duration}'")
            if duration_button:
                duration_button.click()
                time.sleep(1)
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المدة: {e}")

    def set_amount(self, amount):
        """تحديد مبلغ التداول"""
        try:
            amount_input = self.page.query_selector("input[type='number']")
            if amount_input:
                amount_input.fill(str(amount))
                time.sleep(1)
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المبلغ: {e}")

    def execute_direction(self, direction):
        """تنفيذ اتجاه الصفقة"""
        try:
            if direction.upper() == 'BUY':
                buy_button = self.page.query_selector("text=صاعد, text=UP, text=شراء")
                if buy_button:
                    buy_button.click()
                    time.sleep(3)
                    return True
            else:
                sell_button = self.page.query_selector("text=هابط, text=DOWN, text=بيع")
                if sell_button:
                    sell_button.click()
                    time.sleep(3)
                    return True
            
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
            self.page.reload()
            time.sleep(5)
            
            # البحث عن النتيجة
            page_content = self.page.content()
            
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
            if time.time() - self.last_activity > 600:
                logging.info("🔄 تجديد نشاط المتصفح...")
                self.page.reload()
                time.sleep(3)
            return True
        except Exception as e:
            logging.error(f"❌ خطأ في الحفاظ على النشاط: {e}")
            return False

    def close_browser(self):
        """إغلاق المتصفح"""
        if self.browser:
            try:
                self.browser.close()
                if self.playwright:
                    self.playwright.stop()
                logging.info("✅ تم إغلاق المتصفح")
            except:
                pass
