import requests
from datetime import datetime
import time

'''
线报库推送脚本，推荐已进程守护后台运行
需要自行更改webhook_url推送的目标接口
'''

last_post_id = "0"  # 将 last_post_id 初始化为字符串类型

def extract_info(data):
    global last_post_id

    for item in data:
        post_id_str = item.get('id')  # 以字符串形式获取帖子ID
        post_id = int(post_id_str)  # 将帖子ID转换为整数类型
        if post_id > int(last_post_id):
            title = item.get('title')
            link = item.get('url')
            
            # 从链接的末尾开始查找帖子ID
            post_id_index = link.rfind("=")
            if post_id_index != -1:
                post_id = int(link[post_id_index + 1:])
            
            timestamp = item.get('shijianchuo')

            if link and timestamp:
                # 检查链接中是否包含关键词（不区分大小写）
                if "weibo" in link.lower() or "douban-gouzu" in link.lower() or "douban-maolife" in link.lower() or "douban-maobathtub" in link.lower():
                    continue

                full_link = 'http://new.xianbao.fun' + link
                datetime_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                print("标题:", title)
                print("链接:", full_link)
                print("时间:", datetime_str)
                print("帖子ID:", post_id)
                print()

                # 构建推送消息内容
                push_content = f"标题: {title}\n链接: {full_link}\n时间: {datetime_str}"

                # 发送推送请求
                push_url = f"webhook_url{push_content}"
                response = requests.get(push_url)
                if response.status_code == 200:
                    print("推送成功")
                else:
                    print("推送失败")

                # 检查标题是否包含指定关键词（不区分大小写）
                keywords_to_check = ["大毛", "bug", "茅台", "神卡", "免费", "大水", "洪水", "火速", "神价", "红包", "快来", "又有", "又来", "牛来", "速度", "大肉"]
                contains_keywords = any(keyword.lower() in title.lower() for keyword in keywords_to_check)

                if contains_keywords:
                    # 如果标题包含指定关键词，构建额外推送消息内容并发送到新的webhook
                    extra_push_content = f"标题: {title}\n时间: {datetime_str}"
                    extra_push_url = f"webhook_url{extra_push_content}"
                    extra_response = requests.post(extra_push_url)
                    print("推送内容:", extra_push_url)
                    if extra_response.status_code == 200:
                        print("额外推送成功")
                    else:
                        print("额外推送失败")
                        
                # 检查标题是否包含指定关键词（不区分大小写）
                keywords_to_check = ["罗技", "gpw", "戴森", "0撸", "bug"]
                contains_keywords = any(keyword.lower() in title.lower() for keyword in keywords_to_check)

                if contains_keywords:
                    # 如果标题包含指定关键词，构建额外推送消息内容并发送到新的webhook
                    extra_push_content = f"标题: {title}\n链接: {full_link}\n时间: {datetime_str}"
                    extra_push_url = f"webhook_url{extra_push_content}"
                    extra_response = requests.post(extra_push_url)
                    print("推送内容:", extra_push_url)
                    if extra_response.status_code == 200:
                        print("额外tg推送成功")
                    else:
                        print("额外tg推送失败")

            last_post_id = post_id_str  # 更新 last_post_id 为字符串形式的帖子ID

def check_new_posts():
    url = "http://new.xianbao.fun/plus/json/push.json"

    headers = {
        'Referer': 'http://new.xianbao.fun/plus/json/push.json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 11.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5782.203 Safari/537.36'
    }

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=16)
            if response.status_code == 200:
                data = response.json()
                if data:
                    extract_info(data)
        except requests.exceptions.Timeout:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "请求超时")
        except requests.exceptions.RequestException as e:
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "请求发生异常:", e)

        time.sleep(6)

check_new_posts()
