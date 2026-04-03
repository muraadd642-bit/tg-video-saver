import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Render-in sönməməsi üçün saxta veb-server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Məlumatlar (Render-dən oxunacaq)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# İki fərqli klient yaradırıq
user_client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

async def start_clients():
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    print("🚀 Murad, botun artıq işə düşdü!")

@bot_client.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    await event.respond("👋 Salam Murad! Mənə qorumalı kanaldan video linki at, mən də onu çıxarıb sənə göndərim.")

@bot_client.on(events.NewMessage)
async def link_handler(event):
    if 't.me/' in event.raw_text:
        link = event.raw_text.strip()
        status = await event.respond("🔍 Link analiz edilir...")
        try:
            parts = link.split('/')
            msg_id = int(parts[-1])
            peer = int('-100' + parts[parts.index('c') + 1]) if 'c/' in link else parts[parts.index('t.me') + 1]

            async with user_client:
                message = await user_client.get_messages(peer, ids=msg_id)
                if message and message.media:
                    await status.edit("⏳ Video endirilir...")
                    path = await user_client.download_media(message)
                    await bot_client.send_file(event.chat_id, path, caption="✅ Hazırdır!")
                    os.remove(path)
                    await status.delete()
                else:
                    await status.edit("❌ Video tapılmadı.")
        except Exception as e:
            await status.edit(f"❌ Xəta: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_health_check, daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_clients())
    bot_client.run_until_disconnected()
