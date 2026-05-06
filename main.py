import pandas as pd
import requests
import ta
import google.generativeai as genai
import time
import os

# --- 24/7 CREDENTIALS ---
# If using a cloud host like Railway, set these in the 'Environment Variables' tab
BOT_TOKEN = "8631671782:AAG5LU-Ah-gem6suZ8FlwzMU0aHnH9wblCM"
CHAT_ID = "935615512"
API_KEY = "1bf508be06f94bacab3517cb4871b0a5"
GEMINI_KEY = "AIzaSyCaV09AUXfW7Dv2POXdDiVUKLoxk5wwJN0"

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_sovereign_data():
    """Pulls Gold data while strictly respecting the 8 calls/min limit."""
    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=50&apikey={API_KEY}"
    try:
        r = requests.get(url).json()
        if 'values' in r:
            df = pd.DataFrame(r['values']).astype({'close': float})
            df = df.iloc[::-1].reset_index(drop=True)
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            df['ema'] = ta.trend.ema_indicator(df['close'], window=200)
            return df
    except: return None

def execute_avatar_logic(msg, df):
    """The Heavy Lifting: Clinical logic with Zero-Assistant behavior."""
    last = df.iloc[-1]
    protocol = (
        f"AVATAR MODE: SOVEREIGN ALPHA-6\n"
        f"MISSION: $10k RECOVERY\n"
        f"DATA: XAU/USD ${last['close']} | RSI {last['rsi']:.1f}\n"
        "MANDATORY: Verify Trend, TV Indicators, DXY/Oil, and Worst Case."
    )
    try:
        response = ai_model.generate_content(f"{protocol}\n\nABU COMMAND: {msg}")
        return response.text
    except: return "📟 AVATAR SYNC FAILED."

# --- THE PERMANENT LOOP ---
def main():
    last_id = 0
    # Clear queue so we don't reply to old messages on restart
    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1")
    
    print("📟 Sovereign Alpha-6 Avatar is LIVE and 24/7.")
    
    while True:
        try:
            # Poll Telegram for your commands
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_id+1}&timeout=20"
            updates = requests.get(url).json()
            
            if updates.get("result"):
                df = fetch_sovereign_data() # Only fetch when you ask to save quota
                for up in updates["result"]:
                    last_id = up["update_id"]
                    msg = up.get("message", {}).get("text", "")
                    
                    if df is not None:
                        reply = execute_avatar_logic(msg, df)
                        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={reply}&parse_mode=Markdown")
            
            time.sleep(5) # Throttled to ensure Zero-Error quota management
        except Exception as e:
            time.sleep(10) # Auto-reconnect logic

if __name__ == "__main__":
    main()
