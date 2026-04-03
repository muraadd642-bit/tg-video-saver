import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Koyeb-dən gələcək məlumatlar
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if 't.me/' in event.raw_text:
        link = event.raw_text.strip()
        status = await event.respond("🔍 Link analiz edilir...")
        try:
            parts = link.split('/')
            msg_id = int(parts[-1])
            if 'c/' in link:
                peer = int('-100' + parts[parts.index('c') + 1])
            else:
                peer = parts[parts.index('t.me') + 1]

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

print("🚀 Bot Koyeb-də aktivdir!")
client.start()
client.run_until_disconnected()
