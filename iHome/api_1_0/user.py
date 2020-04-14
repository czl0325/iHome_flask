from . import api
from flask import request, jsonify, session, current_app, make_response, g
from iHome.utils.response_code import RET, error_map
from iHome.models import User
from iHome import db, redis_store
from sqlalchemy.exc import IntegrityError
import re
from werkzeug.security import check_password_hash
from iHome.utils.commons import LoginRequired


@api.route("/user/register", methods=["POST"])
def register():
    mobile = request.form.get("mobile")
    phoneCode = request.form.get("phoneCode")
    password = request.form.get("password")
    password2 = request.form.get("password2")

    if not all([mobile, phoneCode, password, password2]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if not re.match(r"1[34578]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg=error_map[RET.NODATA])

    if sms_code != phoneCode:
        return jsonify(errno=RET.DATAERR, errmsg=error_map[RET.DATAERR])

    try:
        user = User(name=mobile, mobile=mobile)
        user.password = password
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAEXIST, errmsg=error_map[RET.DATAEXIST])
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    session["name"] = user.mobile
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


@api.route("/user/login", methods=["POST"])
def login():
    mobile = request.form.get("mobile")
    password = request.form.get("password")

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    user = User.query.filter_by(mobile=mobile).first()

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="查无此用户")

    if not check_password_hash(user.password_hash, password):
        return jsonify(errno=RET.DATAERR, errmsg="密码错误")

    session["name"] = user.mobile
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    resp = make_response(jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_user_dict()))
    resp.headers["Content-Type"] = "application/json"
    resp.set_cookie("name", user.mobile)
    resp.set_cookie("mobile", user.mobile)
    resp.set_cookie("user_id", str(user.id))
    if user.avatar_url is not None:
        resp.set_cookie("avatar_url", user.avatar_url)
    if user.real_name is not None:
        resp.set_cookie("real_name", user.real_name)
    if user.id_card is not None:
        resp.set_cookie("real_name", user.id_card)
    return resp


@api.route("/user/<int:uid>", methods=["GET"])
def getUserById(uid):
    try:
        user = User.query.get(uid)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="没有该用户")

    resp = make_response(jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=user.to_user_dict()))
    resp.headers["Content-Type"] = "application/json"
    resp.set_cookie("name", user.mobile)
    resp.set_cookie("mobile", user.mobile)
    resp.set_cookie("user_id", str(user.id))
    if user.avatar_url is not None:
        resp.set_cookie("avatar_url", user.avatar_url)
    if user.real_name is not None:
        resp.set_cookie("real_name", user.real_name)
    if user.id_card is not None:
        resp.set_cookie("real_name", user.id_card)
    return resp


# 实名认证接口
@api.route("/user/auth", methods=["POST"])
@LoginRequired
def user_auth():
    real_name = request.form.get("real_name")
    id_card = request.form.get("id_card")
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    user_id = g.user_id
    try:
        User.query.filter_by(id=user_id).update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败，请稍后重试")
    resp = make_response(jsonify(errno=RET.OK, errmsg=error_map[RET.OK]))
    resp.headers["Content-Type"] = "application/json"
    resp.set_cookie("real_name", real_name)
    resp.set_cookie("id_card", id_card)
    return resp
