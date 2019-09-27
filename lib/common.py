import time
import hashlib
import json
import struct
import uuid
from functools import wraps
from db import user_data


def get_time():

    now_time = time.strftime('%Y-%m-%d %X')

    return now_time


def get_md5_pwd(pwd):
    md = hashlib.md5()

    md.update(pwd.encode('utf-8'))
    md.update('虹桥炮王，Jason是也!'.encode('utf-8'))

    return md.hexdigest()



def send_data(send_dic, conn, file=None):
    data_bytes = json.dumps(send_dic).encode('utf-8')
    headers = struct.pack('i', len(data_bytes))
    conn.send(headers)
    conn.send(data_bytes)
    if file:
        with open(file, 'rb') as f:
            for line in f:
                conn.send(line)


def get_random_code():
    # uuid可以产生一个世界上唯一的字符串
    md5 = hashlib.md5()
    md5.update(str(uuid.uuid4()).encode('utf-8'))
    return md5.hexdigest()


# 登录认证装饰器
def login_auth(func):
    @wraps(func)
    # (client_back_dic, conn) = args
    def inner(*args, **kwargs):
        # if args[0].get('session') == 服务端存放的session值：
        # # [session, user_id] = values

        addr = args[0].get('addr')
        # addr: [session, user_id]

        # [session, user_id]
        user_session = user_data.user_online.get(addr)
        if user_session:
            if args[0].get('session') == user_session[0]:

                args[0]['user_id'] = user_session[1]
        #
        # for values in user_data.user_online.values():
        #     if args[0].get('session') == values[0]:
        #         # 添加到client_back_dic
        #         args[0]['user_id'] = values[1]  # user_id

        # 判断user_id是否存在
        if args[0].get('user_id'):
            func(*args, **kwargs)

        else:
            send_dic = {'flag': False, 'msg': '未登录，请去登录!'}
            # send_data(send_dic, conn)

            send_data(send_dic, args[1])

    return inner

# if __name__ == '__main__':
#
#     # print(get_time())
#     print(get_random_code())
    # 05248e1b1a10ac08872f8dd5d9dbd814
    # 161df6d362dc52b0037d938a0717963e
    # aabd3987f88b2db46566cf6d9ec864e2