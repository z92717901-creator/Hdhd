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

messages = []
def load_messages():
    global messages
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except: messages = []
def save_messages():
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
load_messages()

# ================== واجهة HTML (تصميم مائي فاتح وجذاب) ==================
HTML_CODE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#0ea5e9">
<title>محطة نبع الصويرة 📍</title>
<style>
  /* ألوان مائية مبهجة ومريحة */
  body { 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    background-color: #f0f9ff; /* أزرق فاتح جداً */
    color: #334155; 
    margin: 0; 
    padding: 0; 
    min-height: 100vh;
  }
  
  /* الهيدر العلوي */
  header { 
    background: linear-gradient(135deg, #0ea5e9, #0284c7);
    color: white;
    text-align: center; 
    padding: 25px 15px; 
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.2);
    border-bottom-left-radius: 30px;
    border-bottom-right-radius: 30px;
    position: sticky;
    top: 0;
    z-index: 50;
  }
  h1 { 
    margin: 0; 
    font-size: 24px; 
    font-weight: 800;
    letter-spacing: 0.5px;
  }
  .subtitle {
    font-size: 13px;
    color: #e0f2fe;
    margin-top: 8px;
    font-weight: 500;
  }
  
  /* حاوية الرسائل */
  #messages { 
    max-width: 800px; 
    margin: 25px auto; 
    padding: 0 15px;
    display: flex; 
    flex-direction: column; 
    gap: 18px; 
    padding-bottom: 120px;
  }
  
  /* فقاعات الرسائل */
  .msg { 
    background: #ffffff; 
    color: #1e293b;
    padding: 16px 20px; 
    border-radius: 20px 20px 20px 6px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    max-width: 85%;
    align-self: flex-start;
    animation: slideUp 0.3s ease-out;
    border: 1px solid #f1f5f9;
  }
  .msg.me { 
    background: linear-gradient(135deg, #38bdf8, #0ea5e9); 
    color: #ffffff;
    border-radius: 20px 20px 6px 20px;
    align-self: flex-end;
    border: none;
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
  }
  
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .meta { 
    font-size: 11px; 
    color: #94a3b8; 
    margin-bottom: 8px; 
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .msg.me .meta { color: #e0f2fe; }
  
  .content { 
    font-size: 16px; 
    line-height: 1.6; 
    white-space: pre-wrap; 
    word-break: break-word; 
    font-weight: 500;
  }
  
  /* أزرار البوت */
  .buttons-container { 
    display: flex; 
    flex-wrap: wrap; 
    gap: 10px; 
    margin-top: 15px; 
  }
  .bot-btn { 
    background-color: #f8fafc; 
    color: #0284c7; 
    border: 1.5px solid #bae6fd; 
    padding: 10px 18px; 
    border-radius: 14px; 
    cursor: pointer; 
    font-size: 14px;
    font-weight: 700;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02);
  }
  .bot-btn:hover { 
    background-color: #0ea5e9;
    color: white;
    border-color: #0ea5e9;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
  }
  
  /* الشريط السفلي والأزرار العائمة */
  #start-box { 
    position: fixed; 
    bottom: 0; 
    left: 0; 
    right: 0; 
    background: rgba(255, 255, 255, 0.95); 
    backdrop-filter: blur(10px);
    padding: 15px 20px; 
    display: flex; 
    justify-content: center; 
    gap: 12px;
    box-shadow: 0 -5px 20px rgba(0,0,0,0.05);
    z-index: 100; 
    border-top: 1px solid #e2e8f0;
  }
  #start-btn, #notify-btn { 
    background: linear-gradient(90deg, #0ea5e9, #0284c7); 
    color: white; 
    border: none; 
    padding: 16px 20px; 
    border-radius: 50px; 
    font-size: 16px; 
    font-weight: 800; 
    cursor: pointer; 
    flex: 1; 
    max-width: 280px;
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.35);
    transition: all 0.2s;
  }
  #start-btn:hover, #notify-btn:hover { 
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.5);
  }
  #notify-btn { 
    background: linear-gradient(90deg, #10b981, #059669); 
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);
    display: none; 
  }
  
  /* شاشة فارغة */
  .empty-state {
    text-align: center;
    color: #64748b;
    padding: 50px 20px;
    font-size: 16px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    font-weight: 600;
  }
</style>
</head>
<body>

<header>
  <h1>💧 محطة نبع الصويرة</h1>
  <div class="subtitle">مياه شرب نقية وخدمة توصيل 24/7</div>
</header>

<div id="messages">
  <div class="empty-state">أهلاً بك في محطة نبع الصويرة، اضغط على زر البدء في الأسفل للتواصل معنا.</div>
</div>

<div id="start-box">
  <button id="notify-btn" onclick="requestNotificationPermission()">🔔 تفعيل الإشعارات</button>
  <button id="start-btn" onclick="sendStart()">🚀 ابدأ المحادثة</button>
</div>

<audio id="notification-sound" src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" preload="auto"></audio>

<script>
let lastCount = -1;
let audioEnabled = false;
let notificationsEnabled = false;

