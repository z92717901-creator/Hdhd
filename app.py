import asyncio
import json
import os
import threading
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ================== الإعدادات ==================
API_ID = 39932829
API_HASH = "af065af801fedce625b300cee1cc7e53"
SOURCE_BOT_ID = "@Gg5677bot"
SESSION_STRING = "1ApWapzMBu7unu6O4wHY30mW1plFpKZOSTWLTCsgJyFyjYa1UwxSTAODTNmqQNxQfaNW71TLIxHySeorVvEPr31JbtdXyTp6i4ZDcvi0hBAa5a3lQYunvw9O5mPalQieos18iCZAKL44u5pWR7v6sMOqsYiBx-C9mC9x7tRClkEQXAFHRqpc_IsaE_5bCCx5NmVNZLMJtibeIUyrzFNDiBXFO67wUTTwmomaAJ2gx8rGxIcf4SJQhzq_dfSDDFIcttffXSr5bs1g2RKBRk3AqdTp6HHXPsEp5UuVihlbryYo9tKMp9x0n3Fl4Qai1K7CWXvgKP80WpS-h5OXWLTh3qP3twyei1sU="

MESSAGES_FILE = "messages.json"

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

# ================== نظام حفظ الرسائل ==================
messages = []

def load_messages():
    global messages
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except Exception:
            messages = []

def save_messages():
    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving messages: {e}")

load_messages()

# ================== واجهة HTML (تصميم مائي واحترافي) ==================
HTML_CODE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>محطة نبع الصويرة 📍</title>
<style>
  /* خلفية مائية متدرجة */
  body { 
    font-family: 'Segoe UI', Tahoma, sans-serif; 
    background: linear-gradient(135deg, #0f172a 0%, #0c4a6e 100%);
    color: #e2e8f0; 
    margin: 0; 
    padding: 20px; 
    padding-bottom: 100px; 
    min-height: 100vh;
  }
  
  /* ترويسة الموقع */
  header { 
    text-align: center; 
    padding: 15px; 
    background: rgba(14, 116, 144, 0.4); 
    backdrop-filter: blur(10px);
    border-radius: 15px;
    border: 1px solid rgba(56, 189, 248, 0.3);
    margin-bottom: 25px; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }
  h1 { 
    margin: 0; 
    color: #38bdf8; 
    font-size: 24px; 
    text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
  }
  
  /* حاوية الرسائل */
  #messages { 
    max-width: 850px; 
    margin: auto; 
    display: flex; 
    flex-direction: column; 
    gap: 14px; 
  }
  
  /* فقاعات الرسائل */
  .msg { 
    background: rgba(30, 58, 138, 0.6); /* أزرق داكن للبوت */
    backdrop-filter: blur(5px);
    border-right: 4px solid #38bdf8; 
    padding: 15px; 
    border-radius: 15px 0 15px 15px; 
    animation: fadeIn 0.3s ease;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  }
  .msg.me { 
    background: rgba(6, 78, 59, 0.7); /* أخضر مائل للأزرق لك */
    border-right-color: #22c55e; 
    border-radius: 0 15px 15px 15px;
  }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .meta { 
    font-size: 12px; 
    color: #94a3b8; 
    margin-bottom: 8px; 
    font-weight: bold;
  }
  .content { 
    font-size: 16px; 
    line-height: 1.6; 
    white-space: pre-wrap; 
    word-break: break-word; 
  }
  
  /* أزرار البوت */
  .buttons-container { 
    display: flex; 
    flex-wrap: wrap; 
    gap: 8px; 
    margin-top: 12px; 
  }
  .bot-btn { 
    background: linear-gradient(90deg, #0284c7, #38bdf8); 
    color: white; 
    border: none; 
    padding: 10px 15px; 
    border-radius: 8px; 
    cursor: pointer; 
    font-weight: bold;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  }
  .bot-btn:hover { 
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.6);
  }
  
  /* زر البدء الكبير الثابت */
  #start-box { 
    position: fixed; 
    bottom: 0; 
    left: 0; 
    right: 0; 
    background: rgba(15, 23, 42, 0.9); 
    backdrop-filter: blur(10px);
    padding: 15px; 
    display: flex; 
    justify-content: center; 
    border-top: 1px solid rgba(56, 189, 248, 0.3); 
    z-index: 100;
  }
  #start-btn { 
    background: linear-gradient(90deg, #0ea5e9, #2563eb); 
    color: white; 
    border: none; 
    padding: 15px 40px; 
    border-radius: 30px; 
    font-size: 18px; 
    font-weight: bold; 
    cursor: pointer; 
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
    transition: transform 0.2s, box-shadow 0.2s;
    width: 100%;
    max-width: 400px;
  }
  #start-btn:hover { 
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6);
  }
  #start-btn:active { transform: translateY(1px); }
</style>
</head>
<body>
<header>
  <h1>📍 محطة نبع الصويرة</h1>
</header>

<div id="messages"><div style="text-align:center; color:#64748b; padding:20px;">مرحباً بك في محطة نبع الصويرة، اضغط على زر البدء بالأسفل للتفاعل مع البوت...</div></div>

<!-- زر البدء الكبير -->
<div id="start-box">
  <button id="start-btn" onclick="sendStart()">🚀 اضغط /start للبدء</button>
