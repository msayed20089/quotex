import time
import logging
import random
from config import QX_EMAIL, QX_PASSWORD, QX_LOGIN_URL

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("⚠️ Playwright غير مثبت، سيتم استخدام وضع المحاكاة")

class QXBrokerManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_logged_in = False
        self.last_activity = time.time()
        
        if PLAYWRIGHT_AVAILABLE:
            self.setup_browser()
        else:
            logging.info("🎮 تشغيل وضع المحاكاة - Playwright غير متوفر")
    
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
            
            # فتح الصفحة الرئيسية
            self.page.goto("https://qxbroker.com/ar/demo-trade")
            time.sleep(5)
            
        except Exception as e:
            logging.error(f"❌ خطأ في إعداد المتصفح: {e}")
            self.browser = None

    def ensure_login(self):
        """التأكد من تسجيل الدخول"""
        if not self.browser:
            logging.info("🎮 وضع المحاكاة - تسجيل الدخول")
            self.is_logged_in = True
            return True
            
        try:
            if self.check_login_status():
                self.is_logged_in = True
                logging.info("✅ المستخدم مسجل الدخول")
                return True
            else:
                logging.info("🔐 جاري تسجيل الدخول...")
                return self.login()
                
        except Exception as e:
            logging.error(f"❌ خطأ في التأكد من تسجيل الدخول: {e}")
            return False

    def check_login_status(self):
        """التحقق من حالة تسجيل الدخول"""
        if not self.browser:
            return True
            
        try:
            current_url = self.page.url
            if "demo-trade" in current_url and "sign-in" not in current_url:
                return True
            
            # التحقق من وجود عناصر الواجهة
            balance_elements = self.page.query_selector_all("text=رصيد")
            if len(balance_elements) > 0:
                return True
                
            return False
        except:
            return False

    def login(self):
        """تسجيل الدخول"""
        if not self.browser:
            logging.info("🎮 وضع المحاكاة - تسجيل الدخول")
            self.is_logged_in = True
            return True
            
        try:
            logging.info("🔗 جاري تسجيل الدخول إلى Quotex...")
            self.page.goto("https://qxbroker.com/ar/sign-in")
            time.sleep(5)
            
            # البحث عن حقول الدخول بطرق متعددة
            selectors = [
                "input[type='email']",
                "input[name='email']", 
                "input[placeholder*='email']",
                "input[placeholder*='بريد']"
            ]
            
            email_field = None
            for selector in selectors:
                try:
                    email_field = self.page.query_selector(selector)
                    if email_field:
                        break
                except:
                    continue
            
            if email_field:
                email_field.fill(QX_EMAIL)
                time.sleep(1)
            else:
                logging.error("❌ لم يتم العثور على حقل البريد الإلكتروني")
                return False
            
            # البحث عن حقل كلمة المرور
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password']",
                "input[placeholder*='كلمة']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.page.query_selector(selector)
                    if password_field:
                        break
                except:
                    continue
            
            if password_field:
                password_field.fill(QX_PASSWORD)
                time.sleep(1)
            else:
                logging.error("❌ لم يتم العثور على حقل كلمة المرور")
                return False
            
            # البحث عن زر الدخول
            login_selectors = [
                "button[type='submit']",
                "button:has-text('تسجيل')",
                "button:has-text('دخول')",
                "button:has-text('Sign')",
                "button:has-text('Login')"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.page.query_selector(selector)
                    if login_button:
                        break
                except:
                    continue
            
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

    def execute_trade(self, pair, direction, duration=30):
        """تنفيذ صفقة"""
        if not self.browser:
            logging.info(f"🎮 وضع المحاكاة - صفقة {direction} على {pair}")
            time.sleep(2)
            return True
            
        try:
            if not self.is_logged_in and not self.ensure_login():
                return False
            
            self.page.goto("https://qxbroker.com/ar/demo-trade")
            time.sleep(5)
            
            logging.info(f"📊 جاري تنفيذ صفقة: {pair} - {direction}")
            
            # البحث عن الزوج واختياره
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
        if not self.browser:
            return True
            
        try:
            # البحث عن زر +
            plus_selectors = [
                "button:has-text('+')",
                "div:has-text('+')",
                "[class*='plus']",
                "[class*='add']"
            ]
            
            for selector in plus_selectors:
                try:
                    plus_button = self.page.query_selector(selector)
                    if plus_button:
                        plus_button.click()
                        logging.info("➕ تم فتح قائمة الأزواج")
                        time.sleep(3)
                        break
                except:
                    continue
            
            # البحث عن شريط البحث
            search_selectors = [
                "input[placeholder*='بحث']",
                "input[placeholder*='search']",
                "input[type='search']"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.page.query_selector(selector)
                    if search_box:
                        break
                except:
                    continue
            
            if search_box:
                search_pair = pair.replace('/', '').upper()
                search_box.fill(search_pair)
                logging.info(f"🔍 جاري البحث عن الزوج: {search_pair}")
                time.sleep(3)
            else:
                logging.error("❌ لم يتم العثور على شريط البحث")
                return False
            
            # اختيار الزوج من النتائج
            pair_selectors = [
                f"text={pair}",
                f"text={pair.replace('/', '').upper()}"
            ]
            
            pair_element = None
            for selector in pair_selectors:
                try:
                    pair_element = self.page.query_selector(selector)
                    if pair_element:
                        break
                except:
                    continue
            
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
        if not self.browser:
            return
            
        try:
            duration_selectors = [
                f"button:has-text('{duration}')",
                f"div:has-text('{duration}')"
            ]
            
            for selector in duration_selectors:
                try:
                    duration_button = self.page.query_selector(selector)
                    if duration_button:
                        duration_button.click()
                        logging.info(f"⏱ تم تحديد مدة {duration} ثانية")
                        time.sleep(2)
                        return
                except:
                    continue
            
            logging.warning(f"⚠️ لم يتم العثور على زر مدة {duration} ثانية")
        except Exception as e:
            logging.warning(f"⚠️ خطأ في تحديد المدة: {e}")

    def set_amount(self, amount):
        """تحديد مبلغ التداول"""
        if not self.browser:
            return
            
        try:
            amount_selectors = [
                "input[type='number']",
                "input[placeholder*='$']"
            ]
            
            for selector in amount_selectors:
                try:
                    amount_input = self.page.query_selector(selector)
                    if amount_input:
                        amount_input.fill(str(amount))
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
        if not self.browser:
            return True
            
        try:
            if direction.upper() == 'BUY':
                buy_selectors = [
                    "button:has-text('صاعد')",
                    "button:has-text('UP')",
                    "button:has-text('شراء')",
                    "[class*='up']",
                    "[class*='buy']"
                ]
                
                for selector in buy_selectors:
                    try:
                        buy_button = self.page.query_selector(selector)
                        if buy_button:
                            buy_button.click()
                            logging.info("🟢 تم النقر على زر صاعد/UP")
                            time.sleep(3)
                            return True
                    except:
                        continue
                
                logging.error("❌ لم يتم العثور على زر صاعد")
                return False
            else:
                sell_selectors = [
                    "button:has-text('هابط')",
                    "button:has-text('DOWN')",
                    "button:has-text('بيع')",
                    "[class*='down']",
                    "[class*='sell']"
                ]
                
                for selector in sell_selectors:
                    try:
                        sell_button = self.page.query_selector(selector)
                        if sell_button:
                            sell_button.click()
                            logging.info("🔴 تم النقر على زر هابط/DOWN")
                            time.sleep(3)
                            return True
                    except:
                        continue
                
                logging.error("❌ لم يتم العثور على زر هابط")
                return False
                    
        except Exception as e:
            logging.error(f"❌ خطأ في تنفيذ الاتجاه: {e}")
            return False

    def get_trade_result(self):
        """الحصول على نتيجة الصفقة"""
        if not self.browser:
            result = random.choice(['WIN', 'LOSS'])
            logging.info(f"🎮 وضع المحاكاة - نتيجة: {result}")
            return result
            
        try:
            logging.info("⏳ في انتظار نتيجة الصفقة...")
            time.sleep(35)
            
            # تحديث الصفحة
            self.page.reload()
            time.sleep(5)
            
            logging.info("🔍 جاري البحث عن نتيجة الصفقة...")
            
            # البحث في الصفحة عن النتائج
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
        if not self.browser:
            return True
            
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
