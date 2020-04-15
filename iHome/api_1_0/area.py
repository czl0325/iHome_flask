from . import api
from flask import request, jsonify, session, current_app, make_response, g
from iHome.models import Area
from iHome.utils.response_code import RET, error_map


# INSERT INTO `ih_area_info`(`name`) VALUES ('思明区'),('湖里区'),('集美区'),('海沧区'),('同安区'),('翔安区');
@api.route("/area", methods=["GET"])
def get_area_list():
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    area_dicts = [area.to_dict() for area in areas]
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=area_dicts)