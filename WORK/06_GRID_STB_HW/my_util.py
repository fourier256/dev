import time

buf = ''

def print_log(txt) :
    ''' comment '''
    global buf
    print(txt)
    buf += '\n'
    buf += txt
    lt = time.localtime()
    tt = str(lt.tm_hour)+':'+str(lt.tm_min)+':'+str(lt.tm_sec)
    open('UBA.log', 'a').write(txt+' - ' + tt +'\n')

def get_buf() :
    global buf
    bufbuf = buf
    buf = ''
    return bufbuf
