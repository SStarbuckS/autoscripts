import requests
from lxml import etree

# 设置代理
proxy = {
    'http': 'http://127.0.0.1:1080',
    'https': 'http://127.0.0.1:1080'
}

qdurl = 'https://xsijishe.com/plugin.php?id=k_misign:sign&operation=qiandao&formhash=3c7b9ffb&format=empty'
htmlurl = 'https://xsijishe.com/k_misign-sign.html'
userurl = 'https://xsijishe.com/home.php?mod=space&uid=xxxxx'
webhook_url = ''

# 设置 User-Agent 和 Cookie
headers = {
    'User-Agent': '123',
    'Cookie': '123'
}

def extract_value(html, xpath_expression):
    tree = etree.HTML(html)
    value = tree.xpath(xpath_expression)
    if value:
        return value[0].strip()
    else:
        return None

# 存储日志信息
log_info = []

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

            for element_id, translation in elements_translation.items():
                value = extract_value(response_html.text, f'//input[@id="{element_id}"]/@value')
                if value is not None:
                    log_info.append(f"{translation}：{value}")
                else:
                    print(f"未找到 {translation} 元素")
        else:
            print("无法访问签到数据页面")

        # 访问 userurl
        response_user = requests.get(userurl, proxies=proxy, headers=headers)
        if response_user.status_code == 200:
            print("成功访问用户页面")
            
            # 提取用户名和车票数量
            username = extract_value(response_user.text, '//h2[@class="nex_profile_titles"]/text()')
            ticket_count = extract_value(response_user.text, '(//li/em[text()="车票"]/../text())[last()]')
            
            if username is not None:
                log_info.append(f"用户名：{username}")
            else:
                log_info.append("未找到用户名元素")
            
            if ticket_count is not None:
                log_info.append(f"当前车票数量：{ticket_count}")
            else:
                log_info.append("未找到车票数量元素")
        else:
            log_info.append("无法访问用户页面")

    else:
        log_info.append("无法访问签到页面")

except requests.RequestException as e:
    log_info.append(f"请求发生异常: {e}")

# 控制台输出日志信息
for info in log_info:
    print(info)

# 将日志信息作为文本发送到 webhook 接口
requests.get(webhook_url + '\n'.join(log_info))
