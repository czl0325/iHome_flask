from . import api
from flask import request, jsonify, session, current_app, make_response, g
from iHome.models import Area, Facility, House, HouseImage, Order
from iHome.utils.response_code import RET, error_map
from iHome.utils.commons import LoginRequired
from iHome import db
from iHome.utils.image_upload import upload_image
from iHome import constants
from datetime import datetime
import json


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
        print(type(house))
        if house.index_image_url is None or house.index_image_url.strip() == '':
            try:
                house.index_image_url = constants.QINIU_URL_PREFIX+result
                db.session.add(house)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                db.session.rollback()
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="上传成功", data=constants.QINIU_URL_PREFIX+result)


@api.route("/house/all", methods=["GET"])
def get_home_houses():
    # todo 使用redis缓存

    try:
        houses = db.session.query(House).order_by(House.create_time.desc()).limit(5).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    house_list = [house.to_base_dict() for house in houses]
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=house_list)


@api.route("/house/search", methods=["GET"])
def search_houses():
    """房屋搜索接口"""
    area_id = request.args.get("aid")
    start_date = request.args.get("sd")
    end_date = request.args.get("ed")
    sort_key = request.args.get("sortKey", "new")
    page_num = request.args.get("p", 1)

    # 处理时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="时间格式错误")

    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")

    try:
        page_num = int(page_num)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="页码参数有误")

    # todo 使用redis缓存

    # 过滤条件的参数列表容器
    filter_params = []

    # 填充过滤参数

    # 找出预订时间有冲突的房子
    conflict_orders = None
    try:
        if start_date and end_date:
            # 查询冲突的订单
            conflict_orders = Order.query.filter(Order.begin_date<=end_date, Order.end_date>=start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date>=start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if conflict_orders:
        # 从订单中获取冲突的房屋id
        conflict_house_ids = [order.house_id for order in conflict_orders]
        # 如果冲突的房屋id不为空，向查询参数中添加条件
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))

    if area_id:
        filter_params.append(House.area_id==area_id)

    if sort_key == "booking":  # 入住做多
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 处理分页
    try:
        page_obj = house_query.paginate(page=page_num, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    # 获取页面数据
    house_list = page_obj.items
    houses = [house.to_base_dict() for house in house_list]
    # 获取总页数
    total_page = page_obj.pages

    # return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=json.dumps({total_page: total_page, houses: houses}))
    response_dict = dict(errno=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "current_page": page_num})
    return response_dict


@api.route("/house/detail", methods=["GET"])
def get_house_detail():
    house_id = request.args.get("id")
    user_id = session.get("user_id", -1)

    if not all(house_id):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # todo 使用redis缓存

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    try:
        house_dict = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据出错")

    house_dict["isMe"] = user_id == house.user_id

    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=house_dict)





