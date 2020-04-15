from . import api
from flask import request, jsonify, session, current_app, make_response, g
from iHome.models import Area, Facility, House, HouseImage
from iHome.utils.response_code import RET, error_map
from iHome.utils.commons import LoginRequired
from iHome import db
from iHome.utils.image_upload import upload_image
from iHome import constants


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
    try:
        facility_str = request.form.get("facility")
        facility_ids = facility_str.split(",")
    except Exception as e:
        current_app.logger.error(e)

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


@api.route("/house/image", methods=["POST"])
@LoginRequired
def upload_house_image():
    user_id = g.user_id
    image_data = request.files.get("house_image")
    house_id = request.form.get("house_id")

    if not all([image_data, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    try:
        result = upload_image(image_data.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")

    house_image = HouseImage(
        house_id=house_id,
        url=result
    )

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片失败")

    try:
        house = House.query.get(house_id)
        if house.index_image_url is None:
            house.index_image_url = constants.QINIU_URL_PREFIX+result
            db.session.add(house)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="上传成功", data=constants.QINIU_URL_PREFIX+result)