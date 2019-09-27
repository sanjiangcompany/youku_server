import socket
import struct
import json
from interface import common_interface
from interface import admin_interface
from interface import user_interface
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from lib import lock_file
from db import user_data

lock = Lock()

lock_file.mutex = lock


func_dic = {
    'register': common_interface.register_interface,
    'login': common_interface.login_interface,
    # 查看电影是否存在接口
    'check_movie': admin_interface.check_movie_interface,

    'upload_movie': admin_interface.upload_movie_interface,

    # 获取电影列表接口
    'get_movie_list': common_interface.get_movie_list_interface,

    'delete_movie': admin_interface.delete_movie_interface,

    'put_notice': admin_interface.put_notice_interface,

    # 普通用户功能
    'buy_vip': user_interface.buy_vip_interface,
    'download_movie': user_interface.download_movie_interface,
    'check_download_record': user_interface.check_download_record_interface,
    'check_all_notice': user_interface.check_all_notice_interface,
}


class SocketServer:
    def __init__(self):
        self.server = socket.socket()
        self.server.bind(
            ('192.168.11.236', 8888)
        )
        self.server.listen(5)
        self.pool = ThreadPoolExecutor(50)


    def run(self):
        print('启动服务端...')
        while True:
            conn, addr = self.server.accept()  # 1 2 3
            # 通过self.pool 线程池异步提交任务（working）
            # self.pool.submit(函数对象, 传递给函数对象的参数1, 参数2)  # 1 2 3
            self.pool.submit(self.working, conn, addr)  # 1 2 3

    # 任务分发
    def dispatcher(self, client_back_dic, conn):
        # # 判断功能的类型
        # if client_back_dic.get('type') == 'register':
        #     common_interface.register_interface(client_back_dic, conn)
        #
        # elif client_back_dic.get('type') == 'login':
        #     common_interface.login_interface(client_back_dic, conn)

        # 通过_type变量接受客户端选择的功能类型
        _type = client_back_dic.get('type')  # login

        if _type in func_dic:  # register
            func_dic.get(_type)(client_back_dic, conn)

    # 用于执行客户端连接任务
    def working(self,  conn, addr):
        while True:
            try:
                # 每一个客户端访问服务端都会经过此处
                # 此处用于接收客户端传入的数据
                headers = conn.recv(4)
                data_len = struct.unpack('i', headers)[0]
                data_bytes = conn.recv(data_len)
                client_back_dic = json.loads(data_bytes.decode('utf-8'))
                # 把每个用户的addr一并赋值给客户端传过来的字典
                client_back_dic['addr'] = str(addr)
                # 把客户端传递过来的字典与conn传给dispatcher执行
                self.dispatcher(client_back_dic, conn)

            except Exception as e:
                print(e)
                lock.acquire()
                user_data.user_online.pop(str(addr))
                lock.release()
                conn.close()
                break
