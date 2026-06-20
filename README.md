# 🤖 AI-Algorithmic-Trading-Assistant (Emran Trading Model)

A robust, multi-agent AI-driven algorithmic trading assistant designed to analyze financial markets (Gold, Indices, and Forex). The system integrates real-time technical analysis with a decentralized voting committee composed of four advanced LLM architectures to deliver precise market insights and automated trade signaling.

---

## 🚀 Key Features

* **Live MetaTrader 5 Integration:** Establishes secure, real-time connectivity with MT5 terminals for live market telemetry and order processing.
* **Advanced Technical Radar:** Automatically computes key market indicators, including RSI, EMA, ATR, MACD, and Bollinger Bands.
* **AI Quad-Agent Committee:** Orchestrates parallel execution of four top-tier AI models to aggregate market sentiment and achieve an optimal decision consensus (BUY, SELL, HOLD):
  1. **Gemini API**
  2. **ChatGPT API**
  3. **Claude API**
  4. **Manus AI API**
* **Risk Management & Execution:** Features dynamic pip calculation, automated Stop Loss (SL) and Take Profit (TP) assignment, and comprehensive Excel logging for analytical auditing.
* **Instant Telegram Broadcasting:** Streams beautifully formatted technical reports and verified signal alerts directly to a designated Telegram channel.

---

## 📁 Repository Structure

* `main_bot.py`: The central orchestrator that drives the system, coordinates analysis, and broadcasts signals.
* `indicators.py`: The technical core responsible for parsing historical data and injecting calculated indicators.
* `ai_agents.py`: Manages parallel API connections to the four AI agents and handles collective decision-making.
* `execution.py`: Handles mathematical risk execution, MT5 order formatting, and transaction logging.
* `config.py`: Central configurations, security credential loading, and initialization checks for MT5.
* `.gitignore`: Built-in security architecture preventing sensitive data (API keys, `.env`) from being exposed.

---

## 🛠️ Setup & Local Deployment

### 1. Environment Setup
Clone the repository and ensure your virtual environment is active. Install the required dependency stack:
```bash
pip install MetaTrader5 pandas requests python-dotenv
