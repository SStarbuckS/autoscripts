import requests
import json
import datetime
import time
import threading
import pytz
import re

qurl = "https://promotion.waimai.meituan.com/lottery/limitcouponcomponent/info?couponReferIds="
# 从cURL命令中提取URL
def extract_url(curl_command):
    url_match = re.search(r"curl '(.*?)'", curl_command)
    if url_match:
        return url_match.group(1)
    else:
        return None

# 从cURL命令中提取请求体
def extract_payload(curl_command):
    payload_match = re.search(r"--data-raw '(.*?)'", curl_command)
    if payload_match:
        return payload_match.group(1)
    else:
        return None

# 从cURL命令中提取请求头
def extract_headers(curl_command):
    headers_match = re.findall(r"-H '(.*?)'", curl_command)
    headers = {}
    for header in headers_match:
        header_parts = header.split(': ')
        if len(header_parts) == 2:
            headers[header_parts[0]] = header_parts[1]
    return headers

# 发送GET请求
def send_get_request(url):
    response = requests.get(url, headers=headers)
    return response.text

# 发送POST请求
def send_post_request(url):
    response = requests.post(url, headers=headers, data=payload)
    return response.text

# 发送请求并输出日志
def send_requests(request_count, delay_time=0):
    for i in range(request_count):
        start_time = time.time()  # 记录请求开始时间
        response_text = send_post_request(url)
        end_time = time.time()  # 记录请求结束时间
        
        # 输出日志
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log = f"[{current_datetime}] - 请求 {i+1}/{request_count} - 响应时间：{end_time - start_time:.3f}秒 - 响应内容：{response_text}"
        print(log)
        
        time.sleep(delay_time / 1000)  # 延迟指定时间（毫秒转换为秒）

# 从'cURL.txt'文件中提取连接格式并更新全局变量
def extract_curl_data(curl_file):
    with open(curl_file, 'r') as file:
        curl_command = file.read().replace('\n', ' ')

    global url, payload, headers
    url = extract_url(curl_command)
    payload = extract_payload(curl_command)
    headers = extract_headers(curl_command)

    # 打印提取的连接格式
    print("URL:", url)
    print("Payload:", payload)
    print("Headers:", headers)

# 主程序入口
def run_script():
    # 提取连接格式并更新全局变量
    curl_file = 'cURL.txt'
    extract_curl_data(curl_file)

    mode = int(input("请选择模式（1 - 抢券模式，2 - 正常模式）："))

    if mode == 1:  # 抢券模式
        # 构建请求的 URL
        coupon_refer_id = re.search(r'couponReferId=(.*?)(&|$)', url).group(1)
        qurl_with_coupon_id = qurl + coupon_refer_id

        # GET请求获取数据
        response_text = send_get_request(qurl_with_coupon_id)
        print(f"GET请求完成 - 响应内容：{response_text}")
        
        print("等待2秒后继续执行...")
        time.sleep(2)  # 添加2秒延迟
        
        # POST请求执行原始请求
        response_text = send_post_request(url)
        print(f"POST请求完成 - 响应内容：{response_text}")

        # 跳转到模式2
        mode = 2

    if mode == 2:  # 正常模式
        mode = int(input("请选择模式（3 - 单线程模式，4 - 多线程模式，5 - 立即执行模式）："))

        if mode == 3:  # 单线程模式
            request_count = int(input("请输入要发送的请求次数："))
            delay_time = float(input("请输入每个请求之间的延迟时间（毫秒）："))

            current_time = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
            scheduled_time = input("请输入脚本的执行时间（格式为HH:MM:SS）：")

            scheduled_datetime = datetime.datetime.strptime(scheduled_time, '%H:%M:%S').time()
            scheduled_datetime = pytz.timezone("Asia/Shanghai").localize(datetime.datetime.combine(current_time.date(), scheduled_datetime))

            time_diff = (scheduled_datetime - current_time).total_seconds()

            if time_diff > 0:
                print(f"等待 {time_diff:.0f} 秒后开始执行脚本...")
                while time_diff > 0:
                    minutes, seconds = divmod(int(time_diff), 60)
                    print(f"\r剩余时间：{minutes:02d}:{seconds:02d}", end="")
                    time.sleep(1)
                    current_time = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
                    time_diff = (scheduled_datetime - current_time).total_seconds()
                print("\n开始执行脚本...")
            else:
                print("指定的执行时间已过，立即开始执行脚本")

            send_requests(request_count, delay_time)

        elif mode == 4:  # 多线程模式
            concurrent_count = int(input("请输入并发请求数："))

            current_time = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
            scheduled_time = input("请输入脚本的执行时间（格式为HH:MM:SS）：")

            scheduled_datetime = datetime.datetime.strptime(scheduled_time, '%H:%M:%S').time()
            scheduled_datetime = pytz.timezone("Asia/Shanghai").localize(datetime.datetime.combine(current_time.date(), scheduled_datetime))

            time_diff = (scheduled_datetime - current_time).total_seconds()

            if time_diff > 0:
                print(f"等待 {time_diff:.0f} 秒后开始执行脚本...")
                while time_diff > 0:
                    minutes, seconds = divmod(int(time_diff), 60)
                    print(f"\r剩余时间：{minutes:02d}:{seconds:02d}", end="")
                    time.sleep(1)
                    current_time = datetime.datetime.now(pytz.timezone("Asia/Shanghai"))
                    time_diff = (scheduled_datetime - current_time).total_seconds()
                print("\n开始执行脚本...")
            else:
                print("指定的执行时间已过，立即开始执行脚本")

            threads = []
            for _ in range(concurrent_count):
                thread = threading.Thread(target=send_requests, args=(1,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        elif mode == 5:  # 立即执行模式
            send_requests(1)

        else:
            print("无效的模式选择！")

    else:
        print("无效的模式选择！")

# 主程序入口
if __name__ == "__main__":
    run_script()
