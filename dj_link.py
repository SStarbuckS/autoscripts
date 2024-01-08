import requests
import re
import json
from urllib.parse import urlparse

"""
提取东京优惠券api
"""

url = input("请输入URL: ")  # 用户输入URL

parsed_url = urlparse(url)
host = parsed_url.netloc  # 提取URL中的Host部分

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
    'Host': host,
}

response = requests.get(url, headers=headers)
response.encoding = response.apparent_encoding  # 尝试自动识别编码
html = response.text

regex = r'window\.__api_data__\s*=\s*({[^;]+});'  # 匹配 window.__api_data__ = {...};
match = re.search(regex, html)

if match and match.group(1):
    json_data = match.group(1)
    try:
        api_data = json.loads(json_data)
        if api_data and 'floorList' in api_data:
            for floor in api_data['floorList']:
                if 'couponList' in floor:
                    for coupon in floor['couponList']:
                        print('beginTimeStr:', coupon.get('beginTimeStr'))
                        print('limit:', coupon.get('limit'))
                        print('args:', coupon.get('args'))
                        print('encodeActivityId:', api_data.get('encodeActivityId'))
                        print('scene:', coupon.get('scene'))
                        print('-------------')
                        # 在这里进行你需要的处理
    except json.JSONDecodeError as e:
        print('JSON 解析错误：', e)
    else:
        print('没有找到符合条件的 JSON 数据。')
