import telebot
import os
import re
import time
import pytz

from datetime import datetime
from dotenv import load_dotenv
from database.mongodb import get_db
from func.youtube.youtube_api import *
from telebot.types import LinkPreviewOptions, InlineKeyboardButton, InlineKeyboardMarkup
load_dotenv()

#Importamos los datos necesarios para el bot
Token = os.getenv('BOT_API')
bot = telebot.TeleBot(Token)

# Conectar a la base de datos
db = get_db()
youtube = db.youtube

#Get YT API info
youtube_client = authenticate()
channel_id = "UCftYv-uM9iItUY4eJp2zerg"

def convert_duration_iso(duracion_iso):
    # Extraer los minutos y segundos con expresiones regulares
    min = re.search(r'(\d+)M', duracion_iso)
    sec = re.search(r'(\d+)S', duracion_iso)

    # Convertir a enteros y formatear como "MM:SS"
    min = int(min.group(1)) if min else 0
    sec = int(sec.group(1)) if sec else 0

    return f"{min:02d}:{sec:02d}"

def convert_date(fecha_iso):
    fecha_obj = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
    zona_cuba = pytz.timezone('America/Havana')
    fecha_cuba = fecha_obj.astimezone(zona_cuba)

    fecha_formateada = fecha_cuba.strftime('%m/%d/%y %I:%M %p')

    return fecha_formateada

def get_yt_videos(message, task=False):
    if message is not None:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if chat_id != -1001485529816 and task is False:
            bot.reply_to(message, "Este comando es exclusivo de Otaku Senpai.")
            return
        
        chat_member = bot.get_chat_member(chat_id, user_id)
    
        if chat_member.status not in ['administrator', 'creator'] and task is False:
            bot.reply_to(message, "Solo los administradores pueden usar este comando.")
            return
    
    print("Buscando Videos...")
    videos = get_latest_videos(youtube_client, channel_id)
    print("Busqueda Finalizada.")
    for video in videos:
        vid_id = None
        print(video['IDVideo'])
        vid_id = youtube.find_one({'_id': video['IDVideo']})

        if vid_id is not None:
            continue
        try:
            youtube.insert_one({'_id': video['IDVideo']})
        except Exception as e:
            print("Error al insertar video: ", e)
            continue

        link_preview_options = LinkPreviewOptions(url=video["Thumbnails"]["high"]["url"], prefer_large_media=True, show_above_text=True)

        msg = f"""
Titulo: <strong>{video["Title"]}</strong>

Descripción: <strong>{video["Description"]}</strong>

Fecha: <strong>{convert_date(video["Published At"])}</strong>
Definición: <strong>{video["Content Details"]["definition"].upper()}</strong> | Duración: <strong>{convert_duration_iso(video["Content Details"]["duration"])}</strong>
"""
        reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "📺 Ir a ver",
                                    url=f"https://www.youtube.com/watch?v={video['IDVideo']}"
                                )
                            ]
                        ]
                    )
        
        bot.send_message(-1001485529816, msg, message_thread_id=251766, link_preview_options=link_preview_options, parse_mode="html", reply_markup=reply_markup)
        time.sleep(3)
