import telebot
import os
import re
from transliterate import translit
import requests as req
import io
import random
import json
# import replicate
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models.gigachat import GigaChat
import time
import base64
import assemblyai as aai
import uuid
import time


debug_mode = True
# debug_mode = False

stickers = {'🤯': 'CAACAgIAAxkBAAIGs2XTdEp0pMQTFZsFL_tJcwABOS8b0AACXxQAAjdUcEh-DciF_xezMjQE', 
            '🙂': 'CAACAgIAAxkBAAIGtWXTdKg0hH4R2SDvCiGNsQQQr0vLAALkNwAC93gAAUsBmw-khStzwzQE', 
            '🐱': 'CAACAgIAAxkBAAIGsWXTc--yWuFCYxJ7PtCUOlX_B7wQAAI3NQACyV4AAUtjRMMVvbBaFzQE', 
            '😲': 'CAACAgIAAxkBAAIGt2XTdV2QGgdeqVSMKU9tFQmvLTHtAALwFQACyjPZS806D2QrLIi2NAQ', 
            '❌': 'CAACAgIAAxkBAAIGuWXTdbaQr-yTtlRUReLjWqwYZ-B_AAIzJAACR_6JSYBmOsh87kjMNAQ', 
            '😂': 'CAACAgIAAxkBAAIHeGXTgEDquQI_sLFJYRzx8sUpLHiZAAIVNQACvDioSVYgKVZSyIcKNAQ', 
            '😎': 'CAACAgIAAxkBAAIHRmXTfcMbPcn1CTNve5oNsN7ObI5rAALDIwAC6QQ5S_N1x_hwppm0NAQ', 
            '🙁': 'CAACAgIAAxkBAAIHSGXTfcuugtyWvmdFomiu4dYmL863AAIHKQAC8ZkZS3nzxoiuGWfXNAQ', 
            '😉': 'CAACAgIAAxkBAAIHXmXTftl-sWe6_nY5yAozIgmXznp2AAL8GgAC2pmJSmdY8XkC7nDjNAQ', 
            '🤤': 'CAACAgIAAxkBAAIHTGXTfdUHJ1OUG6uUu9nSA055mi5UAAJNJgACyIY4S4nnfDVZiza7NAQ', 
            '😭': 'CAACAgIAAxkBAAIHTmXTfd0KVL2gRGtk0kgsLgIYOQiNAAK0KQACx1M4S4lKuQe97uhFNAQ', 
            '🔫': 'CAACAgIAAxkBAAIHUGXTfeLRkC2-fVDzzdgAAUBF9ceVZQAClhQAAt5DWElV3yoWdA-F_zQE', 
            '😈': 'CAACAgIAAxkBAAIHUmXTfeWU8sGJDU24wxQ0wux5sqoNAAKPGwAC1E_ASotmK4PwS_6JNAQ', 
            '🌟': 'CAACAgIAAxkBAAIHWGXTffCwum270lCVWX2lQWrprdENAAJhLgACCU94SyEQXPXZwcJ4NAQ', 
            '😊': 'CAACAgIAAxkBAAIHZGXTfwWkz_62Zl_gi6GPOW1ElLCNAALyGwACileRSh6BOqw6T2AeNAQ', 
            '👍': 'CAACAgIAAxkBAAIHfmXTgIj1GjnpmQSWXQEGUoAT2NcOAAJyHAACXpsAAUtRuOMtRG0DlzQE', 
            '🍻': 'CAACAgIAAxkBAAIHj2XUPV61zHy4PJv9zGeQAT6NEyHAAAKLEAAC66voSX8-twG8foEcNAQ', 
            '😮': 'CAACAgIAAxkBAAIHk2XUPXeOPblydPccp9A6EWqF-jkNAAJFEgAC8E7pScHu7vQ3QuIsNAQ', 
            '😍': 'CAACAgIAAxkBAAIHn2XUu5YmMeHZO7Vijj-mA40ViFMHAALxAAMENMs86QRv2vPAzP00BA', 
            '😄': 'CAACAgIAAxkBAAIISGXXPgcKgd1aptY1Eh3jO3kcctYAAwMaAAIezLFKLw1RSCOuzl80BA', 
            '😸': 'CAACAgIAAxkBAAIIjGXXnfQAAfqwgrYuYU8VD_7qh6ZFewACMRgAAhpGUUioKe3ZOLnMTzQE'}

aai.settings.api_key = "0d29d635244147a59c83524b47ddb44c"
transcriber = aai.Transcriber()

