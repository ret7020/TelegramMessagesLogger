import os
import logging
from aiogram import Bot, Dispatcher, types
import asyncio
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import Base, Messages
from utils import organize_history

bot_token = os.getenv("TOKEN")
logging.basicConfig(level=logging.INFO)



# Init db
engine = create_engine('sqlite:///messages.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Aiogram
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_chat_members(message: types.Message):
    for user in message.new_chat_members:
        if user.id == bot.id:
            chat_id = message.chat.id
            await bot.send_message(chat_id, 'Спасибо, что добавили меня в эту группу. Теперь я буду её мониторить и сообщать, если кто - то удалит или отредактирует сообщение!')
            break

# @dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
# async def left_chat_member_handler(message: types.Message):
#     if message.left_chat_member.id == bot.id:
#         chat_id = message.chat.id
#         logging.info(f"Bot was deleted from group {chat_id}")

@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def someNewMessage(message: types.Message):
    msg_db = Messages(message_id=message.message_id, chat_id=message.chat.id, event_id=0, text=message.text)
    session.add(msg_db)
    session.commit()

@dp.edited_message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def handle_edit_message(message: types.Message):
    msg_db = Messages(message_id=message.message_id, chat_id=message.chat.id, event_id=1, text=message.text)
    session.add(msg_db)
    session.commit()
    nickname = message.from_user.username
    if not nickname: nickname = f"{message.from_user.first_name} {message.from_user.last_name}"
    query = select(Messages).where(Messages.chat_id == message.chat.id, Messages.message_id == message.message_id)
    results = session.execute(query).fetchall()
    history = organize_history(results)
    await bot.send_message(chat_id=message.chat.id, 
                           text=f"@{nickname} изменил сообщение!\nВсе события над сообщением (от создания к текущему): \n{history}", 
                           reply_to_message_id=message.message_id, parse_mode=types.ParseMode.HTML)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())