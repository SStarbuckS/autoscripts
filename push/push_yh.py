import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit, parse_qs
import time
import re
from datetime import datetime

'''
论坛新帖推送脚本，推荐已进程守护后台运行
需要自行更改webhook_url推送的目标接口和Cookie
'''

headers = {
    'Host': 'www.yaohuo.me',
    'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5782.203 Safari/537.36',
    'Cookie': ''
}

max_link_id = 0

webhook_url = ''

def crawl_page(url):
    global max_link_id
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            topic_links = soup.find_all('a', class_='topic-link')

            for link in reversed(topic_links):
                href = link.get('href')
                if href and 'html' in href:
                    parsed_url = urlsplit(href)
                    query_params = parse_qs(parsed_url.query)
                    query_params.pop('lpage', None)
                    parsed_url = parsed_url._replace(query=None)
                    full_link = urlunsplit(parsed_url)
                    full_link = 'https://www.yaohuo.me' + full_link
                    text = link.get_text()

                    match = re.search(r'bbs-(\d+).html', href)
                    if match:
                        link_id = int(match.group(1))

                        keywords = ['大毛', 'bug', '茅台', '神卡', '免费', '大水', '洪水', '火速', '神价', '红包', '快来', '又有', '又来', '牛来', '速度', '大肉', '罗技', 'gpw', '戴森', '0撸', '预约', '千兆', '1000m']
                        for keyword in keywords:
                            if re.search(keyword, text, re.IGNORECASE):
                                if link_id > max_link_id:
                                    max_link_id = link_id
                                    print(f'帖子:{text}\n链接:{full_link}')

                                    webhook_msg = f'帖子:{text}\n链接:{full_link}'
                                    webhook_response = requests.post(webhook_url + webhook_msg)
                                    if webhook_response.status_code == 200:
                                        print(f'{datetime.now()}: 成功发送到Webhook')
                                    else:
                                        print(f'{datetime.now()}: 发送到Webhook失败')
        else:
            print(f'{datetime.now()}: 请求失败 - URL: {url}, 状态码: {response.status_code}')
    except requests.RequestException as e:
        print(f'{datetime.now()}: 请求发生异常 - URL: {url}, 异常信息: {str(e)}')

urls = [
    'https://www.yaohuo.me/bbs/book_list.aspx?action=new&siteid=1000&classid=0&getTotal=2023&page=3',
    'https://www.yaohuo.me/bbs/book_list.aspx?action=new&siteid=1000&classid=0&getTotal=2023&page=2',
    'https://www.yaohuo.me/bbs/book_list.aspx?action=new&siteid=1000&classid=0&getTotal=2023&page=1'
]

while True:
    for url in urls:
        crawl_page(url)
        time.sleep(3)

    time.sleep(360)
