# iHome_flask
使用flask前后端分离开发爱家租房网


#### 需求库
```
pip install flask
pip install flask_sqlalchemy#使flask数据库有orm的操作
pip install flask_session   #把session保存在redis中
pip install flask_wtf       #为flask添加表单验证服务
pip install flask_script    #为flask添加类似django的runserver命令
pip install flask_migrate   #为flask添加数据库生成命令
pip install xmltodict       #xml转化成dict
pip install qiniu           #七牛图片储存框架
```

- migrate数据库指令
```
$ python manage.py db init
$ python manage.py db migrate -m "v1.0"
$ python manage.py db upgrade
$ python manage.py db --help
``` 

- 数据库名
`ihome`



- !["'utf8' is currently an alias for the character set UTF8MB3, but will be an alias for UTF8MB4 in a future release. Please consider using UTF8MB4 in order to be unambiguous."错误](https://www.cnblogs.com/lilip/p/10109557.html)


- 支付宝沙箱账号
 - quiqxl3314@sandbox.com
 - 111111