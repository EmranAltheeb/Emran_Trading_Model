import os
import requests
import json
from config import GEMINI_KEY, OPENAI_KEY, ANTHROPIC_KEY, MANUS_KEY

# 1️⃣ الوكيل الأول: Gemini
def get_gemini_opinion(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"[Gemini API Error]: {str(e)}")
        return "DIRECTION: HOLD"

# 2️⃣ الوكيل الثاني: ChatGPT (OpenAI)
def get_chatgpt_opinion(prompt):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",  # موديل اقتصادي وسريع جداً للفرز الفوري
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2       # درجة حرارة منخفضة لضمان الدقة الحسابية وعدم العشوائية
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ChatGPT API Error]: {str(e)}")
        return "DIRECTION: HOLD"

# 3️⃣ الوكيل الثالث: Claude (Anthropic)
def get_claude_opinion(prompt):
    try:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-5-haiku-latest",  # ممتاز ومصمم خصيصاً للمهام السريعة والتحليلات الرقمية
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()['content'][0]['text']
    except Exception as e:
        print(f"[Claude API Error]: {str(e)}")
        return "DIRECTION: HOLD"

# 4️⃣ الوكيل الرابع: Manus
def get_manus_opinion(prompt):
    try:
        # رابط الـ API الافتراضي والقياسي لوكلاء Manus لإرسال المهام واستقبال التحليلات السريعة
        url = "https://api.manus.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MANUS_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "manus-agent-v1",  # الموديل المخصص للتحليل والتنفيذ المعقد
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"[Manus AI API Error]: {str(e)}")
        return "DIRECTION: HOLD"

# 🔍 دالة الفرز والترجمة الموحدة لاستخراج التوجه النهائي لكل وكيل برمجياً
def extract_agent_direction_ar(agent_output):
    out_upper = agent_output.upper()
    
    if "DIRECTION: BUY" in out_upper or "BUY" in out_upper: 
        return "BUY", "شراء 📈"
    if "DIRECTION: SELL" in out_upper or "SELL" in out_upper: 
        return "SELL", "بيع 📉"
    return "HOLD", "حياد/انتظار ⏳"