os.environ.setdefault('REPLICATE_API_TOKEN', 'r8_K9Ca3DfllpqsDCDnpsxO7eEfXyqvp3e2M1pvH')
# 8FC9E9039795BF010A3AB197358D375C
# AD5800E17B8450C66CE404803C25A6FC

class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = req.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = req.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = req.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

def gen(prom):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '8FC9E9039795BF010A3AB197358D375C', 'AD5800E17B8450C66CE404803C25A6FC')
    model_id = api.get_model()
    uuid = api.generate(prom, model_id)
    images = api.check_generation(uuid)    

    # Здесь image_base64 - это строка с данными изображения в формате base64
    image_base64 = images[0]

    # Декодируем строку base64 в бинарные данные
    image_data = base64.b64decode(image_base64)
    return image_data

# api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '8FC9E9039795BF010A3AB197358D375C', 'AD5800E17B8450C66CE404803C25A6FC')
# model_id = api.get_model()
# uuid = api.generate("Sun in sky", model_id)
# images = api.check_generation(uuid)

# Яндекс
# folder
# b1g3uste2djiuces45cu 
# t1.9euelZqcx8-bmpDPj43MmJrLnpzGiu3rnpWazY7KmZCPzMvGyMyenJGSyMjl8_cWdiJR-e9lKWxw_d3z91YkIFH572UpbHD9zef1656VmouZk4-Ri5CXkZ2RksmKzI3O7_zF656VmouZk4-Ri5CXkZ2RksmKzI3O.U-8fOpAesS4WKwlaHfmufC7FFyM0ZUH5NljTJEkufyTnKhhdYn17sMGILMWVEfvnYBtz4RhzaOtNQbn-QoNJAw
bot = telebot.TeleBot("6365480968:AAHLyOpHK45Sr9vzNvrl56q83z-HxZ1tICk")
# 11ae50e2-e07f-4c0b-9250-2f7103a028f3
# MzRiZWIyNGUtN2E0ZC00NDU5LTliNTAtYjU3NGE3MzFhODBlOjg2YjA2ZDk0LWZlOWUtNGY1Mi05ODg5LTA5ZmRmYWFhMGEwNA==
# chat = GigaChat(credentials="MzRiZWIyNGUtN2E0ZC00NDU5LTliNTAtYjU3NGE3MzFhODBlOjg2YjA2ZDk0LWZlOWUtNGY1Mi05ODg5LTA5ZmRmYWFhMGEwNA==", 
#     verify_ssl_certs=False)
# messages_chatgig = [
#     SystemMessage(
#         content="""Ты бот, который сидит в коментариях телеграмм канала, не соглашается с людьми и всегда говорит противоположные вещи. 
#         Например, ты обязан на 'Привет' ответить 'Пока', 
#         на утверждение, что земля имеет форму шара, ты должен ответить, что она плоская и т.д. 
#         Твое имя Саркастико. Иногда ты присылаешь простые эмодзи без сопровождающего текста. Даже точку в конце не ставишь.
#         Приходящие тебе сообщения имеют такую структуру: <Имя_пользователя>: <Сообщение_пользователя>.
#         Структура твоих ответов: <Твоё_сообщение>.
#         ЗАПРЕЩЕНО использовать структуру, как у пользователя. Твой ответ ОБЯЗАН содержать только сообщение!
#         Когда у тебя спрашивают погоду, ты должен сгенерировать только специальный json: {"function":"weather", "city":str}, где city — локация/город/населённый пункт, получаемый из сообщения пользователя.
#         Старайся обращаться к пользователям по имени. Например: Привет, <Имя_пользователя>! Пока, <Имя_пользователя>! Как дела, <Имя_пользователя>?
#         """
#     )
# ]


def get_token(RqUID):
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    payload='scope=GIGACHAT_API_PERS'
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
      'RqUID': str(RqUID),
      'Authorization': 'Basic MzRiZWIyNGUtN2E0ZC00NDU5LTliNTAtYjU3NGE3MzFhODBlOjg2YjA2ZDk0LWZlOWUtNGY1Mi05ODg5LTA5ZmRmYWFhMGEwNA=='
    }
    response = req.request("POST", url, headers=headers, data=payload, verify=False)
    return response


