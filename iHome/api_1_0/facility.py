from . import api
from flask import request, jsonify, session, current_app, make_response, g
from iHome.models import Facility
from iHome.utils.response_code import RET, error_map


@api.route("/facility", methods=["GET"])
def get_facility_list():
    try:
        facilities = Facility.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    facility_list = [facility.to_dict() for facility in facilities]
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=facility_list)

# INSERT INTO `ih_facility_info`(`name`) VALUES('无线网络'),('热水淋浴'),('空调'),('暖气'),('允许吸烟'),('饮水设备'),('牙具'),('香皂'),('拖鞋'),('手纸'),('毛巾'),('沐浴露、洗发露'),('冰箱'),('洗衣机'),('电梯'),('允许做饭'),('允许带宠物'),('允许聚会'),('门禁系统'),('停车位'),('有线网络'),('电视'),('浴缸');
