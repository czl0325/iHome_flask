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
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date, Order.end_date >= start_date).count()
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
