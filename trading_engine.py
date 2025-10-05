def analyze_and_decide(self):
    """تحليل عشوائي واتخاذ قرار التداول"""
    pair = random.choice(self.pairs)
    direction = random.choice(['BUY', 'SELL'])
    
    # وقت دقيق بدون ثواني
    current_time = datetime.now()
    trade_time = current_time.replace(second=0, microsecond=0).strftime("%H:%M:00")
    
    return {
        'pair': pair,
        'direction': direction,
        'trade_time': trade_time,
        'duration': 30
    }
