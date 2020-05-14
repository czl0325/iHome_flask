from flask import request, g, jsonify, current_app
from iHome import db, redis_store
from iHome.api_1_0 import api
from iHome.utils.commons import LoginRequired
from iHome.utils.response_code import RET, error_map
from iHome.models import House, Order, User
from datetime import datetime


@api.route("/order/save", methods=["POST"])
@LoginRequired
def save_order():
    user_id = g.user_id
    house_id = request.form.get("house_id")
    start_date_str = request.form.get("start_date")
    end_date_str = request.form.get("end_date")

    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if house is None:
        return jsonify(errno=RET.DBERR, errmsg="查无此房屋")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        assert start_date <= end_date
        # 计算预订的天数
        days = (end_date - start_date).days + 1  # datetime.timedelta
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期错误")

    if user_id == house.user_id:
        return jsonify(errno=RET.PARAMERR, errmsg="不能预订自己的房子")

    try:
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date,
                                   Order.end_date >= start_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="房屋已被预订")

    # 订单总额
    amount = days * house.price

    order = Order(
        house_id=house_id,
        user_id=user_id,
        begin_date=start_date,
        end_date=end_date,
        days=days,
        house_price=house.price,
        amount=amount
    )

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存订单失败")

    return jsonify(errno=RET.OK, errmsg="OK", data={"order_id": order.id})


@api.route("/order/<int:order_id>/status", methods=["PUT"])
@LoginRequired
def set_order_status(order_id):
    """接单、拒单"""
    user_id = g.user_id

    action = request.form.get("action")

    if action not in ["accept", "reject"]:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="查无此订单")

    if not order:
        return jsonify(errno=RET.DATAERR, errmsg="订单信息有误")
    # 确保房东只能修改属于自己房子的订单
    if user_id != house.user_id:
        return jsonify(errno=RET.REQERR, errmsg="只有房东才能进行此操作")

    if action == "accept":
        # 接单，将订单状态设置为等待评论
        order.status = "WAIT_PAYMENT"
    elif action == "reject":
        # 拒单，要求用户传递拒单原因
        reason = request.form.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="拒单原因必填")
        order.status = "REJECTED"
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])