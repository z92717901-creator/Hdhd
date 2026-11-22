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
        print(f"Error: {e}")

load_messages()

# ================== واجهة HTML (ألوان هادئة + إشعارات + نطق) ==================
HTML_CODE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>محطة نبع الصويرة 📍</title>
<style>
  body { 
    font-family: 'Segoe UI', Tahoma, sans-serif; 
    background-color: #121212; 
    color: #e0e0e0; 
    margin: 0; 
    padding: 20px; 
    padding-bottom: 100px; 
    min-height: 100vh;
  }
  header { 
    text-align: center; 
    padding: 15px; 
    background-color: #1e1e1e; 
    border-bottom: 2px solid #2c3e50; 
    margin-bottom: 20px;
    border-radius: 12px;
  }
  h1 { margin: 0; color: #90caf9; font-size: 22px; font-weight: 600; }
  #messages { max-width: 850px; margin: auto; display: flex; flex-direction: column; gap: 12px; }
  .msg { background-color: #1e1e1e; border-right: 3px solid #90caf9; padding: 14px; border-radius: 12px 0 12px 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
  .msg.me { background-color: #233442; border-right-color: #4caf50; border-radius: 0 12px 12px 12px; }
  .meta { font-size: 11px; color: #9e9e9e; margin-bottom: 6px; }
  .content { font-size: 15px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
  
  .buttons-container { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .bot-btn { background-color: #2c3e50; color: #e0e0e0; border: 1px solid #546e7a; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 14px; transition: background 0.2s; }
  .bot-btn:hover { background-color: #37474f; }
  
  #start-box { position: fixed; bottom: 0; left: 0; right: 0; background-color: #1e1e1e; padding: 15px; display: flex; justify-content: center; border-top: 1px solid #2c3e50; z-index: 100; }
  #start-btn { background-color: #1a73e8; color: white; border: none; padding: 14px 30px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%; max-width: 400px; transition: background 0.2s; }
  #start-btn:hover { background-color: #1557b0; }

  /* شاشة تفعيل الصوت */
  #audio-permission { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 999; justify-content: center; align-items: center; flex-direction: column; text-align: center; color: white; }
  #audio-permission button { padding: 15px 30px; font-size: 18px; background: #1a73e8; color: white; border: none; border-radius: 8px; margin-top: 20px; cursor: pointer; }
</style>
</head>
<body>

<!-- شاشة تفعيل الصوت -->
<div id="audio-permission">
  <h2>🔔 لتشغيل الإشعارات الصوتية</h2>
  <p>اضغط في أي مكان على الشاشة لتفعيل الصوت</p>
  <button onclick="enableAudio()">تفعيل الصوت الآن</button>
</div>

<header>
  <h1>📍 محطة نبع الصويرة</h1>
</header>

<div id="messages"><div style="text-align:center; color:#9e9e9e; padding:20px;">مرحباً بك، اضغط على الزر بالأسفل للتفاعل مع البوت.</div></div>

<div id="start-box">
  <button id="start-btn" onclick="sendStart()">🚀 اضغط /start للبدء</button>
</div>

<!-- عنصر صوتي مخفي للإشعارات -->
<audio id="notification-sound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

<script>
let lastCount = -1;
let audioEnabled = false;

// تفعيل الصوت بمجرد أول تفاعل من المستخدم
function enableAudio() {
    const audio = document.getElementById('notification-sound');
    // تشغيل وإيقاف سريع لتفعيل الصوت في المتصفح
    audio.volume = 0;
    audio.play().then(() => {
        audio.pause();
        audio.currentTime = 0;
        audio.volume = 1;
        audioEnabled = true;
        document.getElementById('audio-permission').style.display = 'none';
        console.log("تم تفعيل الصوت بنجاح");
    }).catch(e => {
        console.log("فشل تفعيل الصوت:", e);
    });
}

// دالة النطق بالصوت العربي العراقي
function speakText(text) {
    if (!('speechSynthesis' in window)) {
        console.log("المتصفح لا يدعم النطق");
        return;
    }
    
    // إيقاف أي نطق سابق
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ar-IQ'; // اللهجة العراقية
    utterance.rate = 1.0; // سرعة النطق
    utterance.pitch = 1.0; // حدة الصوت
    
    // محاولة اختيار صوت عربي إذا كان متاحاً
    const voices = window.speechSynthesis.getVoices();
    const arabicVoice = voices.find(voice => voice.lang.includes('ar'));
    if (arabicVoice) {
        utterance.voice = arabicVoice;
    }
    
    window.speechSynthesis.speak(utterance);
}

// تشغيل الرنين تلقائياً مع الرسائل الجديدة
async function loadMessages() {
  try {
    const res = await fetch('/api/messages');
    const data = await res.json();
    
    if (data.length === lastCount) return;
    
    // تشغيل الإشعار (الرنين) إذا كانت هناك رسالة جديدة من البوت
    if (lastCount !== -1 && data.length > lastCount) {
        const lastMsg = data[data.length - 1];
        if (!lastMsg.is_me && audioEnabled) {
            playNotification();
        }
    }

    const container = document.getElementById('messages');
    if (data.length === 0) {
      container.innerHTML = '<div style="text-align:center; color:#9e9e9e; padding:20px;">مرحباً بك، اضغط على الزر بالأسفل للتفاعل مع البوت.</div>';
      lastCount = 0;
      return;
    }
    
    container.innerHTML = '';
    
    for (const msg of data) {
      const div = document.createElement('div');
      div.className = 'msg' + (msg.is_me ? ' me' : '');
      const date = new Date(msg.date * 1000).toLocaleTimeString('ar', {hour: '2-digit', minute:'2-digit'});
      let html = `<div class="meta">${msg.is_me ? '👤 أنت' : '🤖 نبع الصويرة'} • ${date}</div>`;
      
      if (msg.text) html += `<div class="content">${escapeHtml(msg.text)}</div>`;
      
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
    window.scrollTo(0, document.body.scrollHeight);
  } catch (e) { console.error(e); }
}

function playNotification() {
    const audio = document.getElementById('notification-sound');
    audio.play().catch(e => console.log("المتصفح منع الصوت:", e));
}

async function sendStart() {
  // تفعيل الصوت فوراً عند الضغط على الزر
  if (!audioEnabled) enableAudio();
  speakText("تم البدء"); // نطق "تم البدء" بالعراقي

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
    if (data.status === 'error') alert('فشل الإرسال: ' + data.msg);
    else setTimeout(loadMessages, 500);
  } catch(e) {
      alert('خطأ في الاتصال بالسيرفر');
  } finally {
      btn.innerHTML = originalText;
      btn.disabled = false;
  }
}

async function clickButton(msgId, btnText) {
  // تفعيل الصوت إذا لم يكن مفعلاً
  if (!audioEnabled) enableAudio();
  
  // نطق اسم الزر الذي تم الضغط عليه بالصوت العراقي
  speakText(btnText);

  await fetch('/api/click', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({msg_id: msgId, btn_data: btnText}) });
  setTimeout(loadMessages, 1000);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// التحدث بمجرد أول لمسة في أي مكان على الشاشة
document.body.addEventListener('click', function() {
    if (!audioEnabled) enableAudio();
}, { once: true });

// إظهار شاشة تفعيل الصوت إذا لم يتم تفعيله بعد
if (!audioEnabled) {
    document.getElementById('audio-permission').style.display = 'flex';
}

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
        except: pass
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