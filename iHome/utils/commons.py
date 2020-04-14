from werkzeug.routing import BaseConverter
from flask import session, g, jsonify
from iHome.utils.response_code import RET, error_map
import functools


# 定义正则转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


def LoginRequired(view_func):
    @functools.wraps(view_func)
    def check_login(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify(errno=RET.SESSIONERR, errmsg=error_map[RET.SESSIONERR])
        else:
            g.user_id = user_id
            return view_func(*args, **kwargs)

    return check_login
