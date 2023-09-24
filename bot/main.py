import telebot
import os
import zipfile
from datetime import datetime
import get_frames
token = '6663304810:AAEo4SdocZgxtwKQjR-o_rK5wWNTJPtN1hM'
bot = telebot.TeleBot(token)
class_recog=get_frames.GetRecogniseFramesFromVideo()


delete_system=True

def get_result(downloadnamefile):
    print()
    n,timecode_list=class_recog.recognize_video(downloadnamefile)
    # timecode_list.remove(0)
    answer_csv= downloadnamefile+'.csv'
    answer_video = n+".mp4"
    return timecode_list, answer_csv, answer_video

def format_answer(name_video,timecode_list):
    s="__Результат__\n" \
           "*Название*: "+name_video+"\n" \
           "*Кол\-во ситуаций*: "+str(len(timecode_list))+"\n"
    if len(timecode_list)>0:
        s+="*Таймкоды событий*: "+str(timecode_list)+"\n"
    return s

def analysis(message,file_name, file_path,is_send_csv):
    # тут начинаем обработку, возвращаем тайм коды в list формате, на вход подаем место файла
    timecode, answer_csv, answer_video = get_result(file_path)
    # отправка ответа
    bot.send_message(
        message.chat.id,
        format_answer(file_name, timecode),
        parse_mode='MarkdownV2'
    )

    # todo для того, что csv отправлялось
    if(is_send_csv):
        bot.send_document(message.chat.id, open(answer_csv, 'rb'))
    text_timecode=""
    if(len(timecode)>0):
        text_timecode = "Таймкоды:\n"
        for i in timecode:
            text_timecode += i + "\n"
    print(answer_video)
    bot.send_video(message.chat.id, open(answer_video, 'rb'), caption=text_timecode)
    #
    if(delete_system):
        try:
            os.remove( answer_csv)
            os.remove( answer_video)
            os.remove( file_path)
        except Exception as e:
            print(e)
id_list=[]
@bot.message_handler(commands=['training'])
def start_message(message):
    if message.chat.id not in id_list:
        id_list.append(message.chat.id)
        bot.send_message(message.chat.id, "Вы включили режим дообучения, для этого вам необходимо отправить видео в формате mp4. Для выключения режима нажмите \n/training")
    else:
        id_list.remove(message.chat.id)
        bot.send_message(message.chat.id, "Вы выключили режим дообучения")

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот, разработанный командой "Ну я"\n'
                                      'Моя задача - выделение таймкодов аварийных ситуаций\n'
                                      'Для начала работы вам необходимо отправить видео в формате mp4 или архив с видео в формате mp4')

@bot.message_handler(content_types=['audio', 'photo', 'voice','animation', 'text', 'location', 'contact', 'sticker'])
def get_gif(message):
    bot.send_message(message.chat.id, 'Вы отправили некорректно файл, вам следует отправить файл как видео')

@bot.message_handler(content_types=['document'])
def get_zip(message):
    if(message.document.mime_type=='application/zip'):
        bot.send_message(message.chat.id, 'Вы отправили архив')
        bot.reply_to(message, 'Начинаю загрузку')
        now = datetime.now()

        file_name = message.document.file_name
        file_name = now.strftime("%d%m%Y%H%M%S%f")[:-3]+file_name

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("documents/"+file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.send_message(message.chat.id, 'Загрузка закончена')
        fantasy_zip = zipfile.ZipFile("documents/"+file_name)


        mp4_files=[]
        for file in fantasy_zip.namelist():
            filename, file_extension = os.path.splitext(file)
            if file_extension.lower()=='.mp4':
                mp4_files.append(file)

        if len(mp4_files)>0:
            bot.send_message(message.chat.id, 'Найдено файлов:'+str(len(mp4_files)))
            os.mkdir("documents/" + file_name[:-4])
            fantasy_zip.extractall("documents/" + file_name[:-4])
            fantasy_zip.close()
            for file in mp4_files:
                analysis(message, os.path.basename(file)[:-4], "documents/" + file_name[:-4]+"/"+file,False)

        else:
            bot.send_message(message.chat.id, 'В архиве нет файлов с расширением mp4')
        if (delete_system):
            try:
                os.remove("documents/" + file_name)
                os.remove("documents/" + file_name[:-4])
            except Exception as e:
                print(e)


    else:
        bot.send_message(message.chat.id, 'Вы отправили неправильный документ')

@bot.message_handler(content_types=['video'])
def get_video(message):
    bot.send_message(message.chat.id, 'Вы отправили видео')
    bot.reply_to(message, 'Начинаю загрузку')
    file_info = bot.get_file(message.video.file_id)
    if(message.video.mime_type=='video/mp4'):
        if(message.chat.id in id_list):
            bot.send_message(message.chat.id, 'Загрузка закончена')
            bot.send_message(message.chat.id, 'Обработка начнется в фоновом режиме в скором времени')
        else:
            downloaded_file = bot.download_file(file_info.file_path)
            with open(file_info.file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, 'Загрузка закончена')
            bot.send_message(message.chat.id, 'Начинаю обработку')

            analysis(message, message.video.file_unique_id, file_info.file_path, False)

            bot.send_message(message.chat.id, 'Окончил обработку')

    else:
        bot.send_message(message.chat.id, 'Вы отправили видео в неправильном формате')

bot.infinity_polling()
