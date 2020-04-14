from qiniu import Auth, put_data, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = '_k1OYVrwNoF0ALCVhmlVv89pDSbIJD5GzPlXXzej'
secret_key = 'UysGleEpeyUrIdgYAifuxKyZj9qhlzqNOgWGAdeY'
# 构建鉴权对象
q = Auth(access_key, secret_key)
# 要上传的空间
bucket_name = 'ihome-czl'


def upload_image(image_data):
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    ret, info = put_data(token, None, image_data)
    if info.status_code == 200:
        return ret.get("key")
    else:
        raise Exception("上传七牛失败!")
