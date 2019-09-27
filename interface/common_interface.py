from db import models
from lib import common, lock_file
from db import user_data


def register_interface(client_back_dic, conn):

    # 写业务逻辑
    # 1.判断用户名是否存在
    username = client_back_dic.get('username')
    # 通过用户名当作条件查询
    user_obj_list = models.User.select(name=username)

    # 若存在，给客户端返回数据, 告诉用户，用户已存在!
    if user_obj_list:
        send_dic = {'flag': False, 'msg': '用户已存在!'}

    # 若不存在，保存数据到MySQL数据库中， 返回注册成功给客户端
    else:
        password = client_back_dic.get('password')
        user_obj = models.User(
            name=username,
            #  pwd, is_vip, is_locked, user_type, register_time
            pwd=common.get_md5_pwd(password),
            is_vip=0,  # 0表示不是VIP， 1表示VIP
            is_locked=0,  # 0表示不锁定， 1表示锁定
            user_type=client_back_dic.get('user_type'),
            register_time=common.get_time())

        user_obj.save()

        send_dic = {'flag': True, 'msg': '注册成功'}

    common.send_data(send_dic, conn)


def login_interface(client_back_dic, conn):
    # 执行login业务逻辑
    username = client_back_dic.get('username')

    # 1.根据用户名查询用户数据
    user_list = models.User.select(name=username)

    if not user_list:
        send_dic = {'flag': False, 'msg': '用户不存在'}

    else:
        user_obj = user_list[0]
        password = client_back_dic.get('password')
        # 1.判断客户端传入的密码与数据库中的密码是否相等
        if user_obj.pwd == common.get_md5_pwd(password):

            # 产生一个随机字符串，作为session值
            session = common.get_random_code()
            addr = client_back_dic.get('addr')
            # 保存session值到服务端，session + user_id一同保存到服务端本地
            # 使用锁写入数据
            lock_file.mutex.acquire()
            #  str(addr)
            user_data.user_online[addr] = [session, user_obj.id]
            lock_file.mutex.release()

            send_dic = {'flag': True, 'msg': '登录成功!',
                       'session': session, 'is_vip': user_obj.is_vip, 'new_notice': None}

            new_notice = get_new_notice_interface()

            if not new_notice:
                pass

            else:
                send_dic['new_notice'] = new_notice

        else:
            send_dic = {'flag': False, 'msg': '密码错误!'}

    common.send_data(send_dic, conn)


# 获取电影接口
@common.login_auth
def get_movie_list_interface(client_back_dic, conn):

    # 获取所有电影对象
    movie_obj_list = models.Movie.select()
    # 添加未删除的电影列表
    back_movie_list = []

    if movie_obj_list:

        # 过滤已删除的电影
        for movie_obj in movie_obj_list:

            # 没有删除则返回
            if not movie_obj.is_delete:  # 1 代表删除

                if client_back_dic.get('movie_type') == 'all':
                    back_movie_list.append(
                        # [电影名称、是否免费、电影ID]
                        [movie_obj.name,'免费' if movie_obj.is_free else "收费", movie_obj.id]
                    )

                elif client_back_dic.get('movie_type') == 'free':
                    # 判断哪些电影是免费的
                    if movie_obj.is_free:
                        back_movie_list.append(
                            [movie_obj.name, '免费', movie_obj.id]
                        )

                else:
                    if not movie_obj.is_free:
                        back_movie_list.append(
                            [movie_obj.name, '收费', movie_obj.id]
                        )



        if back_movie_list:

            send_dic = {'flag': True, 'back_movie_list': back_movie_list}

        else:
            send_dic = {'flag': False, 'msg': '没有电影!'}
    else:

        send_dic = {'flag': False, 'msg': '没有电影!'}

    common.send_data(send_dic, conn)



def get_new_notice_interface():

    # 1.获取所有的公告
    notice_obj_list = models.Notice.select()  # 展示此处notice_obj_list的数据
    if not notice_obj_list:
        return False

    # 2.对公告的发布时间或者id进行排序，获取最新的一条公告

    notice_desc_list = sorted(
        # [notice_obj, notice_obj,notice_obj。。。]
        # 选择1：根据ID notice_obj_list, key=lambda notice_obj: notice_obj.id
        # 选择2：根据时间
        notice_obj_list, key=lambda notice_obj: notice_obj.create_time, reverse=True
    )

    new_notice = {
        'title': notice_desc_list[0].title,
        'content': notice_desc_list[0].content,
    }
    return new_notice

