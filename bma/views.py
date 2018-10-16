#!usr/bin/python
# -*- coding: utf-8 -*-

from . import bmagym

import json
from flask import request

from classes.bmadb import BMAdb
from classes.bmamember import BMAMember

@bmagym.route('/api/member/search', methods=['GET'])
def search():
    """ 查找会员API
    返回json格式数据

    """

    member_to_search = BMAMember()
    member_to_search.deserialize(**request.args)
    db_search = BMAdb()
    result_members = db_search.search_member(member_to_search)
    result_list = []
    for each_member in result_members:
        result_list.append(each_member.serialize())

    return json.dumps(result_list)

@bmagym.route('/api/member/', methods=['POST'])
def member():
    """ 插入/更新会员数据
    只接受POST过来的json数据
    如果u_id已存在就更新
    如果不存在就检查昵称是否重复，不重复就新建一条
    """

    content = request.get_json()

    if content:
        db_member = BMAdb()

        content_list = []

        if isinstance(content, dict):
            content_list.append(content)
        elif isinstance(content, list):
            content_list = content
        else:
            return 'post failed: unknown data type'

        for each_dict in content_list:
            each_member = BMAMember()
            each_member.deserialize(**each_dict)

        # 操作之前先看看nickname是否与已有记录重复
        if each_member.nickname:
            check_nickname = BMAMember(nickname=each_member.nickname)
            check_nickname_result = db_member.search_member(check_nickname)

            # 如果查找到有重复
            if check_nickname_result:
                # 如果(nickname重复)且(u_id不重复)就报错
                if (check_nickname_result[0].u_id != each_member.u_id):
                    return 'duplicated nickname'

        # 已经排除了nickname重复的问题

        # 如果传过来的数据带u_id参数
        if each_member.u_id:
            each_member_search = BMAMember(u_id=each_member.u_id)
            search_result = db_member.search_member(each_member_search)

            # 如果找到相同u_id的记录就更新
            if search_result:
                print('Updating')
                db_member.update_member(search_result[0].u_id, each_member)
            else:
                return 'no such u_id found'
        else:
            # 没带u_id参数，准备做插入操作
            # u_id不重复，nickname也不重复，插入一条新记录
            print('Inserting')
            db_member.insert_member(each_member)

        return 'success'
    else:
        return 'post failed: not json data'
