from database.mongodb import get_db
from telebot.apihelper import ApiTelegramException
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
db = get_db()
users = db.users
contest = db.contest
Contest_Data = db.contest_data

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)


def add_user(user_id):
    # Consulta para seleccionar el documento a actualizar
    filter = {'contest_num': 2}

    # Operación de actualización para agregar dos usuarios más a la lista 'completed_by'
    update = {'$push': {'subscription': {'user': user_id}}}

    # Actualizar el documento en la colección 'tasks'
    result = contest.update_one(filter, update)

    return result

def del_user(user_id):
    # Consulta para seleccionar el documento a actualizar
    filter = {'contest_num': 2}

    # Operación de actualización para agregar dos usuarios más a la lista 'completed_by'
    update = {'$pull': {'subscription': {'user': user_id}}}

    # Actualizar el documento en la colección 'tasks'
    result = contest.update_one(filter, update)

    return result

def reg_user(user_id, username):
    users.insert_one({"user_id": user_id, "username": username})

def send_data_contest(JUECES, text, markup, img=None):
    for item in JUECES:
        try:
            if img:
                bot.send_photo(item, img, text, parse_mode="html", reply_markup=markup)
            else:
                bot.send_message(item, text, parse_mode="html", reply_markup=markup)
        except ApiTelegramException as err:
            print(f"{err}, {item}")

def subscribe_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    found = False

    chat_member = bot.get_chat_member(-1001485529816, user_id)

    if chat_member is None:
        bot.send_message(chat_id, f"Solo los participantes de <a href='https://t.me/OtakuSenpai2020'>Otaku Senpai</a> pueden participar en el concurso.", parse_mode="html")
        return

    if username is None:
        bot.send_message(chat_id, f"Lo siento, no te puedes subscribir al concurso sin un nombre de usuario")
        return
    
    user = users.find_one({'user_id': user_id})
    if user:
        pass
    else:
        reg_user(user_id, username)

    contest_list = contest.find({'contest_num': 2})

    for user in contest_list:
            for sub in user['subscription']:
                if sub['user'] == user_id:
                    found = True
                    break
                
            if found:
                bot.send_message(chat_id, f"Oh! Ya estabas registrado en el concurso.")
                break
            
            if not found:
                add_user(user_id)
                bot.send_message(chat_id, f'Bien acabo de registrarte en el concurso @{username}. Para desuscribirte en cualquier momento usa el comando /unsub')


def unsubscribe_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    found = False
    
    user = users.find_one({'user_id': user_id})
    content_photo = Contest_Data.find_one({'u_id': user_id, 'type': 'photo'})
    content_text = Contest_Data.find_one({'u_id': user_id, 'type': 'text'})

    for user in contest.find({'contest_num': 2}):
            for sub in user['subscription']:
                if sub['user'] == user_id:
                    found = True
                    break

            if not found:
                bot.send_message(chat_id, f'No estás registrado en el concurso')
                return
            
            del_user(user_id)
            bot.send_message(chat_id, f"Bien te has desuscrito del concurso.")

            if content_photo:
                Contest_Data.delete_one({'u_id': user_id, 'type': 'photo'})
                os.remove(f"./func/concurso/{user_id}.jpg")

            if content_text:
                Contest_Data.delete_one({'u_id': user_id, 'type': 'text'})
            
            bot.send_message(chat_id, f"Se han eliminado tus datos de concurso.")
            break
