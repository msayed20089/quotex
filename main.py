from qx_broker import QXBrokerManager
from telegram_bot import TelegramBot
from trading_engine import TradingEngine
from scheduler import TradingScheduler
import logging
import threading
import time
import os
import sys

# إعداد التسجيل المتقدم
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_railway.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """تهيئة البيئة للتشغيل على Railway"""
    logger.info("🔧 جاري تهيئة البيئة لـ Railway...")
    
    # فحص المتغيرات البيئية
    required_vars = ['TELEGRAM_TOKEN', 'QX_EMAIL', 'QX_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"⚠️  متغيرات بيئية مفقودة: {missing_vars}")
        logger.info("ℹ️  استخدام القيم الافتراضية من config.py")
    
    logger.info("✅ اكتملت تهيئة البيئة")

def health_monitor():
    """مراقبة صحة البوت وإرسال تقارير دورية"""
    telegram_bot = TelegramBot()
    error_count = 0
    
    while True:
        try:
            # إرسال تقرير صحة كل 6 ساعات
            if int(time.time()) % 21600 == 0:  # كل 6 ساعات
                telegram_bot.send_message("🟢 البوت يعمل بشكل طبيعي على Railway")
                logger.info("📊 تم إرسال تقرير الصحة")
            
            time.sleep(1)
            
        except Exception as e:
            error_count += 1
            logger.error(f"❌ خطأ في مراقب الصحة: {e}")
            if error_count >= 5:
                logger.critical("🆘 إعادة تشغيل مراقب الصحة بعد أخطاء متعددة")
                break

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    logger.info("🚀 بدء تشغيل بوت التداول على Railway...")
    
    # تهيئة البيئة
    setup_environment()
    
    # إرسال رسالة بدء التشغيل
    telegram_bot = TelegramBot()
    telegram_bot.send_message("🎯 **بدء تشغيل بوت التداول على Railway**\n\n✅ البوت يعمل الآن على السحابة\n⏰ جاري تهيئة جدول التداول...")
    
    while True:
        try:
            # اختبار الاتصال بمنصة QX Broker
            logger.info("🔗 جاري اختبار الاتصال بمنصة QX Broker...")
            qx_manager = QXBrokerManager()
            
            if qx_manager.login():
                logger.info("✅ تم الاتصال بنجاح بمنصة QX Broker")
                telegram_bot.send_message("✅ **تم الاتصال بمنصة QX Broker**\n\n📊 جاهز لبدء التداول الآلي")
            else:
                logger.warning("⚠️  فشل الاتصال بمنصة QX Broker، الاستمرار في وضع المحاكاة")
                telegram_bot.send_message("⚠️ **وضع المحاكاة**\n\n🔧 البوت يعمل في وضع المحاكاة، الصفقات للتجربة فقط")
            
            # تشغيل الجدولة
            logger.info("⏰ جاري تشغيل جدولة المهام...")
            scheduler = TradingScheduler()
            
            # تشغيل الجدولة في thread منفصل
            scheduler_thread = threading.Thread(target=scheduler.run_scheduler, daemon=True)
            scheduler_thread.start()
            
            # تشغيل مراقب الصحة في thread منفصل
            health_thread = threading.Thread(target=health_monitor, daemon=True)
            health_thread.start()
            
            logger.info("✅ بوت التداول الآلي يعمل بنجاح على Railway!")
            
            # البقاء في حلقة رئيسية للمراقبة
            while True:
                if not scheduler_thread.is_alive():
                    logger.error("❌ توقف thread الجدولة، إعادة التشغيل...")
                    break
                    
                if not health_thread.is_alive():
                    logger.error("❌ توقف thread مراقب الصحة، إعادة التشغيل...")
                    break
                    
                time.sleep(30)
                
        except Exception as e:
            logger.critical(f"💥 خطأ حرج في البوت: {e}")
            logger.info("🔄 إعادة تشغيل البوت بعد 60 ثانية...")
            
            try:
                telegram_bot.send_message(f"🔄 **إعادة تشغيل البوت**\n\n⚠️ حدث خطأ: {str(e)[:100]}...\n\nجاري إعادة التشغيل تلقائياً...")
            except:
                pass
                
            time.sleep(60)

if __name__ == "__main__":
    main()