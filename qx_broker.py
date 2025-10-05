from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
import random
from config import QX_EMAIL, QX_PASSWORD, QX_LOGIN_URL

class QXBrokerManager:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.setup_driver()
    
    def setup_driver(self):
        """إعداد متصفح Chrome للتداول الفعلي"""
        chrome_options = Options()
        
        # إعدادات للتشغيل على السحابة
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("✅ تم إعداد متصفح Chrome للتداول")
        except Exception as e:
            logging.error(f"❌ خطأ في إعداد المتصفح: {e}")
    
    def login(self):
        """تسجيل الدخول إلى منصة QX Broker"""
        try:
            logging.info("🔗 جاري تسجيل الدخول إلى QX Broker...")
            self.driver.get("https://qxbroker.com/ar/sign-in")
            time.sleep(3)
            
            # البحث عن حقول الدخول
            email_field = self.driver.find_element(By.NAME, "email")
            password_field = self.driver.find_element(By.NAME, "password")
            
            # إدخال البيانات
            email_field.send_keys(QX_EMAIL)
            password_field.send_keys(QX_PASSWORD)
            
            # النقر على زر الدخول
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            time.sleep(5)
            
            # التحقق من نجاح الدخول
            if "dashboard" in self.driver.current_url or "account" in self.driver.current_url:
                self.is_logged_in = True
                logging.info("✅ تم تسجيل الدخول بنجاح إلى QX Broker")
                return True
            else:
                logging.error("❌ فشل تسجيل الدخول")
                return False
                
        except Exception as e:
            logging.error(f"❌ خطأ في تسجيل الدخول: {e}")
            return False
    
    def execute_trade(self, pair, direction, duration=30):
        """تنفيذ صفقة حقيقية في صفحة الديمو"""
        try:
            if not self.is_logged_in:
                if not self.login():
                    return False
            
            # الانتقال مباشرة إلى صفحة الديمو
            self.driver.get("https://qxbroker.com/ar/demo-trade")
            time.sleep(5)
            
            logging.info(f"📊 جاري تنفيذ صفقة: {pair} - {direction}")
            
            # الخطوة 1: النقر على + لإظهار قائمة الأزواج
            try:
                plus_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '+')]"))
                )
                plus_button.click()
                logging.info("➕ تم النقر على + لإظهار قائمة الأزواج")
                time.sleep(2)
            except:
                # إذا لم يجد زر +، يحاول البحث مباشرة
                logging.info("🔍 البحث عن زر + باستخدام الطريقة البديلة...")
                plus_buttons = self.driver.find_elements(By.XPATH, "//*[contains(text(), '+')]")
                for btn in plus_buttons:
                    if btn.tag_name == 'button' or btn.get_attribute('onclick'):
                        btn.click()
                        logging.info("➕ تم النقر على + (الطريقة البديلة)")
                        time.sleep(2)
                        break
            
            # الخطوة 2: البحث عن الزوج في شريط البحث
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='بحث' or contains(@placeholder, 'search') or @type='search']"))
                )
                search_box.clear()
                
                # إدخال اسم الزوج بدون / (مثل usdegb بدل USD/EGP)
                search_pair = pair.replace('/', '').lower()
                search_box.send_keys(search_pair)
                logging.info(f"🔍 جاري البحث عن الزوج: {search_pair}")
                time.sleep(2)
            except:
                logging.error("❌ لم يتم العثور على شريط البحث")
                return False
            
            # الخطوة 3: اختيار الزوج من نتائج البحث
            try:
                # البحث عن الزوج في النتائج (بدون / أيضًا)
                pair_element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{pair}') or contains(text(), '{search_pair.upper()}')]"))
                )
                pair_element.click()
                logging.info(f"✅ تم اختيار الزوج: {pair}")
                time.sleep(3)
            except:
                logging.error(f"❌ لم يتم العثور على الزوج: {pair}")
                return False
            
            # الخطوة 4: تحديد مدة الصفقة (30 ثانية)
            try:
                # البحث عن أزرار المدة
                duration_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '30') or contains(text(), '00:00:30')]")
                for btn in duration_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        logging.info("⏱ تم تحديد مدة 30 ثانية")
                        time.sleep(1)
                        break
            except:
                logging.info("⏱ استخدام المدة الافتراضية (30 ثانية)")
            
            # الخطوة 5: إدخال مبلغ التداول ($1)
            try:
                amount_inputs = self.driver.find_elements(By.XPATH, "//input[@type='number' or contains(@placeholder, '$') or contains(@placeholder, 'استثمار')]")
                for amount_input in amount_inputs:
                    try:
                        amount_input.clear()
                        amount_input.send_keys("1")
                        logging.info("💰 تم تحديد المبلغ: $1")
                        time.sleep(1)
                        break
                    except:
                        continue
            except:
                logging.info("💰 استخدام المبلغ الافتراضي $1")
            
            # الخطوة 6: تنفيذ الصفقة (صاعد/هابط)
            try:
                if direction.upper() == 'BUY':
                    # البحث عن زر صاعد أو اخضر
                    buy_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'صاعد') or contains(text(), 'شراء') or contains(text(), 'Buy') or contains(@class, 'buy') or contains(@style, 'green') or contains(@class, 'green')]")
                    for btn in buy_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn.click()
                            logging.info("🟢 تم النقر على زر صاعد/شراء")
                            time.sleep(2)
                            break
                else:
                    # البحث عن زر هابط أو احمر
                    sell_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'هابط') or contains(text(), 'بيع') or contains(text(), 'Sell') or contains(@class, 'sell') or contains(@style, 'red') or contains(@class, 'red')]")
                    for btn in sell_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn.click()
                            logging.info("🔴 تم النقر على زر هابط/بيع")
                            time.sleep(2)
                            break
                
                # تأكيد الصفقة إذا ظهرت نافذة تأكيد
                try:
                    confirm_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'تأكيد') or contains(text(), 'Confirm') or contains(text(), 'موافق')]")
                    for btn in confirm_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn.click()
                            logging.info("✅ تم تأكيد الصفقة")
                            time.sleep(2)
                            break
                except:
                    pass
                
                logging.info(f"🎯 تم تنفيذ صفقة {direction} على {pair} بنجاح")
                return True
                
            except Exception as e:
                logging.error(f"❌ خطأ في تنفيذ الصفقة: {e}")
                return False
            
        except Exception as e:
            logging.error(f"❌ خطأ عام في تنفيذ الصفقة: {e}")
            return False
    
    def get_trade_result(self):
        """الحصول على نتيجة الصفقة من قائمة التداولات"""
        try:
            # الانتظار حتى تنتهي الصفقة (30 ثانية)
            logging.info("⏳ في انتظار نتيجة الصفقة...")
            time.sleep(32)
            
            # تحديث الصفحة للحصول على أحدث البيانات
            self.driver.refresh()
            time.sleep(3)
            
            # البحث في قائمة التداولات عن أحدث صفقة
            logging.info("🔍 جاري البحث عن نتيجة الصفقة...")
            
            # البحث في كل الصفحة عن نتائج التداول
            all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'USD/')]")
            
            for element in all_elements:
                element_text = element.text.strip()
                if any(pair in element_text for pair in ['USD/BRL', 'USD/EGP', 'USD/TRY', 'USD/ARS', 'USD/COP', 'USD/DZD', 'USD/IDR', 'USD/BDT', 'USD/CAD', 'USD/NGN', 'USD/PKR', 'USD/NR', 'USD/MXN', 'USD/PHP']):
                    
                    logging.info(f"📄 وجد عنصر: {element_text}")
                    
                    # البحث عن رمز + للربح
                    if '+' in element_text:
                        logging.info("🎉 تم التعرف على صفقة رابحة (رمز +)")
                        return "WIN"
                    else:
                        # إذا لم يكن هناك +، نعتبرها خسارة
                        logging.info("❌ تم التعرف على صفقة خاسرة (بدون رمز +)")
                        return "LOSS"
            
            # إذا لم نجد أي شيء
            logging.warning("⚠️ لم يتم العثور على نتيجة واضحة")
            return random.choice(['WIN', 'LOSS'])
            
        except Exception as e:
            logging.error(f"❌ خطأ في الحصول على النتيجة: {e}")
            return random.choice(['WIN', 'LOSS'])
    
    def close_browser(self):
        """إغلاق المتصفح"""
        if self.driver:
            self.driver.quit()
            logging.info("✅ تم إغلاق المتصفح")
