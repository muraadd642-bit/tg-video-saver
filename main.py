import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Render-in "Port" xətası verməməsi üçün kiçik bir saxta server
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# Bot Məlumatları
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if 't.me/' in event.raw_text:
            link = event.raw_text.strip()
            status = await event.respond("🔍 Link analiz edilir...")
            try:
                parts = link.split('/')
                msg_id = int(parts[-1])
                peer = int('-100' + parts[parts.index('c') + 1]) if 'c/' in link else parts[parts.index('t.me') + 1]

                message = await client.get_messages(peer, ids=msg_id)
                if message and message.media:
                    await status.edit("⏳ Video endirilir...")
                    path = await client.download_media(message)
                    await client.send_file(event.chat_id, path, caption="✅ Video çıxarıldı!")
                    os.remove(path)
                    await status.delete()
                else:
                    await status.edit("❌ Video tapılmadı.")
            except Exception as e:
                await status.edit(f"❌ Xəta: {str(e)}")

    print("🚀 Bot aktivdir!")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Render üçün saxta serveri arxa planda başlat
    threading.Thread(target=run_health_check, daemon=True).start()
    # Botu başlat
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
