from lib import common
from db import models
import os
from conf import settings

@common.login_auth
def upload_movie_interface(client_back_dic, conn):
    print('炮王来交货啦!')

    # 确保电影名称是唯一的  随机字符串 + 电影名称
    movie_name = common.get_random_code() + client_back_dic.get('movie_name')  # .mp4

    movie_size = client_back_dic.get('file_size')

    movie_path = os.path.join(
        settings.DOWNLOAD_PATH, movie_name
    )

    # 1.接受上传的电影
    data_recv = 0
    with open(movie_path, 'wb') as f:
        while data_recv < movie_size:
            data = conn.recv(1024)
            f.write(data)
            data_recv += len(data)

    # 2.把电影数据保存到mysql中
    movie_obj = models.Movie(
        name=movie_name, file_md5=client_back_dic.get('file_md5'),
        is_free=client_back_dic.get('is_free'), is_delete=0,
        path=movie_path, user_id=client_back_dic.get('user_id'),
        upload_time=common.get_time()
    )
    movie_obj.save()

    send_dic = {
        'flag': True, 'msg': f'{client_back_dic.get("movie_name")}电影上传成功!'
    }

    common.send_data(send_dic, conn)


@common.login_auth
def check_movie_interface(client_back_dic, conn):

    file_md5 = client_back_dic.get('file_md5')

    movie_list = models.Movie.select(file_md5=file_md5)

    if movie_list:

        send_dic = {
            'flag': False, 'msg': '电影已存在!'
        }

    else:

        send_dic = {
            'flag': True, 'msg': '电影可以上传'
        }

    common.send_data(send_dic, conn)


@common.login_auth
def delete_movie_interface(client_back_dic, conn):
    movie_id = client_back_dic.get('movie_id')
    # 直接删除
    movie_obj = models.Movie.select(id=movie_id)[0]
    movie_obj.is_delete = 1
    # 调用更新方法
    movie_obj.sql_update()

    send_dic = {
        'flag': True, 'msg': '电影删除成功!'
    }

    common.send_data(send_dic, conn)


@common.login_auth
def put_notice_interface(client_back_dic, conn):
    title = client_back_dic.get('title')
    content = client_back_dic.get('content')
    user_id = client_back_dic.get('user_id')
    notice_obj = models.Notice(title=title, content=content, user_id=user_id,
                  create_time=common.get_time())

    notice_obj.save()

    send_dic = {
        'msg': '公告发布成功!'
    }

    common.send_data(send_dic, conn)