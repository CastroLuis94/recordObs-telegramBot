from telegram.ext import Updater, CommandHandler
import pandas as pd
import subprocess
import glob
import os
import time
from jinja2 import Template
import imgkit
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
BASE_PATH = os.path.dirname(os.path.realpath(__name__))
###########################User Data###########################################

## Se tiene que crear un archivo data_user.txt donde en el primer renglon tenga
## el id del usuario y despues el token del bot que te proporciono telegram.
with open("data_user.txt", "r") as file:
    chat_id, bot_token = file.readline().split()

## Aca tomo el path que va a tener la imagen, por default es /home/user/imagen.png
## si se quiere cambiar el directorio/nombre se cambia la linea de abajo
imagen_path = os.environ['HOME'] + "/imagen.png"
try:
    data_user = pd.read_csv("meetings_user.csv", index_col=0)
except:
    data_user = pd.DataFrame(columns=['sala','password']) 
zoom = 'zoom "--url=zoommtg://zoom.us/join?action=join&confno={0}&pwd={1}" &'

#############################################################################
def start(bot, update):
    update.message.reply_text(
        'Hola ' + update.message.from_user.first_name + '''.\n Use el comando /help para mas informacion.        
        ''')


def help(bot, update):
    update.message.reply_text(
    """Este es un bot para uso personal, si quieren saber mas sobre este bot puede comunicarse con @Castroluis94.
    Los comandos disponibles son:
    /start_record : Activa obs y se pone a grabar segun su configuracion, le da a la computadora 3 segundos para abrir el programa y saca un screen para reenviarsela al usuario.(Puede que si la computadora es lenta necesite mas tiempo, usar el comando de abajo para ver el estado actual de la compu, activar otra vez este comando podria abrir un obs extra)
    /send_screenshot : Devuelve una screen de la computadora en el momento actual. No se necesita haber activado start_record para ejecutalo.
    """
)

def start_record(bot, update):
    if str(update.message.chat.id) == chat_id:
        subprocess.run("obs --startrecording &" ,shell=True)
        time.sleep(3)
        send_screenshot(bot, update)
    else:
        update.message.reply_text("Este es un bot para uso personal. Vos no sos mi dueño")


def send_screenshot(bot, update):
    if str(update.message.chat.id) == chat_id:
        subprocess.run("gnome-screenshot -f {0}".format(imagen_path) ,shell=True)
        bot.send_photo(chat_id, photo=open(imagen_path, 'rb'))
        os.remove(imagen_path)
    else:
        update.message.reply_text("Este es un bot para uso personal. Vos no sos mi dueño")

def list_meetings(bot, update):
    message = "Sus meetings son:\n"
    for index in data_user.index:
        message += index + "\n"
    update.message.reply_text(message)

def delete_meeting(bot, update):
    separetor = " "
    meeting = separetor.join(update.message.text.split()[1:])
    data_user.drop([meeting], inplace=True)
    zoom_card(data_user)

    
    

def meetings(bot, update):
    if data_user.index.empty:
        update.message.reply_text("Actualmente no tiene meetings")
        return
    id = update.message.chat.id
    card_path = BASE_PATH + "/user_card.png"
    zoom_card(data_user)
    bot.send_photo(id, photo=open(card_path, 'rb'))

def active_zoom(bot, update):
    separetor = " "
    meeting = separetor.join(update.message.text.split()[1:])
    sala = data_user.loc[meeting]['sala']
    password = data_user.loc[meeting]['password']
    zoom_meeting = zoom.format(sala, password)
    subprocess.run(zoom, shell=True)


def add_meeting(bot, update):
    password = update.message.text.split()[-1]
    sala = update.message.text.split()[-2]
    separetor = " "
    meetings = separetor.join(update.message.text.split()[1:-2])
    data_user.loc[meetings] = [sala, password]
    update.message.reply_text("La nueva meeting fue agregada")


def save_meeting(bot, update):
    data_user.to_csv("meetings_user.csv")
    


def zoom_card(data_user):
    with open(os.path.join(BASE_PATH,'meetings_user.html'), 'r') as f:
        template = Template(f.read())
    css = os.path.join(BASE_PATH, 'card.css')
    options = {
             'crop-w': 615,
             'crop-x': 200
        }
    img = imgkit.from_string(template.render(data_user=data_user, BASE_PATH=BASE_PATH), "user_card.png", options=options, css=css)    
    

if __name__ == "__main__":

    updater = Updater(bot_token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('start_record', start_record))
    updater.dispatcher.add_handler(CommandHandler('send_screenshot', send_screenshot))
    updater.dispatcher.add_handler(CommandHandler('list_meetings', list_meetings))
    updater.dispatcher.add_handler(CommandHandler('meetings', meetings))
    updater.dispatcher.add_handler(CommandHandler('active_zoom', active_zoom))
    updater.dispatcher.add_handler(CommandHandler('add_meeting', add_meeting))
    updater.dispatcher.add_handler(CommandHandler('delete_meeting', delete_meeting))
    updater.dispatcher.add_handler(CommandHandler('save_meeting', save_meeting))
    updater.start_polling()
    updater.idle()

    
    