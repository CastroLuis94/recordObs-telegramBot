from telegram.ext import Updater, CommandHandler
import pandas as pd
import subprocess
import glob
import os
import time
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

###########################User Data###########################################

## Se tiene que crear un archivo data_user.txt donde en el primer renglon tenga
## el id del usuario y despues el token del bot que te proporciono telegram.
with open("data_user.txt", "r") as file:
    chat_id, bot_token = file.readline().split()

## Aca tomo el path que va a tener la imagen, por default es /home/user/imagen.png
## si se quiere cambiar el directorio/nombre se cambia la linea de abajo
imagen_path = os.environ['HOME'] + "/imagen.png"
data_user = pd.read_csv("meetings_user.csv", index_col=0)
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

def meetings(bot, update):
    tabla = str(data_user)
    update.message.reply_text("meeting" + tabla)
    
if __name__ == "__main__":
    updater = Updater(bot_token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('start_record', start_record))
    updater.dispatcher.add_handler(CommandHandler('send_screenshot', send_screenshot))
    updater.dispatcher.add_handler(CommandHandler('meetings', meetings))

    updater.start_polling()
    updater.idle()