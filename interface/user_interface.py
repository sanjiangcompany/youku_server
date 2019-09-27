from db import models
from lib import common
import os
from conf import settings


@common.login_auth
def buy_vip_interface(client_back_dic, conn):

    user_id = client_back_dic.get('user_id')

    user_obj = models.User.select(id=user_id)[0]
    user_obj.is_vip = 1
    user_obj.sql_update()

    send_dic = {'flag': True, 'msg': '会员充值成功!'}

    common.send_data(send_dic, conn)


@common.login_auth
def download_movie_interface(client_back_dic, conn):

    movie_id = client_back_dic.get('movie_id')
    movie_name = client_back_dic.get('movie_name')
    movie_type = client_back_dic.get('movie_type')
    user_id = client_back_dic.get('user_id')
    # movie_obj = models.Movie.select(id=movie_id)[0]
    # movie_path = movie_obj.path
    movie_path = os.path.join(settings.DOWNLOAD_PATH, movie_name)
    movie_size = os.path.getsize(movie_path)
    send_dic = {
        'flag': True, 'msg': '准备下载', 'movie_size': movie_size
    }
    user_obj = models.User.select(id=user_id)[0]

    if movie_type == '免费':
        wait_time = 0

        if not user_obj.is_vip:

            wait_time = 20

        send_dic['wait_time'] = wait_time

    print(send_dic)
    common.send_data(send_dic, conn, movie_path)

    obj = models.DownloadRecord(user_id=user_id, movie_id=movie_id,
                          download_time=common.get_time())
    obj.save()


@common.login_auth
def check_download_record_interface(client_back_dic, conn):
    record_obj_list = models.DownloadRecord.select()
    user_id = client_back_dic.get('user_id')

    back_record_list = []

    if record_obj_list:
        for record_obj in record_obj_list:
            if record_obj.user_id == user_id:

                # 获取当前用户下载电影记录的电影对象
                movie_obj = models.Movie.select(id=record_obj.movie_id)[0]

                back_record_list.append(
                    movie_obj.name
                )

            else:
                send_dic = {'flag': False, 'msg': '当前用户没有下载记录!'}

        send_dic = {
            'flag':True, 'record_list': back_record_list
        }

    else:
        send_dic = {'flag': False, 'msg': '没有任何下载记录!'}

    common.send_data(send_dic, conn)


@common.login_auth
def check_all_notice_interface(client_back_dic, conn):

    notice_obj_list = models.Notice.select()

    back_notice_list = []

    if notice_obj_list:

        for notice_obj in notice_obj_list:
            title = notice_obj.title
            content = notice_obj.content
            back_notice_list.append(
                {'title': title, 'content': content}
            )

        send_dic = {'flag': True, 'back_notice_list': back_notice_list}

    else:
        send_dic = {'flag': False, 'msg': '没有公告!'}

    common.send_data(send_dic, conn)