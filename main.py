import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Render port xətası verməsin deyə saxta server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Məlumatlar
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN") # Yeni botun tokeni

# Həm sənin hesabınla (videonu çəkmək üçün), həm də botla (cavab vermək üçün) qoşuluruq
user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("👋 Salam Murad! Mənə qorumalı kanaldan video linki at, mən də onu sənə çıxarım.")

@bot_client.on(events.NewMessage)
async def handler(event):
    if 't.me/' in event.raw_text:
        link = event.raw_text.strip()
        status = await event.respond("🔍 Link analiz edilir...")
        try:
            parts = link.split('/')
            msg_id = int(parts[-1])
            peer = int('-100' + parts[parts.index('c') + 1]) if 'c/' in link else parts[parts.index('t.me') + 1]

            # Videonu sənin adından (UserBot) tapırıq
            async with user_client:
                message = await user_client.get_messages(peer, ids=msg_id)
                if message and message.media:
                    await status.edit("⏳ Video endirilir (bu bir az vaxt ala bilər)...")
                    path = await user_client.download_media(message)
                    # Videonu Bot adından sənə göndəririk
                    await bot_client.send_file(event.chat_id, path, caption="✅ Buyur, videon hazırdır!")
                    os.remove(path)
                    await status.delete()
                else:
                    await status.edit("❌ Bu linkdə video tapılmadı.")
        except Exception as e:
            await status.edit(f"❌ Xəta baş verdi: {str(e)}")

print("🚀 Xüsusi Bot aktivdir!")
threading.Thread(target=run_health_check, daemon=True).start()
bot_client.run_until_disconnected()
