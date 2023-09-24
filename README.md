# nu-ya-cifrovoj-proryv-
## Разворачивание TG бота
* Устанавливаем python 3.10 [тык](https://www.python.org/downloads/release/python-3100/)
* Скачиваем архив c исходниками бота [тык](https://drive.google.com/drive/folders/10pw8xV2ASFfkPPEsBj-bNKNv5sAe4T1W?usp=sharing)
* Разархивируем архив TGbot.7z
* При помощи команды _pip install -r requirements.txt_ устанавливаем необходимые зависимости
* Запускаем _main.py_
* Бот доступен по ссылке [тык](https://t.me/nu_ya_cifrovoj_proryv_bot)
## Использование разработанного решения
* Устанавливаем python 3.10 [тык](https://www.python.org/downloads/release/python-3100/)
* Устанавливаем ultralytics ( _pip install ultralytics_ )
* Устанавливаем opencv-python ( _pip install opencv-python_ )
* Скачиваем обученные модели [тык](https://drive.google.com/drive/folders/1TZuoVOinBHF468ofhk3PqjIbcrBhamoH?usp=sharing)
* Скачиваем разработанное решение [тык](https://drive.google.com/drive/folders/1-QPu45mKhuJeMQKeQCoJLT4nPq9aHoKR?usp=sharing)

Для работы с решением достаточно выполнить импорт, инициализацию класса и передать путь к видео
 ```
import get_frames
f= get_frames.GetRecogniseFramesFromVideo()
f.recognize_video("test_vid.mp4")
```
