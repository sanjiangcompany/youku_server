'''
定义字段类
'''
from orm.mysql_control import Mysql


class Field:
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default


# varchar
class StringField(Field):
    def __init__(self, name, column_type='varchar(255)', primary_key=False, default=None):
        super().__init__(name, column_type, primary_key, default)


# int
class IntegerField(Field):
    def __init__(self, name, column_type='int', primary_key=False, default=0):
        super().__init__(name, column_type, primary_key, default)


# 元类控制表模型类的创建
class OrmMetaClass(type):

    # 类名, 类的基类, 类的名称空间
    def __new__(cls, class_name, class_bases, class_attr):
        # print(class_name, class_bases, class_attr)
        # 1.过滤Models类
        if class_name == 'Models':
            return type.__new__(cls, class_name, class_bases, class_attr)

        # 2.控制模型表中: 表名, 主键, 表的字段
        # 如果模型表类中没有定义table_name,把类名当做表名

        # 获取表名
        table_name = class_attr.get('table_name', class_name)  # user_info, User

        # 3.判断是否只有一个主键
        primary_key = None

        # 用来存放所有的表字段, 存不是目的,目的是为了取值方便
        mappings = {}

        '''
        __main__: xxxx
        'id': <__main__.IntegerField object at 0x000001E067D48B00>, 
        'name': <__main__.StringField object at 0x000001E067D48AC8>}
        '''
        for key, value in class_attr.items():

            # 判断value是否是字段类的对象
            if isinstance(value, Field):

                # 把所有字段都添加到mappings中
                mappings[key] = value

                if value.primary_key:

                    if primary_key:
                        raise TypeError('主键只能有一个')

                    # 获取主键
                    primary_key = value.name

        # 删除class_attr中与mappings重复的属性, 节省资源
        for key in mappings.keys():
            class_attr.pop(key)

        # 判断是否有主键
        if not primary_key:
            raise TypeError('必须要有一个主键')

        class_attr['table_name'] = table_name
        class_attr['primary_key'] = primary_key
        class_attr['mappings'] = mappings
        '''
               'table_name': table_name
               'primary_key': primary_key
               'mappings': {'id': <__main__.IntegerField object at 0x000001E067D48B00>,
                            'name': <__main__.StringField object at 0x000001E067D48AC8>}
                            }
       '''
        return type.__new__(cls, class_name, class_bases, class_attr)


# 继承字典类,
class Models(dict, metaclass=OrmMetaClass):
    def __init__(self, **kwargs):
        # print(kwargs)  # 接收关键字参数
        super().__init__(**kwargs)

    # 在对象.属性没有的时候触发
    def __getattr__(self, item):
        # print(item)
        return self.get(item, '没有这个key')

    # 在对象.属性 = 属性值 时触发
    def __setattr__(self, key, value):

        # 字典赋值操作
        self[key] = value

    # 查
    @classmethod
    def select(cls, **kwargs):

        # 获取数据库链接对象
        ms = Mysql()

        # 若没有kwargs代表没有条件查询
        if not kwargs:
            # select * from table;
            sql = 'select * from %s' % cls.table_name

            res = ms.my_select(sql)

        # 若有kwargs代表有条件
        else:
            # print(kwargs)  # {id:1}
            key = list(kwargs.keys())[0]  # id
            value = kwargs.get(key)  # 1

            # select * from table where id=1;
            sql = 'select * from %s where %s=?' % (
                cls.table_name, key
            )

            sql = sql.replace('?', '%s')

            res = ms.my_select(sql, value)

        if res:
            # [{},{}, {}]   ---->  [obj1, obj2, obj3]
            # 把mysql返回来的 列表套 字典 ---> 列表套 对象
            # l1 = []
            # # 遍历mysql返回所有的字典
            # for d in res:
            #     # 把每一个字典传给cls实例化成一个个的r1对象
            #     r1 = cls(**d)
            #     # 追加到l1列表中
            #     l1.append(r1)

            return [cls(**result) for result in res]

    # 插入
    def save(self):
        ms = Mysql()
        # insert into table(x,x,x) values(x,x,x);

        # 字段名
        fields = []
        # 字段的值
        values = []
        # 存放对应字段的?号
        args = []

        for k, v in self.mappings.items():
            # 把主键过滤掉
            if not v.primary_key:
                fields.append(
                    v.name
                )
                values.append(
                    getattr(self, v.name, v.default)
                )
                args.append('?')

        # insert into table(x,x,x) values(?, ?, ?);
        sql = 'insert into %s(%s) values(%s)' % (
            self.table_name, ','.join(fields), ','.join(args)
        )

        sql = sql.replace('?', '%s')

        ms.my_execute(sql, values)

    # 更新
    def sql_update(self):
        ms = Mysql()

        fields = []
        primary_key = None
        values = []

        for k, v in self.mappings.items():
            # 获取主键的值
            if v.primary_key:
                primary_key = getattr(self, v.name, v.default)

            else:

                # 获取 字段名=?, 字段名=?,字段名=?
                fields.append(
                    v.name + '=?'
                )

                # 获取所有字段的值
                values.append(
                    getattr(self, v.name, v.default)
                )

        # update table set %s=?,... where id=1;  把主键当做where条件
        sql = 'update %s set %s where %s=%s' % (
            self.table_name, ','.join(fields), self.primary_key, primary_key
        )

        # print(sql)  # update User set name=? where id=3

        sql = sql.replace('?', '%s')

        ms.my_execute(sql, values)


