import asyncio
import json
import os
import threading
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from supabase import create_client, Client

# ================== الإعدادات ==================
API_ID = 39932829
API_HASH = "af065af801fedce625b300cee1cc7e53"
SOURCE_BOT_ID = "@Gg5677bot"
SESSION_STRING = "1ApWapzMBu7unu6O4wHY30mW1plFpKZOSTWLTCsgJyFyjYa1UwxSTAODTNmqQNxQfaNW71TLIxHySeorVvEPr31JbtdXyTp6i4ZDcvi0hBAa5a3lQYunvw9O5mPalQieos18iCZAKL44u5pWR7v6sMOqsYiBx-C9mC9x7tRClkEQXAFHRqpc_IsaE_5bCCx5NmVNZLMJtibeIUyrzFNDiBXFO67wUTTwmomaAJ2gx8rGxIcf4SJQhzq_dfSDDFIcttffXSr5bs1g2RKBRk3AqdTp6HHXPsEp5UuVihlbryYo9tKMp9x0n3Fl4Qai1K7CWXvgKP80WpS-h5OXWLTh3qP3twyei1sU="

# قراءة المفاتيح من Render
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase Error: {e}")

# ================== واجهة HTML (تصميم محسن) ==================
HTML_CODE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>محطة نبع الصويرة 📍</title>
<style>
  body { font-family: 'Segoe UI', Tahoma, sans-serif; background-color: #f0f9ff; color: #334155; margin: 0; padding: 0; }
  header { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; text-align: center; padding: 20px; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; position: sticky; top: 0; z-index: 50; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
  h1 { margin: 0; font-size: 22px; }
  #messages { max-width: 800px; margin: 20px auto; padding: 0 15px; display: flex; flex-direction: column; gap: 15px; padding-bottom: 100px; }
  .msg { background: #ffffff; color: #1e293b; padding: 15px; border-radius: 15px 15px 15px 5px; max-width: 85%; align-self: flex-start; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
  .msg.me { background: #0ea5e9; color: #ffffff; border-radius: 15px 15px 5px 15px; align-self: flex-end; }
  .meta { font-size: 12px; color: #64748b; margin-bottom: 5px; }
  .msg.me .meta { color: #e0f2fe; }
  .content { font-size: 15px; line-height: 1.5; white-space: pre-wrap; }
  .buttons-container { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .bot-btn { background: #f1f5f9; color: #0284c7; border: 1px solid #bae6fd; padding: 10px 15px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.2s; }
  .bot-btn:hover { background: #0ea5e9; color: white; }
  #start-box { position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 15px; display: flex; justify-content: center; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); }
  #start-btn { background: #0ea5e9; color: white; border: none; padding: 15px 30px; border-radius: 30px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%; max-width: 300px; }
</style>
</head>
<body>
<header><h1>💧 محطة نبع الصويرة</h1></header>
<div id="messages"><div style="text-align:center; color:#64748b; padding:20px;">مرحباً بك، اضغط على زر البدء.</div></div>
<div id="start-box">
  <button id="start-btn" onclick="sendStart()">🚀 ابدأ المحادثة</button>
</div>

<script>
let lastCount = -1;

async function loadMessages() {
  try {
    const res = await fetch('/api/messages');
    const data = await res.json();
    if (data.length === lastCount) return;
    const container = document.getElementById('messages');
    container.innerHTML = '';
    if (data.length === 0) {
        container.innerHTML = '<div style="text-align:center; color:#64748b; padding:20px;">مرحباً بك، اضغط على زر البدء.</div>';
    } else {
        for (const msg of data) {
          const div = document.createElement('div');
          div.className = 'msg' + (msg.is_me ? ' me' : '');
          let html = `<div class="meta">${msg.is_me ? '👤 أنت' : '💧 البوت'}</div>`;
          if (msg.text) html += `<div class="content">${escapeHtml(msg.text)}</div>`;
          
          // عرض الأزرار إذا كانت موجودة
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
    }
    lastCount = data.length;
    window.scrollTo(0, document.body.scrollHeight);
  } catch (e) { console.error(e); }
}

async function sendStart() {
  const btn = document.getElementById('start-btn');
  btn.innerText = 'جاري الإرسال...';
  btn.disabled = true;
  try {
    const res = await fetch('/api/send', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: '/start'}) });
    const data = await res.json();
    if (data.status === 'error') alert('فشل: ' + data.msg);
    else setTimeout(loadMessages, 1000);
  } catch(e) { alert('خطأ في الاتصال'); } finally { btn.innerText = '🚀 ابدأ المحادثة'; btn.disabled = false; }
}

async function clickButton(msgId, btnText) {
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

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/api/messages')
def get_messages():
    if supabase is None: return jsonify([])
    try:
        response = supabase.table('messages').select('*').order('date', desc=False).execute()
        # تأكد من أن الأزرار تُرجع كمصفوفة وليس كنص
        for msg in response.data:
            if isinstance(msg.get('buttons'), str):
                try:
                    msg['buttons'] = json.loads(msg['buttons'])
                except:
                    msg['buttons'] = []
        return jsonify(response.data)
    except Exception as e:
        print(f"Fetch Error: {e}")
        return jsonify([])

@app.route('/api/send', methods=['POST'])
def send_message():
    text = request.json.get('text', '')
    if not text: return jsonify({"status": "error", "msg": "الرسالة فارغة"}), 400
    try:
        future = asyncio.run_coroutine_threadsafe(client.send_message(SOURCE_BOT_ID, text), loop)
        future.result(timeout=15)
        
        if supabase:
            new_msg = {"id": int(datetime.now().timestamp() * 1000), "date": datetime.now().timestamp(), "text": f"أنت: {text}", "is_me": True, "buttons": []}
            supabase.table('messages').insert(new_msg).execute()
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Send Error: {e}") 
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/api/click', methods=['POST'])
def click_button():
    data = request.json
    async def click():
        # استعادة الآيدي الأصلي (نقسم على 1000 لأننا ضربناه في الملي ثانية)
        original_id = int(data.get('msg_id') / 1000) if data.get('msg_id') > 1000000000000 else int(data.get('msg_id'))
        msg = await client.get_messages(SOURCE_BOT_ID, ids=original_id)
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
    if supabase:
        try:
            new_msg = {
                "id": msg.id, 
                "date": msg.date.timestamp(), 
                "text": msg.text or msg.caption or "", 
                "is_me": False, 
                "buttons": buttons # سيتم حفظها كمصفوفة JSON
            }
            supabase.table('messages').insert(new_msg).execute()
        except Exception as e:
            print(f"DB Error: {e}")

if __name__ == '__main__':
    async def start_telethon():
        await client.start()
        print("✓ Telethon is CONNECTED!")
        await client.run_until_disconnected()
    
    threading.Thread(target=lambda: loop.run_until_complete(start_telethon()), daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)