import random
from datetime import datetime
from config import CAIRO_TZ

class TradingEngine:
    def __init__(self):
        from config import TRADING_PAIRS
        self.pairs = TRADING_PAIRS
        
    def analyze_and_decide(self):
        """تحليل عشوائي واتخاذ قرار التداول"""
        pair = random.choice(self.pairs)
        direction = random.choice(['BUY', 'SELL'])
        
        # وقت توقيت القاهرة مع ثواني = 00
        cairo_time = datetime.now(CAIRO_TZ)
        trade_time = cairo_time.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        
        return {
            'pair': pair,
            'direction': direction,
            'trade_time': trade_time,
            'duration': 30
        }
    
    def update_stats(self, result, stats):
        """تحديث الإحصائيات"""
        stats['total_trades'] += 1
        
        if result == 'ربح':
            stats['win_trades'] += 1
        else:
            stats['loss_trades'] += 1
            
        stats['net_profit'] = stats['win_trades'] - stats['loss_trades']
        return stats
    
    def get_cairo_time(self):
        """الحصول على وقت القاهرة الحالي"""
        return datetime.now(CAIRO_TZ).strftime("%H:%M:%S")
