from models import Messages

def organize_history(messages: Messages):
    EVENTS_MAP = ["Отправлено", "<i>Изменено</i>", "<b>Удалено</b>"] # 0 1 2
    return "\n".join([f"{EVENTS_MAP[message[0].event_id]}: {message[0].text}" for message in messages])