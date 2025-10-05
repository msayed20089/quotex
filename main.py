from telegram_bot import TelegramBot
from scheduler import TradingScheduler
import logging
import threading
import time
import os

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    try:
        logger.info("🚀 بدء تشغيل بوت التداول على Railway...")
        
        # اختبار بوت التليجرام
        telegram_bot = TelegramBot()
        
        if telegram_bot.send_message("🟢 **بدء تشغيل البوت**\n\nجاري تهيئة النظام..."):
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
        logger.info("🔄 نظام الصفقات: كل 3 دقائق")
        
        # البقاء في حلقة رئيسية
        while True:
            time.sleep(60)
            
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل: {e}")
        logger.info("🔄 إعادة التشغيل بعد 30 ثانية...")
        time.sleep(30)
        main()

if __name__ == "__main__":
    main()
