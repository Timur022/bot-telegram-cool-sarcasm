import telebot
from sys import argv



bot = telebot.TeleBot("6365480968:AAHLyOpHK45Sr9vzNvrl56q83z-HxZ1tICk")

if int(argv[1]) > 999:
	file = open("C:\\Users\\becke\\OneDrive\\Desktop\\bot\\0001-"+str(argv[1])+".mp4", 'rb')
	video=file.read()
	file.close()
else:
	file = open("C:\\Users\\becke\\OneDrive\\Desktop\\bot\\0001-0"+str(argv[1])+".mp4", 'rb')
	video=file.read()
	file.close()

bot.send_video_note(chat_id="-1001898091141", data=video, disable_notification=True)

# group
# "-1001898091141"

# test
# -1001633145413