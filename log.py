from telethon import TelegramClient, events
from config import *
import sqlite3
import json
import datetime
import logging


def save_message(chat_id, message_id, text):
    data = (chat_id, message_id, json.dumps([text], ensure_ascii=False), json.dumps([str(datetime.datetime.now())]), 0)
    cursor.execute("INSERT INTO `messages` (`chat_id`, `message_id`, `texts`, `events_times`, `deleted`) VALUES (?, ?, ?, ?, ?)", data) 
    sqlite_connection.commit()
 
logging.basicConfig(level=logging.INFO)

sqlite_connection = sqlite3.connect('db')
cursor = sqlite_connection.cursor()
client = TelegramClient('logger', API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHATS))
async def new_message_handler(event):
    save_message(event.message.peer_id.channel_id, event.message.id, event.raw_text)
    
@client.on(events.MessageDeleted(chats=CHATS))
async def delete_message_handler(event):
    logging.info("Delete message")
    # event.original_update.channel_id
    for message_id in event.deleted_ids:
        cursor.execute("UPDATE `messages` SET `deleted` = 1 WHERE `chat_id` = ? AND `message_id` = ?", (event.original_update.channel_id, message_id))
    sqlite_connection.commit()    

@client.on(events.MessageEdited(chats=CHATS))
async def edit_messages_handler(event):
    logging.info("Edit message")
    print(event.message.id, event.message.peer_id.channel_id)
    print(event.raw_text)
    logged_message = cursor.execute("SELECT `texts`, `events_times` FROM `messages` WHERE `chat_id` = ? AND `message_id` = ?", (event.message.peer_id.channel_id, event.message.id)).fetchall()
    if logged_message:
        logged_texts, logged_times = json.loads(logged_message[0][0]), json.loads(logged_message[0][1])
        logged_texts.append(event.raw_text)
        logged_times.append(str(datetime.datetime.now()))
        logged_texts, logged_times = json.dumps(logged_texts, ensure_ascii=False), json.dumps(logged_times)
        cursor.execute("UPDATE `messages` SET texts = ?, events_times = ? WHERE `chat_id` = ? AND `message_id` = ?", (logged_texts, logged_times, event.message.peer_id.channel_id, event.message.id))
        sqlite_connection.commit()
    else: # Message not logged later; so add this message to db
        save_message(event.message.peer_id.channel_id, event.message.id, event.raw_text)

client.start()
client.run_until_disconnected()
logging.info("Disconnecting from db")
cursor.close()
sqlite_connection.close()

