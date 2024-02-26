from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
import telebot
token="6365480968:AAHLyOpHK45Sr9vzNvrl56q83z-HxZ1tICk"

bot=telebot.TeleBot(token)
@bot.message_handler()
def start_message(message):
	# print(message)
	bot.send_message(message.chat.id,"Привет ✌️")
bot.infinity_polling()

# chat = GigaChat(credentials="MzRiZWIyNGUtN2E0ZC00NDU5LTliNTAtYjU3NGE3MzFhODBlOjE0YTA2YmZlLWRhYzgtNDcwYy05ZGNiLTBmYzBmNDk4MWIzYg==", verify_ssl_certs=False)
# print(chat.get_models())
# messages = [
#     SystemMessage(
#         content="Ты токсичный бот-тролль, который саркастично общается с подписчиками телеграмм канала."
#     )
# ]

# while(True):
#     user_input = input("User: ")
#     messages.append(HumanMessage(content=user_input))
#     res = chat(messages)
#     messages.append(res)
#     print("Bot: ", res.content)