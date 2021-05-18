import telebot     # run telegram bot
import random
from datetime import datetime # generate log


my_dict = { 0: 'нөл', 1: 'бір', 2: 'екі', 3: 'үш', 4: 'төрт', 5: 'бес', 6: 'алты', 7: 'жеті', 8: 'сегіз', 9: 'тоғыз' }

user = dict()

def log(text):
    time_stamp = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    print(time_stamp + " " + text)



def get_random_numbers():
    a = []
    for i in range(5):
        a.append(random.randint(0,9))

    return a

if __name__ == "__main__":
    with open("creds/digits_2021_dataset_bot.txt", "r") as f:
        audio_digits_dataset_creds = f.read().strip() # "  hello world \t\n" -> "hello world"
    bot = telebot.TeleBot(audio_digits_dataset_creds)
    print(audio_digits_dataset_creds)

    @bot.message_handler(commands = ['start'])
    def get_text_messages(message):
        user_id = message.from_user.id
        user_name = message.from_user.username
        answer = "Сәлем, дос! Маған сөйлеу тану бойыншы оқу моделін құру үшін мәліметтер базасы қажет. Сенің көмегің өте маңызды! Жалғастыру үшін /alga бас"
        bot.send_message(user_id, answer)

    @bot.message_handler(commands = ['alga'])
    def get_task(message):
        user_id = message.from_user.id
        numbers = get_random_numbers()
        print(numbers)
        value = []
        for number in numbers:
            value.append(my_dict[number])
        value = ('_').join(value)
        print(value)
        user[user_id] = value
        bot.send_message(user_id, "Келесі сандарды бір секунд үзіліспен айтып шық {0}".format(str(value)))


    @bot.message_handler(content_types=['voice', 'text']) # decorator
    def get_voice(message):
        user_id = message.from_user.id
        user_name = message.from_user.username
        if message.text:
            answer = "Send voice!"
            bot.send_message(user_id, answer)
            return

        log_text = "User ({0}): {1}".format(user_name, str(message.voice))
        log(log_text)

        tele_file = bot.get_file(message.voice.file_id)
        log_text = "User ({0}): {1}".format(user_name, str(tele_file))
        log(log_text)

        ogg_data = bot.download_file(tele_file.file_path)
        with open("data/ogg/" + user[user_id] + ".ogg", "wb") as f:
            f.write(ogg_data)


        answer = "Рақмет! Тағы дауыс тіркелу үшін /alga бас."
        bot.send_message(user_id, answer)


    bot.polling(none_stop=True, interval=0)
