from datetime import datetime
import hashlib, base64, json, urllib
from iHome.utils.xml2json import Xml2Json


class REST(object):
    def __init__(self, ServerIP, ServerPort, SoftVersion):
        self.ServerIP = ServerIP
        self.ServerPort = ServerPort
        self.SoftVersion = SoftVersion
        self.BodyType = 'json'

    # 设置主帐号
    # @param AccountSid  必选参数    主帐号
    # @param AccountToken  必选参数    主帐号Token
    def setAccount(self, AccountSid, AccountToken):
        self.AccountSid = AccountSid
        self.AccountToken = AccountToken

    def setAppId(self, AppId):
        self.AppId = AppId;

    # 发送模板短信
    # @param to  必选参数     短信接收彿手机号码集合,用英文逗号分开
    # @param datas 可选参数    内容数据
    # @param tempId 必选参数    模板Id
    def sendTemplateSMS(self, to, datas, tempId):
        nowdate = datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        # 生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = hashlib.md5(signature.encode("latin1")).hexdigest().upper()
        # 拼接URL
        url = "https://" + self.ServerIP + ":" + self.ServerPort + "/" + self.SoftVersion + "/Accounts/" + self.AccountSid + "/SMS/TemplateSMS?sig=" + sig
        # 生成auth
        src = self.AccountSid + ":" + self.Batch;
        auth = base64.encodebytes(src.encode(encoding='utf-8')).strip()
        req = urllib.request.Request(url)
        self.setHttpHeader(req)
        req.add_header("Authorization", auth)
        # 创建包体
        b = ''
        for a in datas:
            b += '<data>%s</data>' % (a)

        body = '<?xml version="1.0" encoding="utf-8"?><SubAccount><datas>' + b + '</datas><to>%s</to><templateId>%s</templateId><appId>%s</appId>\
               </SubAccount>\
               ' % (to, tempId, self.AppId)
        if self.BodyType == 'json':
            # if this model is Json ..then do next code
            b = '['
            for a in datas:
                b += '"%s",' % (a)
            b += ']'
            body = '''{"to": "%s", "datas": %s, "templateId": "%s", "appId": "%s"}''' % (to, b, tempId, self.AppId)
        req.add_data(body)
        data = ''
        try:
            res = urllib.urlopen(req);
            data = res.read()
            res.close()

            if self.BodyType == 'json':
                locations = json.loads(data)
            else:
                locations = str(Xml2Json(data).result)
            if self.Iflog:
                self.log(url, body, data)
            return locations
        except Exception as e:
            if self.Iflog:
                self.log(url, body, data)
            return {'172001': '网络错误'}

    # 设置包头
    def setHttpHeader(self, req):
        if self.BodyType == 'json':
            req.add_header("Accept", "application/json")
            req.add_header("Content-Type", "application/json;charset=utf-8")
        else:
            req.add_header("Accept", "application/xml")
            req.add_header("Content-Type", "application/xml;charset=utf-8")