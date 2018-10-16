#!usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
from bmamember import BMAMember

class BMAdb(object):

    DB_INFO = {
        'host': '127.0.0.1',
        'user': 'root',
        'passwd': 'mataleao0',
        'charset': 'utf8'
    }

    DB_NAME = 'bmagym'
    TABLE_PAY_LOG = 'pay_log'
    TABLE_MEMBER = 'member'

    def __init__(self):
        """ 初始化数据库
        1. 建立数据库bmagym
        2. 建立数据表pay_log，用于存储付款log
            表结构说明：
                l_id: log id
                u_id: 付款用户id
                pay_time: 付款时间
                buy_duration: 本次付款所购买的时长
                buy_count: 本次付款所购买的次数
                event_id: 生效的活动id
                recommended_by: 推荐人/会籍顾问id
                comment: 备注

        3. 建立数据表members，用于存储会员信息
            表结构说明：
                u_id: 用户id
                nickname: 微信名字
                realname: 真实姓名
                wechat_id: 微信id
                sex: 性别 0-Unknown 1-male 2-female
                tel: 电话
                paper_type: 证件类型
                paper_number: 证件号码
                email: 邮箱
                birthday: 生日
                duration left: 剩余时间
                count left: 剩余次数
                comment: 备注

        4. 建立数据表events，用于存储活动信息
        """
        try:
            conn = MySQLdb.connect(**self.DB_INFO)

            with conn:
                cursor = conn.cursor()

                # 如果没有数据库就新建一个
                sql = (
                    'CREATE DATABASE IF NOT EXISTS %s '
                    'DEFAULT CHARSET utf8 '
                    'COLLATE utf8_general_ci'
                    %self.DB_NAME
                )
                cursor.execute(sql)
                conn.select_db(self.DB_NAME)

                # 如果没有pay_log表就新建一个
                sql = (
                    'CREATE TABLE IF NOT EXISTS %s('
                        'l_id int NOT NULL AUTO_INCREMENT,'
                        'u_id int NOT NULL,'
                        'pay_time datetime DEFAULT CURRENT_TIMESTAMP NOT NULL,'
                        'buy_duration smallint,'
                        'buy_count smallint,'
                        'event_id int,'
                        'recommended_by int,'
                        'comment text,'
                        'PRIMARY KEY(l_id)'
                    ')' %self.TABLE_PAY_LOG
                )
                cursor.execute(sql)

                # 如果没有members表就建一个
                sql = (
                    'CREATE TABLE IF NOT EXISTS %s('
                        'u_id int NOT NULL AUTO_INCREMENT,'
                        'nickname varchar(30),'
                        'realname varchar(30),'
                        'wechat_id varchar(30),'
                        'sex tinyint(1),'
                        'tel varchar(13),'
                        'paper_type varchar(10),'
                        'paper_number varchar(30),'
                        'email varchar(30),'
                        'birthday date,'
                        'duration_left smallint,'
                        'count_left smallint,'
                        'comment text,'
                        'PRIMARY KEY(u_id)'
                    ')' %self.TABLE_MEMBER
                )
                cursor.execute(sql)

                conn.commit()

        except MySQLdb.Error, e:
            # 如果出错就输出错误消息
            print('MySQL Error [%d]: %s' %(e.args[0], e.args[1]))

        finally:
            cursor.close()
            conn.close()

    def _execsql(self, sql, *arg):
        """ 执行SQL语句
        Args:
            sql: 语句
            *arg: list格式的参数

        Returns:
            result: 如果是查询语句就返回查询结果的字典
        """

        result = {}

        try:
            conn = MySQLdb.connect(cursorclass=MySQLdb.cursors.DictCursor,
                    **self.DB_INFO)
            with conn:
                conn.select_db(self.DB_NAME)
                cursor = conn.cursor()

                print('SQL: %s\nArgs: %s' % (sql, arg)) # for debug

                cursor.execute(sql, arg)
                result = cursor.fetchall()
                conn.commit()
        except MySQLdb.Error, e:
            # 如果出错就输出错误消息
            print('MySQL Error [%d]: %s' %(e.args[0], e.args[1]))
        finally:
            cursor.close()
            conn.close()

        return result

    def _insert_dict(self, table_name, dict_to_insert):
        """ 向数据库插入字典格式的数据
        根据字典格式数据生成对应的SQL
        需注意保持格式一致

        Args:
            table_name: 目标数据表名
            dict_to_insert: 需要插入的字典格式数据
        """

        # 插入的dict里有几项就生成几个“%s, ”
        placeholders = ', '.join(['%s']*len(dict_to_insert))
        columns = ', '.join(dict_to_insert.keys())

        # INSERT INTO pay_log (l_id, u_id, ...) VALUES (%s, %s, ...)
        sql = ('INSERT INTO %s (%s) VALUES (%s)'
                %(table_name,
                columns,
                placeholders))

        self._execsql(sql, *dict_to_insert.values())

    def insert_member(self, member):
        """ 向member表插入数据

        Args:
            member: BMAMember类型的对象

        """

        if member.__dict__.has_key('u_id'):
            member.u_id = 0

        self._insert_dict(self.TABLE_MEMBER, member.serialize())

    def _search(self, table_name, **kwargs):
        """ 查找数据库
        返回一个字典类型结果
        目前还只能用=查找咯

        Args:
            table_name: 目标表名
            **kwargs: 查找条件

        Returns:
            把查找到的记录以字典形式返回
        """

        # SELECT * FROM member WHERE u_id = %s AND sex = %s AND ...
        conditions = []
        for k in kwargs.keys():
            conditions.append('%s = %s' %(k, '%s'))
        where = ' AND '.join(conditions)
        sql = 'SELECT * FROM %s WHERE %s' %(table_name, where)

        return self._execsql(sql, *kwargs.values())

    def search_member(self, member):
        """ 在数据库搜索符合条件的member记录
        如果找到了就把记录转换成一个BMAMember对象
        合并为list返回

        Args:
            member: BMAMember对象的tuple，有效属性就是搜索条件

        Returns:
            搜索结果，一个或多个BMAMember对象的list
        """

        # 搜索结果是一个tuple，里面是一个或多个dict
        dict_results = self._search(self.TABLE_MEMBER, **member.serialize())
        members = []

        for each_result in dict_results:
            member = BMAMember()
            member.deserialize(**each_result)
            members.append(member)

        return members

    def update_member(self, u_id, member):
        """ 更新数据库里的member记录
        创建一个BMAMember对象，里面装上需要更新的数据
        把这些数据更新到u_id对应的记录里

        Args:
            u_id: 目标记录的u_id
            member: BMAMember对象，属性是需要更新的新数据

        SQL:
            UPDATE member SET
              name = 'new name',
              email = 'new@email.com',
              ...
            WHERE
              u_id = 123456
        """

        dict_member = member.serialize()

        sets = []
        for k, v in dict_member.iteritems():
            sets.append('%s = \'%s\'' % (k, v))

        update = ', '.join(sets)
        sql = 'UPDATE %s SET %s WHERE u_id = %s' % (self.TABLE_MEMBER, update,
                u_id)

        self._execsql(sql)
