import schedule
import time
import threading
from datetime import datetime, timedelta
import logging
from config import UTC3_TZ

class TradingScheduler:
    def __init__(self):
        from qx_broker import QXBrokerManager
        from telegram_bot import TelegramBot
        from trading_engine import TradingEngine
        from monitoring_system import MonitoringSystem
        
        self.qx_manager = QXBrokerManager()
        self.telegram_bot = TelegramBot()
        self.trading_engine = TradingEngine()
        self.monitoring_system = MonitoringSystem(self.trading_engine, self.telegram_bot)
        
        self.stats = {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'net_profit': 0,
            'win_rate': 0,
            'current_streak': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'session_start': datetime.now(UTC3_TZ),
            'last_trade_time': None
        }
        
        self.pending_trades = {}
        self.regular_schedule_started = False
        self.system_start_time = datetime.now(UTC3_TZ)
        
    def get_utc3_time(self):
        """الحصول على وقت UTC+3"""
        return datetime.now(UTC3_TZ)
    
    def keep_browser_alive(self):
        """الحفاظ على نشاط المتصفح بين الصفقات"""
        try:
            self.qx_manager.keep_alive()
            logging.debug("✅ تم الحفاظ على نشاط المتصفح")
        except Exception as e:
            logging.error(f"❌ خطأ في الحفاظ على نشاط المتصفح: {e}")
            self.monitoring_system.log_error("BROWSER_KEEP_ALIVE", str(e))
    
    def start_24h_trading(self):
        """بدء التداول 24 ساعة بتوقيت UTC+3"""
        logging.info("🚀 بدء التداول 24 ساعة بتوقيت UTC+3...")
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        self.telegram_bot.send_message(
            f"🎯 <b>بدء تشغيل البوت بنجاح!</b>\n\n"
            f"📊 البوت يعمل الآن 24 ساعة\n"
            f"🔄 صفقة كل 3 دقائق\n"
            f"⏰ الوقت الحالي: {current_time} (UTC+3)\n"
            f"📈 نظام التحليل الفني: نشط\n"
            f"🛡️ نظام المراقبة: نشط\n\n"
            f"🚀 <i>استعد لفرص ربح مستمرة!</i>"
        )
        
        # بدء أول صفقة فورية
        self.start_immediate_trade()
        
        # جدولة الصفقات المنتظمة كل 3 دقائق
        self.schedule_regular_trades()
        
        # جدولة المهام الدورية
        self.schedule_periodic_tasks()
    
    def start_immediate_trade(self):
        """بدء أول صفقة فورية"""
        try:
            now_utc3 = self.get_utc3_time()
            next_trade_time = now_utc3.replace(second=0, microsecond=0) + timedelta(minutes=1)
            time_until_trade = (next_trade_time - now_utc3).total_seconds()
            
            logging.info(f"⏰ أول صفقة بعد: {time_until_trade:.0f} ثانية - الساعة: {next_trade_time.strftime('%H:%M:%S')} (UTC+3)")
            
            threading.Timer(time_until_trade, self.execute_trade_cycle).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة الفورية: {e}")
            self.monitoring_system.log_error("IMMEDIATE_TRADE", str(e))
    
    def schedule_regular_trades(self):
        """جدولة الصفقات كل 3 دقائق بتوقيت UTC+3"""
        schedule.clear()
        
        # جدولة صفقة كل 3 دقائق على مدار 24 ساعة
        for hour in range(0, 24):
            for minute in range(0, 60, 3):
                schedule_time = f"{hour:02d}:{minute:02d}"
                schedule.every().day.at(schedule_time).do(self.execute_trade_cycle)
        
        logging.info("✅ تم جدولة الصفقات كل 3 دقائق بتوقيت UTC+3")
    
    def schedule_periodic_tasks(self):
        """جدولة المهام الدورية"""
        # الحفاظ على نشاط المتصفح كل 5 دقائق
        schedule.every(5).minutes.do(self.keep_browser_alive)
        
        # إرسال تقرير الصحة كل ساعة
        schedule.every().hour.do(self.send_health_report)
        
        # إرسال إحصائيات كل 6 ساعات
        schedule.every(6).hours.do(self.send_periodic_stats)
        
        logging.info("✅ تم جدولة المهام الدورية")
    
    def execute_trade_cycle(self):
        """دورة تنفيذ الصفقة الكاملة"""
        try:
            # تحديث وقت آخر نشاط
            self.stats['last_trade_time'] = self.get_utc3_time()
            
            # تحليل واتخاذ قرار باستخدام التحليل الفني
            trade_data = self.trading_engine.analyze_and_decide()
            
            # وقت التنفيذ بعد 60 ثانية
            execute_time = self.get_utc3_time() + timedelta(seconds=60)
            execute_time_str = execute_time.replace(second=0, microsecond=0).strftime("%H:%M:%S")
            
            # تخزين بيانات الصفقة
            trade_id = f"{execute_time_str}_{trade_data['pair']}_{trade_data['direction']}"
            self.pending_trades[trade_id] = {
                'data': trade_data,
                'start_time': execute_time,
                'end_time': execute_time + timedelta(seconds=30),
                'confidence': trade_data.get('confidence', 'LOW'),
                'analysis_method': trade_data.get('analysis_method', 'RANDOM')
            }
            
            # إرسال إشارة الصفقة مع معلومات التحليل الفني
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                execute_time_str,
                trade_data.get('confidence', 'LOW'),
                trade_data.get('analysis_method', 'RANDOM')
            )
            
            logging.info(f"📤 إشارة صفقة: {trade_data['pair']} - {trade_data['direction']} - {execute_time_str} (UTC+3)")
            logging.info(f"📊 الثقة: {trade_data.get('confidence', 'LOW')} - الطريقة: {trade_data.get('analysis_method', 'RANDOM')}")
            
            # تنفيذ الصفقة بعد 60 ثانية بالضبط
            threading.Timer(60, self.start_trade_execution, [trade_id]).start()
            
            # بدء الجدولة المنتظمة بعد الصفقة الأولى
            if not self.regular_schedule_started:
                self.regular_schedule_started = True
                self.start_regular_schedule_message()
                
        except Exception as e:
            logging.error(f"❌ خطأ في دورة الصفقة: {e}")
            self.monitoring_system.log_error("TRADE_CYCLE", str(e))
    
    def start_regular_schedule_message(self):
        """إرسال رسالة بدء الجدولة المنتظمة"""
        self.telegram_bot.send_message(
            "🔄 <b>بدء الجدولة المنتظمة</b>\n\n"
            "📊 البوت يعمل الآن بالنظام المنتظم\n"
            "⏰ صفقة كل 3 دقائق بتوقيت UTC+3\n"
            "📈 نظام التحليل الفني: نشط\n"
            "🛡️ نظام المراقبة: نشط\n\n"
            "🎯 <i>جاري تحضير الصفقات القادمة...</i>"
        )
    
    def start_trade_execution(self, trade_id):
        """بدء تنفيذ الصفقة في المنصة"""
        try:
            if trade_id not in self.pending_trades:
                logging.error(f"❌ لم يتم العثور على الصفقة: {trade_id}")
                return
                
            trade_info = self.pending_trades[trade_id]
            trade_data = trade_info['data']
            
            # تنفيذ الصفقة في المنصة
            success = self.qx_manager.execute_trade(
                trade_data['pair'],
                trade_data['direction'],
                trade_data['duration']
            )
            
            if success:
                logging.info(f"✅ بدء صفقة في المنصة: {trade_data['pair']} - {trade_data['direction']}")
                self.monitoring_system.log_success()
                
                # جدولة نشر النتيجة بعد 30 ثانية
                time_until_result = (trade_info['end_time'] - self.get_utc3_time()).total_seconds()
                threading.Timer(time_until_result, self.publish_trade_result, [trade_id]).start()
            else:
                logging.error(f"❌ فشل تنفيذ الصفقة في المنصة: {trade_data['pair']}")
                self.monitoring_system.log_error("TRADE_EXECUTION", f"فشل تنفيذ {trade_data['pair']}")
                
        except Exception as e:
            logging.error(f"❌ خطأ في تنفيذ الصفقة: {e}")
            self.monitoring_system.log_error("TRADE_EXECUTION", str(e))
    
    def publish_trade_result(self, trade_id):
        """نشر نتيجة الصفقة بعد 30 ثانية"""
        try:
            if trade_id not in self.pending_trades:
                logging.error(f"❌ لم يتم العثور على الصفقة للنشر: {trade_id}")
                return
                
            trade_info = self.pending_trades[trade_id]
            trade_data = trade_info['data']
            
            # الحصول على النتيجة من المنصة
            result = self.qx_manager.get_trade_result()
            
            # تحديث الإحصائيات
            self.stats = self.trading_engine.update_stats(result, self.stats)
            
            # إرسال النتيجة مع معلومات التحليل
            self.telegram_bot.send_trade_result(
                trade_data['pair'],
                result,
                self.stats,
                trade_info['confidence'],
                trade_info['analysis_method']
            )
            
            current_time = self.get_utc3_time().strftime("%H:%M:%S")
            logging.info(f"🎯 نتيجة صفقة: {trade_data['pair']} - {result} - الوقت: {current_time} (UTC+3)")
            
            # تسجيل النجاح في نظام المراقبة
            if result == 'WIN':
                self.monitoring_system.log_success()
            
            # مسح الصفقة
            del self.pending_trades[trade_id]
            
            # إحصائيات كل 10 صفقات
            if self.stats['total_trades'] % 10 == 0:
                self.send_periodic_stats()
            
        except Exception as e:
            logging.error(f"❌ خطأ في نشر النتيجة: {e}")
            self.monitoring_system.log_error("RESULT_PUBLISHING", str(e))
    
    def send_periodic_stats(self):
        """إرسال إحصائيات دورية"""
        try:
            current_time = self.get_utc3_time().strftime("%H:%M:%S")
            session_duration = self.get_utc3_time() - self.stats['session_start']
            hours, remainder = divmod(session_duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            stats_text = f"""
📊 <b>إحصائيات دورية</b>

• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• صافي الربح: {self.stats['net_profit']}
• معدل الربح: {self.stats['win_rate']:.1f}%
• أقوى سلسلة ربح: {self.stats['max_win_streak']}
• أقوى سلسلة خسارة: {self.stats['max_loss_streak']}

⏰ مدة الجلسة: {int(hours)}h {int(minutes)}m
🕒 آخر تحديث: {current_time} (UTC+3)

🎯 <i>استمر في التداول بذكاء!</i>
"""
            self.telegram_bot.send_message(stats_text)
            
        except Exception as e:
            logging.error(f"❌ خطأ في إرسال الإحصائيات: {e}")
    
    def send_health_report(self):
        """إرسال تقرير صحة النظام"""
        try:
            health_report = self.monitoring_system.get_system_health()
            self.telegram_bot.send_message(health_report)
        except Exception as e:
            logging.error(f"❌ خطأ في إرسال تقرير الصحة: {e}")
    
    def check_system_health(self):
        """فحص صحة النظام بشكل دوري"""
        try:
            # فحص آخر نشاط
            if self.stats['last_trade_time']:
                time_since_last_trade = (self.get_utc3_time() - self.stats['last_trade_time']).total_seconds()
                if time_since_last_trade > 600:  # 10 دقائق بدون صفقات
                    self.monitoring_system.send_alert(f"⚠️ لم يتم تنفيذ صفقات منذ {int(time_since_last_trade/60)} دقائق")
            
            # فحص عدد الأخطاء المتتالية
            if self.monitoring_system.performance_metrics['consecutive_errors'] >= 5:
                self.monitoring_system.send_alert("🔴 حالة حرجة! البوت يواجه صعوبات متتالية في التنفيذ")
                
        except Exception as e:
            logging.error(f"❌ خطأ في فحص صحة النظام: {e}")
    
    def run_scheduler(self):
        """تشغيل الجدولة مع المراقبة المستمرة"""
        try:
            self.start_24h_trading()
            
            # جدولة فحص صحة النظام كل 10 دقائق
            schedule.every(10).minutes.do(self.check_system_health)
            
            logging.info("✅ بدء تشغيل الجدولة والمراقبة...")
            
            # حلقة التشغيل الرئيسية
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                    
                    # فحص صحة النظام كل دقيقة (بدون استخدام schedule)
                    current_time = self.get_utc3_time()
                    if hasattr(self, 'last_health_check'):
                        if (current_time - self.last_health_check).total_seconds() >= 60:
                            self.check_system_health()
                            self.last_health_check = current_time
                    else:
                        self.last_health_check = current_time
                        
                except Exception as e:
                    logging.error(f"❌ خطأ في حلقة الجدولة: {e}")
                    time.sleep(5)  # انتظار قبل إعادة المحاولة
                    
        except Exception as e:
            logging.error(f"❌ خطأ فادح في تشغيل الجدولة: {e}")
            self.monitoring_system.send_alert(f"🔴 توقف النظام: {e}")
            
            # إعادة التشغيل بعد 30 ثانية
            logging.info("🔄 إعادة تشغيل الجدولة بعد 30 ثانية...")
            time.sleep(30)
            self.run_scheduler()
