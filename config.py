import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

# شحن المتغيرات والمفاتيح البيئية من ملف .env
load_dotenv()

# سحب المفاتيح الرسمية والمباشرة للوكلاء الـ 4 ومنصة التحليل
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY_PRIMARY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
MANUS_KEY = os.getenv("MANUS_API_KEY")
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")

# إعدادات ملف التوثيق والأصول المالية المعززة بالرادار
EXCEL_FILE = "trading_signals_log.xlsx"
AVAILABLE_ASSETS = ['XAUUSDs', 'US30s', 'EURUSDs', 'GBPUSDs', 'AUDUSDs', 'US.ITs']

def initialize_mt5():
    """الدالة المسؤولة عن بدء تشغيل منصة ميتاتريدر 5 وضمان استقرار الاتصال اللحظي"""
    if not mt5.initialize():
        print(f"[❌ ERROR] فشل الاتصال بمنصة MT5. السبب: {mt5.last_error()}")
        return False
    print("[✅ INITIALIZATION] تم ربط نظام الرادار بسيرفر MT5 الحي بنجاح تام.")
    return True