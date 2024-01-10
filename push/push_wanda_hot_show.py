import requests
import hashlib
import time
from datetime import datetime
import json

'''
爬取万达影院指定影厅今日上映的电影
访问m.wandacinemas.com确认地区影院后将网页链接替换到脚本中的url
'''

# 定义生成check值的函数
def generate_check(url, mx_api, timestamp):
    mx_api_dict = json.loads(mx_api)
    sCode = mx_api_dict.get('sCode', '')
    cCode = mx_api_dict.get('cCode', '')
    sign = 'B3AA12B0145E1982F282BEDD8A3305B89A9811280C0B8CC3A6A60D81022E4903'
    check_string = f"{sCode}{cCode}{sign}{timestamp}{url}"
    md5 = hashlib.md5()
    md5.update(check_string.encode('utf-8'))
    return md5.hexdigest()

url = ''
headers = {
    'MX-API': '{"ver":"7.0.0","sCode":"Wanda","_mi_":"","width":1280,"json":true,"cCode":"1_3","check":"123","ts":678,"heigth":720,"appId":"3"}'
}

# 获取当前时间戳
timestamp = str(int(time.time() * 1000))

# 提取用于生成check值的部分URL
check_url = url.split('.com')[1]

# 生成check值
check_value = generate_check(check_url, headers['MX-API'], timestamp)

# 更新headers中的check值和ts时间戳值
headers['MX-API'] = headers['MX-API'].replace('123', check_value).replace('678', timestamp)

# 请求URL
response = requests.get(url, headers=headers)

# 发送消息到webhook接口
message = ""
if response.status_code == 200:
    data = response.json()
    hotMovie = data.get('data', {}).get('hotMovie', [])

    for movie in hotMovie:
        name = movie.get('nameCN')
        genre_ids = movie.get('genreIds')
        release_date_timestamp = movie.get('releaseDate')

        # 转换时间戳为易读的时间格式
        release_date = datetime.fromtimestamp(release_date_timestamp / 1000).strftime('%Y年%m月%d日')

        movie_info = f"电影名: {name}\n影片类型: {genre_ids}\n首映日期: {release_date}\n------------\n"
        message += movie_info

    # 输出信息到控制台
    print(message)

else:
    print("请求失败")
    message = "请求失败"

# 发送整合的信息到webhook接口并进行错误处理
# 完整的推送url
webhook_url = '' + message
try:
    response = requests.post(webhook_url)
    if response.status_code == 200:
        print("消息发送成功")
    else:
        raise requests.RequestException(f"消息发送失败: {response.status_code}")
except requests.RequestException as e:
    print(f"消息发送异常: {e}")