</div>

<script>
let lastCount = -1;

// دالة لجلب الرسائل وعرضها من الأقدم للأحدث (تنزل للأسفل)
async function loadMessages() {
  try {
    const res = await fetch('/api/messages');
    const data = await res.json();
    if (data.length === lastCount) return;
    
    const container = document.getElementById('messages');
    if (data.length === 0) {
      container.innerHTML = '<div style="text-align:center; color:#64748b; padding:20px;">مرحباً بك في محطة نبع الصويرة، اضغط على زر البدء بالأسفل للتفاعل مع البوت...</div>';
      lastCount = 0;
      return;
    }
    
    container.innerHTML = '';
    
    // عرض الرسائل من الأقدم للأحدث (لتنزل الرسائل الجديدة للأسفل)
    for (const msg of data) {
      const div = document.createElement('div');
      div.className = 'msg' + (msg.is_me ? ' me' : '');
      const date = new Date(msg.date * 1000).toLocaleTimeString('ar', {hour: '2-digit', minute:'2-digit'});
      let html = `<div class="meta">${msg.is_me ? '👤 أنت' : '🤖 نبع الصويرة'} • ${date}</div>`;
      
      if (msg.text) html += `<div class="content">${escapeHtml(msg.text)}</div>`;
      
      // إضافة أزرار البوت إن وجدت
      if (msg.buttons && msg.buttons.length > 0) {
        html += `<div class="buttons-container">`;
        msg.buttons.forEach(btnText => {
          html += `<button class="bot-btn" onclick="clickButton(${msg.id}, '${btnText}')">${btnText}</button>`;
        });
        html += `</div>`;
      }
      
      div.innerHTML = html;
      container.appendChild(div);
    }
    lastCount = data.length;
    
    // النزول التلقائي لأسفل الصفحة
    window.scrollTo(0, document.body.scrollHeight);
  } catch (e) { console.error(e); }
}

// دالة إرسال /start عند الضغط على الزر
async function sendStart() {
  const btn = document.getElementById('start-btn');
  const originalText = btn.innerHTML;
  btn.innerHTML = 'جاري الإرسال...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/send', { 
      method: 'POST', 
      headers: {'Content-Type': 'application/json'}, 
      body: JSON.stringify({text: '/start'}) 
    });
    const data = await res.json();
    
    if (data.status === 'error') {
        alert('فشل الإرسال: ' + data.msg);
    } else {
        setTimeout(loadMessages, 500);
    }
  } catch(e) {
      alert('خطأ في الاتصال بالسيرفر');
  } finally {
      btn.innerHTML = originalText;
      btn.disabled = false;
  }
}

// دالة الضغط على أزرار البوت (Inline Buttons)
async function clickButton(msgId, btnText) {
  await fetch('/api/click', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({msg_id: msgId, btn_data: btnText}) });
  setTimeout(loadMessages, 1000);
}

// حماية النص من الأكواد الضارة
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// تحديث تلقائي كل ثانيتين
setInterval(loadMessages, 2000);
loadMessages();
</script>
</body>
</html>
"""

# ================== مسارات Flask ==================
@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/api/messages')
def get_messages():
    return jsonify(messages)

@app.route('/api/send', methods=['POST'])
def send_message():
    text = request.json.get('text', '')
    if not text: return jsonify({"status": "error", "msg": "الرسالة فارغة"}), 400
    
    async def send():
        if not client.is_connected():
            await client.connect()
        await client.send_message(SOURCE_BOT_ID, text)

    try:
        future = asyncio.run_coroutine_threadsafe(send(), loop)
        future.result(timeout=15) 
        
        messages.append({
            "id": int(datetime.now().timestamp()),
            "date": datetime.now().timestamp(),
            "text": f"أنت: {text}",
            "is_me": True,
            "buttons": []
        })
        save_messages()
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error: {e}") 
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/click', methods=['POST'])
def click_button():
    data = request.json
    async def click():
        msg = await client.get_messages(SOURCE_BOT_ID, ids=data.get('msg_id'))
        if msg:
            for row in msg.buttons:
                for btn in row:
                    if btn.text == data.get('btn_data'):
                        await msg.click(text=btn.text)
                        break
    try:
        future = asyncio.run_coroutine_threadsafe(click(), loop)
        future.result(timeout=10)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

# ================== مراقبة الرسائل ==================
@client.on(events.NewMessage(from_users=SOURCE_BOT_ID))
async def handler(event):
    msg = event.message
    buttons = [btn.text for row in msg.buttons for btn in row if btn.text] if msg.buttons else []
    messages.append({
        "id": msg.id,
        "date": msg.date.timestamp(),
        "text": msg.text or msg.caption or "",
        "is_me": False,
        "buttons": buttons
    })
    save_messages()

# ================== التشغيل ==================
async def start_client():
    try:
        await client.start()
        print("✓ Telethon is CONNECTED and READY!")
        
        try:
            await client.get_entity(SOURCE_BOT_ID) 
            print("✓ Bot entity loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load bot entity: {e}")

        await client.run_until_disconnected()
    except Exception as e:
        print(f"Telethon Start Error: {e}")

if __name__ == '__main__':
    def run_async_loop():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_client())
    
    threading.Thread(target=run_async_loop, daemon=True).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)