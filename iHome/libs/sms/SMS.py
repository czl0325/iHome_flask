from iHome.libs.sms.REST import REST
import threading

accountSid = '8aaf070870e20ea10171538411603851'
accountToken = '5bd34216014a4a0f9ff73f4e6f2e7574'
appId = '8aaf070870e20ea10171538411b63857'
serverIP = 'app.cloopen.com'
serverPort = '8883'
softVersion = '2013-12-26'


class SMS(object):
    # 单例模式
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(SMS, "_instance"):
            with SMS._instance_lock:
                SMS._instance = SMS(*args, **kwargs)
                SMS._instance.rest = REST(serverIP, serverPort, softVersion)
                SMS._instance.rest.setAccount(accountSid, accountToken)
                SMS._instance.rest.setAppId(appId)
        return SMS._instance

    def send_template_sms(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        status_code = result.get("statusCode")
        if status_code == "000000":
            # 表示发送短信成功
            return 0
        else:
            # 发送失败
            return -1


