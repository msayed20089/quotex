import logging
import time
import threading
from datetime import datetime
from config import UTC3_TZ

class MonitoringSystem:
    """نظام مراقبة مبسط لأداء البوت"""
    
    def __init__(self, trading_engine=None, telegram_bot=None):
        self.trading_engine = trading_engine
        self.telegram_bot = telegram_bot
        self.performance_metrics = {
            'start_time': datetime.now(UTC3_TZ),
            'total_errors': 0,
            'consecutive_errors': 0,
            'last_successful_trade': None,
            'system_uptime': 0,
            'performance_alerts': []
        }
        
    def log_error(self, error_type, error_message):
        """تسجيل الأخطاء"""
        self.performance_metrics['total_errors'] += 1
        self.performance_metrics['consecutive_errors'] += 1
        
        error_data = {
            'type': error_type,
            'message': error_message,
            'timestamp': datetime.now(UTC3_TZ).strftime("%H:%M:%S")
        }
        
        self.performance_metrics['performance_alerts'].append(error_data)
        
        # الحفاظ على آخر 50 تنبيه فقط
        if len(self.performance_metrics['performance_alerts']) > 50:
            self.performance_metrics['performance_alerts'] = self.performance_metrics['performance_alerts'][-50:]
        
        logging.warning(f"⚠️ خطأ مسجل: {error_type} - {error_message}")
    
    def log_success(self):
        """تسجيل نجاح الصفقة"""
        self.performance_metrics['consecutive_errors'] = 0
        self.performance_metrics['last_successful_trade'] = datetime.now(UTC3_TZ)
        logging.info("✅ تم تسجيل نجاح الصفقة")
    
    def send_alert(self, message):
        """إرسال تنبيه عبر التليجرام"""
        try:
            if self.telegram_bot:
                current_time = datetime.now(UTC3_TZ).strftime("%H:%M:%S")
                alert_message = f"🚨 <b>تنبيه نظام المراقبة</b>\n\n{message}\n\n⏰ الوقت: {current_time}"
                self.telegram_bot.send_message(alert_message)
            else:
                logging.warning(f"🚨 تنبيه: {message}")
        except Exception as e:
            logging.error(f"❌ خطأ في إرسال التنبيه: {e}")
    
    def get_system_health(self):
        """الحصول على تقرير صحة النظام"""
        try:
            current_time = datetime.now(UTC3_TZ)
            uptime = current_time - self.performance_metrics['start_time']
            uptime_hours = uptime.total_seconds() / 3600
            
            health_report = f"""
🩺 <b>تقرير صحة النظام</b>

⏰ وقت التشغيل: {uptime_hours:.1f} ساعة
📊 إجمالي الأخطاء: {self.performance_metrics['total_errors']}
🔴 أخطاء متتالية: {self.performance_metrics['consecutive_errors']}
✅ آخر صفقة ناجحة: {self.performance_metrics['last_successful_trade'].strftime('%H:%M:%S') if self.performance_metrics['last_successful_trade'] else 'N/A'}

📈 <i>حالة النظام: {'🟢 ممتازة' if self.performance_metrics['consecutive_errors'] == 0 else '🟡 متوسطة' if self.performance_metrics['consecutive_errors'] < 3 else '🔴 حرجة'}</i>
"""
            return health_report
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء تقرير الصحة: {e}")
            return "🩺 <b>تقرير صحة النظام</b>\n\n⚠️ غير متوفر حاليًا"
    
    def run_health_check(self):
        """تشغيل فحص صحة دوري"""
        try:
            # إذا كان هناك أكثر من 5 أخطاء متتالية، إرسال تنبيه عاجل
            if self.performance_metrics['consecutive_errors'] >= 5:
                self.send_alert("🔴 حالة حرجة! البوت يواجه صعوبات متتالية في التنفيذ")
        except Exception as e:
            logging.error(f"❌ خطأ في فحص الصحة: {e}")
