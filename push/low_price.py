import requests
import json
import time
import os
import sys

'''
购物网站商品低价推送提醒
需要替换product_and_prices商品链接和预期价格
'''

try:
    from sendNotify import send
except Exception as err:
    print('%s\n加载通知服务失败~' % err)

def get_product_info(product_url, expected_price_str):
    base_url = "https://www.zhelink.com:8028/HistoricallyLowPrice/api/low_price/data?goods="
    full_url = f"{base_url}{product_url}"

    headers = {
        "Host": "www.zhelink.com:8028"
    }

    # 发送 GET 请求
    response = requests.get(full_url, headers=headers)

    # 检查请求是否成功
    if response.status_code == 200:
        # 解析 JSON 数据
        data = response.json()

        # 提取data字段中的JSON字符串
        data_json_str = data.get("data", "")

        # 再次解析JSON字符串
        data_json = json.loads(data_json_str) if data_json_str else {}

        # 提取需要的字段
        current_price = data_json.get("currentPrice")
        sp_name = data_json.get("spName")
        lower_price = data_json.get("lowerPrice")

        # 打印提取的信息（中文）
        print("商品名称:", sp_name)
        print("商品链接:", product_url)
        print("当前价格:", current_price)
        print("史低价格:", lower_price)
        print("提醒价格:", expected_price_str)

        # 比较当前价格和预期价格
        if current_price and float(current_price) <= float(expected_price_str):
            send_notification(sp_name, product_url, current_price, expected_price_str, lower_price)
        
        print("--------------------")
    else:
        print(f"获取 {product_url} 数据失败。状态码:", response.status_code)
        send('商品低价提醒', '出错了请检查！')

def send_notification(sp_name, product_url, current_price, expected_price_str, lower_price):
        title = "商品低价提醒"
        content = f"商品名称：{sp_name}\n商品链接：{product_url}\n当前价格：{current_price} 小于或等于预期价格 {expected_price_str}！\n历史最低价格参考：{lower_price}"
        send(title, content)

# 例子：多个商品链接和预期价格
product_and_prices = [
    {"url": "https://detail.tmall.com/item.htm?id=123", "expected_price": "100.00"},
    # 添加更多商品链接和预期价格...
]

# 遍历商品链接并调用函数，添加延迟
for item in product_and_prices:
    get_product_info(item["url"], item["expected_price"])
    time.sleep(6)  # 延迟6秒
