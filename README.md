# 脚本来源互联网分享，供学习参考。

* [电信云盘自动签到](https://raw.githubusercontent.com/SStarbuckS/autoscripts/main/189Cloud-Checkin.py)

密码、手机号需要填写文件，默认多账户

* [阿里云盘自动签到](https://raw.githubusercontent.com/SStarbuckS/autoscripts/main/aliDriveCheckIn.py)

环境变量`ali_ck`，填写抓包`refresh_token`值

* [贴吧签到](https://raw.githubusercontent.com/SStarbuckS/autoscripts/main/tieba.py) [@trw131](https://github.com/trw131/TiebaCheckIn)

获取签到时的cookie，填入py文件中 google浏览器，打开相应贴吧，该页面，右键-检查-网络，点击签到按钮，在其中add请求的标头中，复制cookie内容至py文件

获取bduss，填入py文件中 同页面下，右键-检查-应用，找到BDUSS内容，复制至py文件

server酱或其他通知方式设置不表，参考各通知网站api

* [爱奇艺签到](https://raw.githubusercontent.com/SStarbuckS/autoscripts/main/iQIYI.js) [@NobyDa](https://github.com/NobyDa/Script)

JsBox, Node.js用户获取Cookie说明：

方法一手机：开启抓包, 网页登录 `https://m.iqiyi.com/user.html` 返回抓包APP搜索URL关键字 apis/user/info.action 复制请求头中的Cookie字段填入以下脚本变量或环境变量中即可

方法二PC：网页登录 `https://www.iqiyi.com` 按F12控制台执行 console.log(document.cookie) 复制打印的Cookie填入以下脚本变量或环境变量中即可

* [恩山论坛签到](https://raw.githubusercontent.com/SStarbuckS/autoscripts/main/checkIn_EnShan.py) [@BNDou](https://github.com/BNDou/Auto_Check_In)

环境变量`COOKIE_ENSHAN`，网页登录 `https://www.right.com.cn/forum/` 按F12控制台`Network`Cookie值

* [司机社签到](https://raw.githubusercontent.com/SStarbuckS/autoscripts/main/sijishe.py)

填写userid，ua，cookie，webhook值
