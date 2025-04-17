import telegram
import time
import sys
import asyncio

control_file_path = './control.txt'
config_file_path = './config.txt'

async def log_telegram_sub(text) :
    with open(config_file_path, "r") as file_in :
        all_content = file_in.readlines();
        token = ""    

        for line in all_content:
            if(line.split('=')[0].strip()=="TELEGRAM_LOG_BOT_TOKEN") :
                token = line.split('=')[1].strip()

        bot = telegram.Bot(token=token)
        my_bot_id = 1836873714;
    
    with open("telegram.log", "a") as file_out:
        tt = time.localtime()
        file_out.write("{YYYY}_{mm}_{dd} {HH}:{MM}:{SS}".format(YYYY=tt.tm_year, mm=tt.tm_mon, dd=tt.tm_mday, HH=tt.tm_hour, MM=tt.tm_min, SS=tt.tm_sec))
        file_out.write(text)
        file_out.write("\n");
    try:
        await bot.sendMessage(chat_id=my_bot_id, text=text);
    except:
        with open("error.log", "a") as file_out:
            tt2 = time.localtime()
            file_out.write("{YYYY}_{mm}_{dd} {HH}:{MM}:{SS}".format(YYYY=tt2.tm_year, mm=tt2.tm_mon, dd=tt2.tm_mday, HH=tt2.tm_hour, MM=tt2.tm_min, SS=tt2.tm_sec))
            file_out.write("telegram send message failed : ")
            file_out.write(text)
            file_out.write("\n");
    print(text);

async def send_image_sub(file_name) :
    with open(config_file_path, "r") as file_in :
        all_content = file_in.readlines();
        token = ""    
        for line in all_content:
            if(line.split('=')[0].strip()=="TELEGRAM_LOG_BOT_TOKEN") :
                token = line.split('=')[1].strip()

        bot = telegram.Bot(token=token)
        my_bot_id = 1836873714;
    try:
        await bot.send_photo(my_bot_id, photo=open(file_name, 'rb'))
    except:
        print('error send image')

def log_telegram(text) :
    asyncio.run(log_telegram_sub(text))
    return 0

def send_image(text) :
    asyncio.run(send_image_sub(text))
    return 0
