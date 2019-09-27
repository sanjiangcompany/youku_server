from orm.orm import Models, StringField, IntegerField


# 用户表
class User(Models):
    # 表名
    table_name = 'user'
    # 字段
    id = IntegerField(name='id', primary_key=True)
    name = StringField(name='name')
    #  pwd, is_vip, is_locked, user_type, register_time
    pwd = StringField(name='pwd')
    is_vip = IntegerField(name='is_vip')
    is_locked = IntegerField(name='is_locked')
    user_type = StringField(name='user_type')
    register_time = StringField(name='register_time')


# 电影表
class Movie(Models):
    # 表名
    table_name = 'movie'
    # 字段
    id = IntegerField(name='id', primary_key=True)
    name = StringField(name='name')
    # path, is_free, file_md5, user_id, is_delete, upload_time
    path = StringField(name='path')
    is_free = IntegerField(name='is_free')  # 1   0
    file_md5 = StringField(name='file_md5')
    user_id = IntegerField(name='user_id')
    is_delete = IntegerField(name='is_delete')
    upload_time = StringField(name='upload_time')


# 公告表
class Notice(Models):
    table_name = 'notice'
    # 字段
    id = IntegerField(name='id', primary_key=True)
    title = StringField(name='title')
    content = StringField(name='content')
    user_id = IntegerField(name='user_id')
    create_time = StringField(name='create_time')


# 下载记录表
class DownloadRecord(Models):
    table_name = 'download_record'
    # 字段
    id = IntegerField(name='id', primary_key=True)
    user_id = IntegerField(name='user_id')
    movie_id = IntegerField(name='movie_id')
    download_time = StringField(name='download_time')
