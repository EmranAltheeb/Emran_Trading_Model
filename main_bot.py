import time
import requests
import MetaTrader5 as mt5
from config import initialize_mt5, BOT_TOKEN, AVAILABLE_ASSETS
from indicators import get_market_data
from ai_agents import get_gemini_opinion, get_chatgpt_opinion, get_claude_opinion, get_manus_opinion, extract_agent_direction_ar

def send_telegram_message(message):
    """إرسال التوصيات والتقارير الفورية إلى بوت التيليجرام الخاص بك"""
    if not BOT_TOKEN:
        print("[⚠️ WARNING] توكن التيليجرام غير موجود في ملف .env")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # ملحوظة: تأكد من تغيير معرف الشات (chat_id) إلى الآيدي الرقمي الخاص بك أو اسم قناتك
    payload = {
        "chat_id": "@عمران_رادار_الذكاء_الاصطناعي", 
        "text": message, 
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"[⚠️ Telegram Error]: فشل إرسال الرسالة. استجابة السيرفر: {response.text}")
    except Exception as e:
        print(f"[Telegram Send Error]: {str(e)}")

def run_radar_system(trading_style="Scalping"):
    """المحرك الرئيسي لتشغيل الرادار وجمع تصويت اللجنة الرباعية واستخراج التوصية"""
    print(f"\n[📡 RADAR ACTIVE] بدأ رادار الفرز الذكي الآن بأسلوب: {trading_style}...")
    
    for asset in AVAILABLE_ASSETS:
        print(f"\n[🔍 ANALYZING] جاري سحب وتحليل معطيات الأصل المالي: {asset}...")
        
        # 1. سحب داتا الشموع والمؤشرات المعززة بـ Finnhub
        rsi, ema_9, ema_21, technical_report = get_market_data(asset, trading_style)
        
        # 2. بناء الـ Prompt الفائق والموحد للجنة التحكيمية الرباعية
        analysis_prompt = (
            f"You are an elite institutional financial analyst agent. Analyze this market data for {asset} ({trading_style} style):\n\n"
            f"{technical_report}\n\n"
            f"Technical Context Summary:\n"
            f"- Current RSI(14): {rsi:.2f}\n"
            f"- Fast Line EMA(9): {ema_9:.5f}\n"
            f"- Slow Line EMA(21): {ema_21:.5f}\n\n"
            f"CRITICAL INSTRUCTION:\n"
            f"Based on the price action, volatility (ATR), MACD momentum, Bollinger Bands, and global sentiment from Finnhub, provide your final decision.\n"
            f"Your output MUST contain exactly one of these strings: 'DIRECTION: BUY', 'DIRECTION: SELL', or 'DIRECTION: HOLD'. "
            f"Do not truncate this prefix."
        )
        
        # 3. استدعاء الوكلاء الأربعة بالتوازي للحصول على الآراء
        print(f"🤖 استدعاء الوكيل 1 (Gemini)...")
        gemini_raw = get_gemini_opinion(analysis_prompt)
        gemini_dir, gemini_txt = extract_agent_direction_ar(gemini_raw)
        
        print(f"🤖 استدعاء الوكيل 2 (ChatGPT)...")
        chatgpt_raw = get_chatgpt_opinion(analysis_prompt)
        chatgpt_dir, chatgpt_txt = extract_agent_direction_ar(chatgpt_raw)
        
        print(f"🤖 استدعاء الوكيل 3 (Claude)...")
        claude_raw = get_claude_opinion(analysis_prompt)
        claude_dir, claude_txt = extract_agent_direction_ar(claude_raw)
        
        print(f"🤖 استدعاء الوكيل 4 (Manus)...")
        manus_raw = get_manus_opinion(analysis_prompt)
        manus_dir, manus_txt = extract_agent_direction_ar(manus_raw)
        
        # 4. نظام التصويت وفرز الأغلبية الساحقة (75%+)
        votes = [gemini_dir, chatgpt_dir, claude_dir, manus_dir]
        buy_votes = votes.count("BUY")
        sell_votes = votes.count("SELL")
        
        decision_emoji = "⏳ حياد/انتظار (HOLD)"
        
        if buy_votes >= 3:
            decision_emoji = "🚀 شراء قادم بقوة (BUY)"
        elif sell_votes >= 3:
            decision_emoji = "💥 بيع قادم بقوة (SELL)"
            
        # 5. صياغة التقرير الاحترافي النهائي لإرساله كتوصية للتيليجرام
        report_message = (
            f"📊 **[توصية الرادار الرباعي الفائق]** 📊\n"
            f"• الأصل المالي: `{asset}`\n"
            f"• أسلوب الفرز: `{trading_style}`\n"
            f"• مؤشر RSI: `{rsi:.2f}`\n"
            f"----------------------------------\n"
            f"🧠 **تصويت لجنة الذكاء الاصطناعي:**\n"
            f"1️⃣ جمناي 2.5:  {gemini_txt}\n"
            f"2️⃣ جي بي تي 4: {chatgpt_txt}\n"
            f"3️⃣ كلود 3.5:   {claude_txt}\n"
            f"4️⃣ مانوس وكيل: {manus_txt}\n"
            f"----------------------------------\n"
            f"🔥 **التوصية المشتركة النهائية:**\n"
            f"🎯 `[{decision_emoji}]`\n"
        )
        
        print(f"🏁 النتيجة النهائية لـ {asset}: {decision_emoji}")
        
        # 6. إرسال التقرير والتوصية للتيليجرام فقط (تمت إزالة دالة التنفيذ الاوتوماتيكي بالكامل)
        send_telegram_message(report_message)
        
        # فترة انتظار قصيرة بين تدوير الأصول لمنع ضغط الـ API
        time.sleep(2)

if __name__ == "__main__":
    # تشغيل وتهيئة الاتصال بـ ميتاتريدر 5 لسحب الداتا فقط
    if initialize_mt5():
        try:
            # حلقة الرادار لمتابعة السوق وبث التوصيات كل 5 دقائق
            while True:
                run_radar_system(trading_style="Scalping")
                print("\n[💤 SLEEP] تم بث دورة التوصيات الحالية. انتظار 5 دقائق لبدء دورة الفرز القادمة...")
                time.sleep(300) 
        except KeyboardInterrupt:
            print("\n[🛑 STOP] تم إيقاف رادار التوصيات بناءً على طلبك.")
        finally:
            mt5.shutdown()