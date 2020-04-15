from . import api
from flask import request, jsonify, session, current_app, make_response
from iHome.models import Area, Facility
from iHome.utils.response_code import RET, error_map
from iHome.utils.commons import LoginRequired
from iHome import db


@api.route("/house/info", methods=["GET"])
def get_house_info():
    return jsonify(errno=RET.OK, error_map="成功")


@api.route("/house/create", methods=["POST"])
@LoginRequired
def create_house():
    user_id = g.user_id

    title = request.form.get("title")  # 房屋名称标题
    price = request.form.get("price")  # 房屋单价
    area_id = request.form.get("area_id")  # 房屋所属城区的编号
    address = request.form.get("address")  # 房屋地址
    room_count = request.form.get("room_count")  # 房屋包含的房间数目
    acreage = request.form.get("acreage")  # 房屋面积
    unit = request.form.get("unit")  # 房屋布局（几室几厅)
    capacity = request.form.get("capacity")  # 房屋容纳人数
    beds = request.form.get("beds")  # 房屋卧床数目
    deposit = request.form.get("deposit")  # 押金
    min_days = request.form.get("min_days")  # 最小入住天数
    max_days = request.form.get("max_days")  # 最大入住天数

    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="金额必须是数字")

    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="地区错误")

    if area is None:
        return jsonify(errno=RET.PARAMERR, errmsg="地区错误")

    # 保存房屋信息
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 处理房屋的设施信息
    facility_ids = house_data.get("facility")

    if facility_ids:
        try:
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="保存设施信息失败")

        if facilities:
            house.facilities = facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存房屋信息失败")

    return jsonify(errno=RET.OK, errmsg="保存成功", data={"house_id": house.id})