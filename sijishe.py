import requests
from lxml import etree

# 设置代理
proxy = {
    'http': 'http://127.0.0.1:1080',
    'https': 'http://127.0.0.1:1080'
}

qdurl = 'https://xsijishe.com/plugin.php?id=k_misign:sign&operation=qiandao&formhash=3c7b9ffb&format=empty'
htmlurl = 'https://xsijishe.com/k_misign-sign.html'

# 设置 User-Agent 和 Cookie
headers = {
    'User-Agent': '123',
    'Cookie': '123'
}

def extract_value(html, xpath_expression):
    tree = etree.HTML(html)
    value = tree.xpath(xpath_expression)
    if value:
        return value[0]
    else:
        return None

try:
    # 先访问 qdurl，检查响应状态码
    response_qdurl = requests.get(qdurl, proxies=proxy, headers=headers)
    if response_qdurl.status_code == 200:
        print("成功访问签到页面")
        
        # 访问 htmlurl
        response_html = requests.get(htmlurl, proxies=proxy, headers=headers)
        if response_html.status_code == 200:
            print("成功访问签到数据页面")
            
            # 提取并输出各个元素的值
            elements_translation = {
                'qiandaobtnnum': '签到排名',
                'lxdays': '连续签到天数',
                'lxlevel': '签到等级',
                'lxreward': '积分奖励',
                'lxtdays': '签到总天数'
            }

            log_info = "日志信息：\n"
            for element_id, translation in elements_translation.items():
                value = extract_value(response_html.text, f'//input[@id="{element_id}"]/@value')
                if value is not None:
                    log_info += f"{translation}：{value}\n"
                    print(f"{translation}：{value}")
                else:
                    log_info += f"未找到 {translation} 元素\n"
                    print(f"未找到 {translation} 元素")

            # 推送到 Webhook
            webhook_url = '' + log_info
            webhook_response = requests.get(webhook_url)
            if webhook_response.status_code == 200:
                print("信息已成功推送到 Webhook")
            else:
                print("推送到 Webhook 失败")

        else:
            print("无法访问签到数据页面")

    else:
        print("无法访问签到页面")

except requests.RequestException as e:
    print("请求发生异常:", e)