function enableAudio() {
    const audio = document.getElementById('notification-sound');
    audio.volume = 0;
    audio.play().then(() => { audio.pause(); audio.currentTime = 0; audio.volume = 1; audioEnabled = true; }).catch(e => {});
}
document.body.addEventListener('click', () => { if (!audioEnabled) enableAudio(); }, { once: true });

function requestNotificationPermission() {
    if (!("Notification" in window)) { alert("متصفحك لا يدعم الإشعارات."); return; }
    Notification.requestPermission().then(permission => {
        if (permission === "granted") {
            notificationsEnabled = true;
            document.getElementById('notify-btn').style.display = 'none';
            alert("تم تفعيل الإشعارات بنجاح!");
        }
    });
}

if ("Notification" in window && Notification.permission !== "granted") {
    document.getElementById('notify-btn').style.display = 'block';
} else if (Notification.permission === "granted") {
    notificationsEnabled = true;
}

function speakText(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ar-IQ';
    window.speechSynthesis.speak(utterance);
}

async function loadMessages() {
  try {
    const res = await fetch('/api/messages');
    const data = await res.json();
    if (data.length === lastCount) return;
    
    if (lastCount !== -1 && data.length > lastCount) {
        const lastMsg = data[data.length - 1];
        if (!lastMsg.is_me) {
            if (audioEnabled) document.getElementById('notification-sound').play().catch(e => {});
            if (notificationsEnabled) {
                new Notification("💧 محطة نبع الصويرة", { body: lastMsg.text.substring(0, 100), icon: "https://cdn-icons-png.flaticon.com/512/2965/2965272.png" });
            }
            speakText("وصلك إشعار جديد");
        }
    }

    const container = document.getElementById('messages');
    container.innerHTML = '';
    if (data.length === 0) {
        container.innerHTML = '<div class="empty-state">أهلاً بك في محطة نبع الصويرة، اضغط على زر البدء في الأسفل للتواصل معنا.</div>';
    } else {
        for (const msg of data) {
          const div = document.createElement('div');
          div.className = 'msg' + (msg.is_me ? ' me' : '');
          const date = new Date(msg.date * 1000).toLocaleTimeString('ar', {hour: '2-digit', minute:'2-digit'});
          let html = `<div class="meta">${msg.is_me ? '👤 أنت' : '💧 نبع الصويرة'} • ${date}</div>`;
          if (msg.text) html += `<div class="content">${escapeHtml(msg.text)}</div>`;
          if (msg.buttons && msg.buttons.length > 0) {
            html += `<div class="buttons-container">`;
            msg.buttons.forEach(btnText => { html += `<button class="bot-btn" onclick="clickButton(${msg.id}, '${btnText}')">${btnText}</button>`; });
            html += `</div>`;
          }
          div.innerHTML = html;
          container.appendChild(div);
        }
    }
    lastCount = data.length;
    window.scrollTo(0, document.body.scrollHeight);
  } catch (e) { console.error(e); }
}

async function sendStart() {
  if (!audioEnabled) enableAudio();
  speakText("تم بدء المحادثة");
  const btn = document.getElementById('start-btn');
  btn.innerText = 'جاري الإرسال...';
  btn.disabled = true;
  try {
    const res = await fetch('/api/send', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: '/start'}) });
    const data = await res.json();
    if (data.status === 'error') alert('فشل: ' + data.msg);
    else setTimeout(loadMessages, 500);
  } catch(e) { alert('خطأ في الاتصال'); } finally { btn.innerText = '🚀 ابدأ المحادثة'; btn.disabled = false; }
}

async function clickButton(msgId, btnText) {
  if (!audioEnabled) enableAudio();
  speakText(btnText);
  await fetch('/api/click', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({msg_id: msgId, btn_data: btnText}) });
  setTimeout(loadMessages, 1500);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
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
    if not text: return jsonify({"status": "error"}), 400
    async def send():
        if not client.is_connected(): await client.connect()
        await client.send_message(SOURCE_BOT_ID, text)
    try:
        asyncio.run_coroutine_threadsafe(send(), loop).result(timeout=15)
        messages.append({"id": int(datetime.now().timestamp()), "date": datetime.now().timestamp(), "text": f"أنت: {text}", "is_me": True, "buttons": []})
        save_messages()
        return jsonify({"status": "ok"})
    except Exception as e:
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
        asyncio.run_coroutine_threadsafe(click(), loop).result(timeout=10)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

# ================== مراقبة الرسائل والحذف التلقائي ==================
@client.on(events.NewMessage(from_users=SOURCE_BOT_ID))
async def handler(event):
    msg = event.message
    buttons = [btn.text for row in msg.buttons for btn in row if btn.text] if msg.buttons else []
    messages.append({"id": msg.id, "date": msg.date.timestamp(), "text": msg.text or msg.caption or "", "is_me": False, "buttons": buttons})
    save_messages()

@client.on(events.MessageDeleted(chats=SOURCE_BOT_ID))
async def on_message_deleted(event):
    global messages
    deleted_ids = event.deleted_ids
    messages = [msg for msg in messages if msg['id'] not in deleted_ids]
    save_messages()

async def start_client():
    try:
        await client.start()
        print("✓ Telethon is CONNECTED!")
        try: await client.get_entity(SOURCE_BOT_ID)
        except: pass
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    threading.Thread(target=lambda: loop.run_until_complete(start_client()), daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)