# User, Movie, Notice
# 表模型类
class User(Models):
    # table_name = 'user_info'
    id = IntegerField(name='id', primary_key=True)
    name = StringField(name='name')
    # pwd = StringField(name='pwd')


class Movie(Models):
    id = IntegerField(name='id', primary_key=True)
    pass


# # # User('出入任意个数的关键字参数')
# user_obj = User()  # user_obj--->dict
# user_obj.name = 'xxxx'

# if __name__ == '__main__':
#     res = User.select(name='jason_sb')[0]
#     print(res)
#
#     # res.name = 'jason_sb'
#     #
#     # res.sql_update()
#
#     # user_obj = User(name='egon')
#     # user_obj.save()
#
# '''
# 表:
#     表名, 只有一个唯一的主键, 字段(必须是Field的字段)
#
# 元类:
#     通过元类控制类的创建.
# '''
#
# # class Movie:
# #     def __init__(self, movie_name, movie_type):
# #         self.movie_name = movie_name
# #         self.movie_type = movie_type
# #
# #
# # class Notice:
# #     def __init__(self, title, content):
# #         self.title = title
# #         self.content = content
#
# '''
# 问题1: 所有表类都要写__init__, 继承一个父类
# 问题2: 可以接收任意个数以及任意名字的关键字参数. 继承python中的字典对象.
# '''
#
# # if __name__ == '__main__':
# #     # d1 = dict({'name': 'tank'})
# #     # d2 = dict(name='tank2')
# #     # print(d1)
# #     # print(d2)
# #
# #     d3 = Models(name='jason')
# #     # print(d3)
# #     # print(d3.get('name'))
# #     # print(d3['name'])
# #     # print(d3.name)
# #     # d3.name = 'tank'
# #     # d3.pwd = '123'
# #     # print(d3.name)
# #     # print(d3)
# #     print(d3.name)  # None
# #
# #     d3.pwd = '123'
# #     print(d3.pwd)
# #     print(d3)


if __name__ == '__main__':
    # 查看所有
    # res = User.select()
    # print(res)

    # 根据查询条件查询
    res = User.select(name='json_egon_sb')
    print(res)
#
#     # 更新
#     # user_obj = res[0]
#     # user_obj.name = 'jason_sb_sb'
#     # user_obj.sql_update()  # {'id': 3, 'name': 'jason_sb'}
#
#     # 插入
#     # user_obj = User(name='json_egon_sb')
# #     # user_obj.save()