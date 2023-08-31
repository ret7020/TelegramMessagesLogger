from telethon import TelegramClient, events
import os
import asyncio
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import Base, Messages
from utils import organize_history
import logging

CHATS = [-987221179]


# Init db
engine = create_engine('sqlite:///messages.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
LOG = os.getenv("API_HASH")
CURRENT_USER_ID = None
client = TelegramClient('logger', API_ID, API_HASH)



@client.on(events.NewMessage(chats=CHATS))
async def new_message_handler(event):
    msg_db = Messages(message_id=event.message.id, chat_id=event.message.peer_id.chat_id, event_id=0, text=event.message.message)
    session.add(msg_db)
    session.commit()

@client.on(events.MessageEdited(chats=CHATS))
async def edit_message_handler(event):
    msg_db = Messages(message_id=event.message.id, chat_id=event.message.peer_id.chat_id, event_id=1, text=event.message.message)
    session.add(msg_db)
    session.commit()

@client.on(events.MessageDeleted)
async def delete_message_handler(event):
    for msg_id in event.deleted_ids:
        query = select(Messages).where(Messages.message_id == msg_id)
        results = session.execute(query)
        results = results.scalar_one_or_none()
        if results: # If message logged before, otherwise no need to log it, because we can't get it's original text
            msg_db = Messages(message_id=msg_id, chat_id=results.chat_id, event_id=2)
            session.add(msg_db)
    session.commit()
    


client.start()
loop = asyncio.get_event_loop()
coroutine = client.get_me()
result = loop.run_until_complete(coroutine)
print(result.id)

client.run_until_disconnected()