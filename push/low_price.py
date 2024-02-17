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

# 假设这个函数用于发送微信推送消息
def send_notification(title, url, price, expected_price):
    title = "商品低价提醒"
    content = f"商品名称：{title}\n商品链接：{url}\n当前价格：{price} 小于或等于预期价格 {expected_price}！"
    send(title, content)

def fetch_data(search_url, expected_price):
    url = "https://www.gwdang.com/miniprogram/price_trend?from=miniprogram"
    headers = {
        "Host": "www.gwdang.com",
        "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5839.211 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "search_url": search_url
    }

    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        data = response.json()
        dp_info = data.get('dp_info')
        if dp_info:
            title = dp_info.get('title')
            url = dp_info.get('url')
            price = int(dp_info.get('price'))  # 将价格转换为整数以便比较
            print("商品标题:", title)
            print("商品链接:", url)
            print("当前价格:", price)
            print("提醒价格:", expected_price)
            
            if price <= expected_price:
                send_notification(title, url, price, expected_price)
                print("已发送低价预警消息！")
            else:
                print("当前价格未达到预期价格，不发送低价预警消息。")
        else:
            print(f"无法从响应中提取商品标题和价格: {search_url}")
            send('商品低价提醒', '出错了请检查！')
    else:
        print(f"无法获取数据: {search_url}. 状态码:", response.status_code)
        send('商品低价提醒', '出错了请检查！')

def main():
    search_urls = [
        {"url": "https://detail.tmall.com/item.htm?id=123", "expected_price": 20000},
        # 添加更多链接和对应的预期价格
    ]

    for item in search_urls:
        fetch_data(item["url"], item["expected_price"])
        time.sleep(6)  # 添加延迟

if __name__ == "__main__":
    main()
