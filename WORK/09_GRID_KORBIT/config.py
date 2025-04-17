import sys
#import my_telegram_bot
import time

control_file_path = './control.txt'
config_file_path = './config.txt'

if(len(sys.argv)==3) :
    config_file_path = sys.argv[1]
    control_file_path = sys.argv[2]
#else :
#    my_telegram_bot.log_telegram('warning: config/control files are not specified')

def get_config(param) :
    file_in = open(config_file_path, 'r')
    all_content = file_in.readlines()

    value = "NO_VALUE"

    for line in all_content:
        if(line.split('=')[0].strip()==param) :
            value = line.split('=')[1].strip()
            break

    if(value == 'NO_VALUE') :
        time.sleep(1)
        for line in all_content:
            if(line.split('=')[0].strip()==param) :
                value = line.split('=')[1].strip()
                break
        #if(value == 'NO_VALUE') :
        #    my_telegram_bot.log_telegram('error : param '+param+' is no defined in file '+ config_file_path)
        #    exit()

    return value


def get_control(param) :
    file_in = open(control_file_path, 'r')
    all_content = file_in.readlines()

    value = 'NO_VALUE'

    for line in all_content:
        if(line.split('=')[0].strip()==param) :
            value = line.split('=')[1].strip()

    if(value == 'NO_VALUE') :
        time.sleep(1)
        for line in all_content:
            if(line.split('=')[0].strip()==param) :
                value = line.split('=')[1].strip()
                break
        #if(value == 'NO_VALUE') :
        #    my_telegram_bot.log_telegram('error : param '+param+' is no defined in file '+ control_file_path)
        #    exit()

    return value

def set_control(param, value) :
    file_in = open(control_file_path, 'r')
    all_content = file_in.readlines()
    file_in.close()

    file_out = open(control_file_path, 'w')
    for line in all_content :
        if(line.split('=')[0].strip()==param) :
            file_out.write(param+'='+str(value)+'\n')
        else :
            file_out.write(line)
