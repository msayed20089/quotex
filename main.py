from telegram_bot import TelegramBot
from scheduler import TradingScheduler
import logging
import threading
import time
import os
import sys

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # إرسال كل ال logs لـ stdout
    ]
)

logger = logging.getLogger(__name__)

def keep_alive_output():
    """إرسال output مستمر علشان Railway ما يوقفش ال container"""
    while True:
        logger.info("🔄 النظام يعمل بشكل طبيعي...")
        time.sleep(30)  # إرسال log كل 30 ثانية

def main():
    """الدالة الرئيسية مع تحسينات لـ Railway"""
    try:
        logger.info("⏳ جاري تهيئة النظام على Railway...")
        
        # بدء thread للإخراج المستمر
        output_thread = threading.Thread(target=keep_alive_output)
        output_thread.daemon = True
        output_thread.start()
        
        time.sleep(5)
        
        logger.info("🚀 بدء تشغيل بوت التداول 24 ساعة...")
        
        # اختبار بوت التليجرام
        telegram_bot = TelegramBot()
        
        if telegram_bot.send_message("🟢 **بدء تشغيل البوت على Railway**\n\nجاري تهيئة النظام..."):
            logger.info("✅ تم الاتصال بنجاح ببوت التليجرام")
        
        # تشغيل الجدولة
        logger.info("⏰ جاري تشغيل جدولة المهام...")
        scheduler = TradingScheduler()
        
        # تشغيل الجدولة في thread منفصل
        scheduler_thread = threading.Thread(target=scheduler.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logger.info("✅ بوت التداول الآلي يعمل بنجاح!")
        logger.info("📊 البوت سيبدأ الصفقات فوراً")
        logger.info("🔄 نظام الصفقات: كل 3 دقائق على مدار الساعة")
        logger.info("⏰ توقيت UTC+3 - الثواني دائماً: 00")
        
        # حلقة رئيسية بسيطة
        counter = 0
        while True:
            time.sleep(60)
            counter += 1
            if counter % 5 == 0:  # كل 5 دقائق
                logger.info("📡 البوت يعمل بشكل مستمر...")
            
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل: {e}")
        logger.info("🔄 إعادة التشغيل بعد 30 ثانية...")
        time.sleep(30)
        main()

if __name__ == "__main__":
    main()
