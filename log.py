from telethon import TelegramClient, events
from config import *
import sqlite3
import json
import datetime

sqlite_connection = sqlite3.connect('db')
cursor = sqlite_connection.cursor()
client = TelegramClient('logger', API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHATS))
async def new_message_handler(event):
    print("New message")
    print(event.raw_text, event.message.id, event.message.peer_id.channel_id)
    data = (event.message.peer_id.channel_id, event.message.id, json.dumps([event.raw_text], ensure_ascii=False), json.dumps([str(datetime.datetime.now())]), 0)
    print(data)
    cursor.execute("INSERT INTO `messages` (`chat_id`, `message_id`, `texts`, `events_times`, `deleted`) VALUES (?, ?, ?, ?, ?)", data) 
    sqlite_connection.commit()

@client.on(events.MessageDeleted(chats=CHATS))
async def delete_message_handler(event):
    print("Messages deleted")
    print(event.deleted_ids)
    

client.start()
client.run_until_disconnected()
cursor.close()
sqlite_connection.close()