def chat(access_token, messages, repetition_penalty=1, max_tokens=1024, n=1, top_p=0.1, temperature=0.1):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload = json.dumps({
      "model": "GigaChat:latest",
      "messages": messages,
      "temperature": temperature,
      "top_p": top_p,
      "n": n,
      "stream": False,
      "max_tokens": max_tokens,
      "repetition_penalty": repetition_penalty
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Bearer ' + access_token
    }
    response = req.request("POST", url, headers=headers, data=payload, verify=False)
    return json.loads(response.text)

x = uuid.uuid4()

get_t = json.loads(get_token(x).content)
messages_gig = [{
    "role": "system",
    "content": """Ты бот, который сидит в коментариях телеграмм канала, не соглашается с людьми и всегда говорит противоположные вещи. 
        Например, ты обязан на 'Привет' ответить 'Пока', 
        на утверждение, что земля имеет форму шара, ты должен ответить, что она плоская и т.д. 
        Твое имя Саркастико. Иногда ты присылаешь простые эмодзи без сопровождающего текста. Даже точку в конце не ставишь.
        Приходящие тебе сообщения имеют такую структуру: <Имя_пользователя>: <Сообщение_пользователя>.
        Структура твоих ответов: <Твоё_сообщение>.
        ЗАПРЕЩЕНО использовать структуру, как у пользователя. Твой ответ ОБЯЗАН содержать только сообщение!
        Когда у тебя спрашивают погоду, ты ОБЯЗАН сгенерировать только специальный json: {"function":"weather", "city":str}, где city — локация/город/населённый пункт, получаемый из сообщения пользователя.
        Старайся обращаться к пользователям по имени. Например: Привет, <Имя_пользователя>! Пока, <Имя_пользователя>! Как дела, <Имя_пользователя>?
        """
}]

def shit(response):
    if response[0:2] == "О,":
        response = "Бля"+response[1:]
    return response.replace("Вау", "Ахуеть").replace("вау", "ахуеть").replace("Ого", "Ебать").replace(" ого", " ебать").replace("Бетонная глыба", "Придурок").replace('нафиг', 'нахуй').replace('Ебатьнь', 'Огонь')

def message_send_pic(message, get_t):
    if message.text == "Да":
        bot.reply_to(message, "Пизда")
    else:
        if message.from_user.first_name == None:
            message.from_user.first_name = "Ноунейм"
        if message.from_user.last_name == None:
            message.from_user.last_name = " "
        name_u = message.from_user.first_name + " " + message.from_user.last_name
        # print(name_u)
        message.text = message.text.replace('"', '\\"')
        messages1=str(name_u)+": "+message.text
        response = run_conversation(messages1, get_t)
        response = shit(response)

        if random.randint(1, 10) == 6:
            bot.send_photo(message.chat.id, photo=gen(response), caption=response, reply_parameters=telebot.types.ReplyParameters(message.message_id))
        elif response in stickers.keys():
            bot.send_sticker(message.chat.id, sticker=stickers[response], reply_parameters=telebot.types.ReplyParameters(message.message_id))
        else:
            bot.reply_to(message, response)


def get_current_weather(location):
    """Get the current weather in a given location"""
    resp = req.get('https://api.openweathermap.org/geo/1.0/direct?q='+location+'&limit=5&appid=4b79e183c4904f7f107cc6301cee2732')

    weather = req.get('https://api.openweathermap.org/data/2.5/weather?lat='+str(resp.json()[0]['lat'])+'&lon='+str(resp.json()[0]['lon'])+'&appid=4b79e183c4904f7f107cc6301cee2732&lang=ru&unit=metric')

    weather_info = {
        "location": location,
        "temperature": str(int(weather.json()['main']['temp'])-273),
        "forecast": weather.json()['weather'][0]['description'],
    }
    return json.dumps(weather_info)

# def get_movie(question):
#     """Get the current weather in a given location"""
    
#     movie_info = {
#         "question": question,
#         "movie": "Интерстеллар",
#     }
#     return json.dumps(movie_info)


# def get_movie(question):
#     """Get the current weather in a given location"""
    
#     movie_info = {
#         "question": question,
#         "movie": "Интерстеллар",
#     }
#     return json.dumps(movie_info)

def run_conversation(messages, get_t):
    print(messages)
    messages_gig.append({"role": "user", "content": messages })
    messages_gig.append({"role": "assistant", "content": chat(get_t['access_token'], messages_gig)["choices"][0]['message']['content']})
    print("Саркастико: "+messages_gig[len(messages_gig)-1]['content'])
    weath = ""
    try:
        weath = get_current_weather(json.loads(messages_gig[len(messages_gig)-1]['content'])['city'])
    except json.decoder.JSONDecodeError:
        return messages_gig[len(messages_gig)-1]['content']
    messages_gig.append({"role": "user", "content": weath+"\nОтформатируй этот json как обычное сообщение о погоде в UTF-8." })
    messages_gig.append({"role": "assistant", "content": chat(get_t['access_token'], messages_gig)["choices"][0]['message']['content']})
    return messages_gig[len(messages_gig)-1]['content']
user_id = [1145705460, 1087968824, 777000]

@bot.channel_post_handler()
def handle_messages(messages):
    global get_t
    for message in messages:
        if int(float(time.time())*1000) > int(get_t['expires_at']):
            get_t = json.loads(get_token(x).content)
        if debug_mode:
            print(messages[0])
        message = messages[0]
        if message.content_type == "video" and (random.randint(0, 20) == 6 or message.from_user.id in user_id):
            # r_file = req.get(bot.get_file_url(message.video.file_id))
            file_info = bot.get_file(message.video.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file = open("otus.mp4", "wb+")
            file.write(downloaded_file)
            file.close()
            transcript = transcriber.transcribe("C:\\Users\\becke\\OneDrive\\Desktop\\bot\\otus.mp4")
            # transcript.text=transcript.text.replace("Субтитры сделал DimaTorzok", "")
            if debug_mode:
                print(transcript.text)
            if message.text != None:
                message.text = "Я отправил тебе видео. Вот о чем говорится в видео: \"" + transcript.text + "\"\n" + message.text
            elif message.caption != None:
                message.text = "Я отправил тебе видео. Вот о чем говорится в видео: \"" + transcript.text + "\"\n" + message.caption
            else:
                message.text = "Я отправил тебе видео. Вот о чем говорится в видео: \"" + transcript.text + "\""
            message_send_pic(message, get_t)
        elif message.content_type == "voice" and (random.randint(0, 20) == 6 or message.from_user.id in user_id):
            r_file = req.get(bot.get_file_url(message.voice.file_id))
            file = open("otus.mp4", "wb+")
            file.write(r_file.content)
            file.close()
            transcript = transcriber.transcribe("C:\\Users\\becke\\OneDrive\\Desktop\\bot\\otus.mp4")
            if debug_mode:
                print(transcript.text)
            if message.text != None:
                message.text = "Я отправил тебе голосовое сообщение. Вот содержимое голосового сообщения: \"" + transcript.text + "\"\n" + message.text
            elif message.caption != None:
                message.text = "Я отправил тебе голосовое сообщение. Вот содержимое голосового сообщения: \"" + transcript.text + "\"\n" + message.caption
            else:
                message.text = "Я отправил тебе голосовое сообщение. Вот содержимое голосового сообщения: \"" + transcript.text + "\""
            message_send_pic(message, get_t)
        elif message.content_type == "photo" and (random.randint(0, 20) == 6 or message.from_user.id in user_id):
            # if debug_mode:
            #     print("photo")
            # file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
            # downloaded_file = bot.download_file(file_info.file_path)
            # file = open("photus.png", "wb+")
            # file.write(downloaded_file)
            # file.close()
            # output = replicate.run(
            #     "methexis-inc/img2prompt:50adaf2d3ad20a6f911a8a9e3ccf777b263b8596fbd2c8fc26e8888f8a0edbb5",
            #     input={"image": open("photus.png", "rb")}
            # )
            # if debug_mode:
            #     print("output:")
            #     print(output)
            # if message.text != None:
            #     message.text = "Я отправил тебе фото. Вот описание фото: \"" + output + "\"\n" + message.text
            # elif message.caption != None:
            #     message.text = "Я отправил тебе фото. Вот описание фото: \"" + output + "\"\n" + message.caption
            # else:
            message.text = "Я отправил тебе фото."
            message_send_pic(message, get_t)
        elif message.content_type == "sticker" and (random.randint(0, 20) == 6 or message.from_user.id in user_id):
            # name_ru = translit(message.from_user.first_name, language_code='ru', reversed=True)
            # print(name_ru)
            message.text = message.sticker.emoji
            if message.from_user.first_name == None:
                message.from_user.first_name = "Ноунейм"
            if message.from_user.last_name == None:
                message.from_user.last_name = " "
            name_u = message.from_user.first_name + " " + message.from_user.last_name
            messages1=str(name_u)+": "+message.text
            # execute_query('INSERT INTO gpt_data(role, content, name) VALUES("'+"user"+'", "'+message.text+'", "'+name_ru+'")')

            # r1=execute_read_query("SELECT * FROM gpt_data WHERE id=1")
            # rM=execute_read_query("SELECT * FROM gpt_data ORDER BY id DESC")
            # r=execute_read_query("SELECT * FROM gpt_data WHERE id>"+str(len(rM)-31))

            messages_gig.append({"role": "user", "content": messages1 })
            messages_gig.append({"role": "assistant", "content": chat(get_t['access_token'], messages_gig)["choices"][0]['message']['content']})
            res = shit(messages_gig[len(messages_gig)-1]['content'])
            if res in stickers.keys():
                bot.send_sticker(message.chat.id, sticker=stickers[res], reply_parameters=telebot.types.ReplyParameters(message.message_id))
            elif len(res) == 1:
                stickers[res]=message.sticker.file_id
                print("!!!!!! "+ str(stickers))
                bot.send_sticker(message.chat.id, sticker=stickers[res], reply_parameters=telebot.types.ReplyParameters(message.message_id))
            else:
                bot.reply_to(message, res)
        elif message.text != None  and (random.randint(0, 20) == 6 or message.from_user.id in user_id):
            if message.text == "Да":
                bot.reply_to(message, "Пизда")
            else:
                if message.from_user.first_name == None:
                    message.from_user.first_name = "Ноунейм"
                if message.from_user.last_name == None:
                    message.from_user.last_name = " "
                name_u = message.from_user.first_name + " " + message.from_user.last_name
                message.text = message.text.replace('"', '\\"')
                messages1=str(name_u)+": "+message.text
                response = run_conversation(messages1, get_t)
                response = shit(response)
                if random.randint(1, 10) == 6:
                    bot.send_photo(message.chat.id, photo=gen(response), caption=response, reply_parameters=telebot.types.ReplyParameters(message.message_id))
                elif response in stickers.keys():
                    bot.send_sticker(message.chat.id, sticker=stickers[response], reply_parameters=telebot.types.ReplyParameters(message.message_id))
                else:
                    bot.reply_to(message, response)
        elif message.caption != None and (random.randint(0, 20) == 6 or message.from_user.id in user_id):
            if message.caption == "Да":
                bot.reply_to(message, "Пизда")
            else:
                if message.from_user.first_name == None:
                    message.from_user.first_name = "Ноунейм"
                if message.from_user.last_name == None:
                    message.from_user.last_name = " "
                name_u = message.from_user.first_name + " " + message.from_user.last_name
                message.text = message.text.replace('"', '\\"')
                messages1=str(name_u)+": "+message.text
                response = run_conversation(messages1, get_t)
                response = shit(response)
                if random.randint(1, 10) == 6:
                    bot.send_photo(message.chat.id, photo=gen(response), caption=response, reply_parameters=telebot.types.ReplyParameters(message.message_id))
                elif response in stickers.keys():
                    bot.send_sticker(message.chat.id, sticker=stickers[response], reply_parameters=telebot.types.ReplyParameters(message.message_id))
                else:
                    bot.reply_to(message, response)

        # Do something with the message
        # if message.text != None:
        #     if message.text == "Что за фильм?":
        #         bot.reply_to(message, 'Интерстеллар')
        #     elif message.text == "Спасибо":
        #         bot.reply_to(message, 'Пожалуйста')
        #     elif message.text == "Не понял":
        #         bot.reply_to(message, 'Это потому что ты тупой')
        #     elif message.text.find("хочу сделать") != -1:
        #         bot.reply_to(message, "Аахахахаха! Опять как всегда всё через жопу сделаешь! \U0001F923")
        #     elif message.text.find("не буду") != -1:
        #         bot.reply_to(message, "Ну вот ты и слился")
        #     elif message.text == "Пошел нахуй" or message.text == "Пошел нах" or message.text == "Иди нахуй":
        #         bot.reply_to(message, 'Сам иди')
        # elif message.caption != None:
        #     if message.caption == "Что за фильм?":
        #         bot.reply_to(message, 'Интерстеллар')
        #     elif message.caption.find("хочу сделать") != -1:
        #         bot.reply_to(message, "Аахахахаха! Опять как всегда всё через жопу сделаешь! \U0001F923")
        #     elif message.caption.find("не буду") != -1:
        #         bot.reply_to(message, "Ну вот ты и слился")

bot.set_update_listener(handle_messages)
bot.infinity_polling()