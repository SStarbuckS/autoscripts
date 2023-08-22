import re
import requests
import json
import time
from datetime import datetime, timedelta

# 初始化全局变量
global_url = None
global_payload = None
global_headers = None

def read_curl_file(filename):
    with open(filename, 'r') as file:
        curl_command = file.read().strip()
    return curl_command

def processAccounts(curl_filename='cURL.txt'):
    try:
        curl_command = read_curl_file(curl_filename)
        extract_curl_info(curl_command)
    except FileNotFoundError:
        print(f"未找到 cURL 文件 '{curl_filename}'。")
        
# 读取配置文件中的信息并设置为全局变量
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    loop_count = int(config_data.get('loopCount', 1))
    coupon_url = config_data.get('coupon_url', '')
    advance_time_ms = int(config_data.get('advanceTime', 0))
    lead_time_ms = int(config_data.get('leadTime', 0))

# 打印当前系统时间和信息在同一行（包括毫秒）
def print_current_time(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 去掉最后3位毫秒
    print(f"{current_time} - {message}")

# 抢券函数
def grab_coupon():
    global global_url, global_headers, coupon_url

    if coupon_url:
        if global_url and global_headers:
            print_current_time("开始构建GET链接并请求...")
            coupon_id_match = re.search(r'couponReferId=([A-F0-9]+)&', global_url)
            if coupon_id_match:
                coupon_id = coupon_id_match.group(1)
                
                new_url = f"{coupon_url}{coupon_id}"
                start_time = time.time()
                response = requests.get(new_url, headers=global_headers)
                end_time = time.time()
                response_json = response.json()
                response_msg = response_json.get('msg', 'No "msg" field in response')
                elapsed_time_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
                print_current_time(f"GET请求成功，响应时间: {elapsed_time_ms} ms，响应请求: {response_msg}")
                
                # 延迟2秒
                time.sleep(2)
                
                # 单独发送POST请求
                if global_payload:
                    start_time = time.time()
                    response = requests.post(global_url, data=global_payload, headers=global_headers)
                    end_time = time.time()
                    response_json = response.json()
                    response_msg = response_json.get('msg', 'No "msg" field in response')
                    elapsed_time_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
                    print_current_time(f"单独发送POST请求，响应时间: {elapsed_time_ms} ms，响应请求: {response_msg}")
                else:
                    print_current_time("Missing payload for separate POST request")
            else:
                print_current_time("Coupon ID not found in the URL")
        else:
            print_current_time("Missing URL or headers for grabbing coupon")
    else:
        if not hasattr(grab_coupon, "empty_url_warning_shown"):
            print_current_time("coupon_url is empty, skipping coupon grabbing")
            grab_coupon.empty_url_warning_shown = True

# 发包函数
def send_post_request():
    global global_url, global_payload, global_headers
    
    for i in range(loop_count):
        if global_url and global_payload and global_headers:
            start_time = time.time()
            response = requests.post(global_url, data=global_payload, headers=global_headers)
            end_time = time.time()
            response_json = response.json()
            response_msg = response_json.get('msg', 'No "msg" field in response')
            elapsed_time_ms = int((end_time - start_time) * 1000)  # 转换为毫秒
            print_current_time(f"POST请求成功（第 {i+1}/{loop_count} 次），响应时间: {elapsed_time_ms} ms，响应请求: {response_msg}")

            # 检查响应消息中是否包含特定关键词，如果包含则终止程序
            keywords_to_check = ["已领取", "来晚了", "异常", "网络"]
            for keyword in keywords_to_check:
                if keyword in response_msg:
                    print_current_time(f"检测到关键词: '{keyword}'，程序终止。")
                    return
        else:
            print_current_time("Missing URL, payload, or headers")

# 等待特定时间执行脚本的函数
def prompt_execution_time():
    execution_time = input("请输入执行时间（hh:mm:ss）：")
    try:
        execution_time_obj = datetime.strptime(execution_time, '%H:%M:%S').time()
        print(f"execution_time_obj：{execution_time_obj}")
        
        grab_time_obj = (datetime.combine(datetime.today(), execution_time_obj) - timedelta(milliseconds=advance_time_ms)).time()
        post_time_obj = (datetime.combine(datetime.today(), execution_time_obj) - timedelta(milliseconds=lead_time_ms)).time()

        print(f"grab_time_obj：{grab_time_obj}")
        print(f"post_time_obj：{post_time_obj}")
        
        grab_executed = False  # 增加一个标志变量来跟踪是否已执行 grab_coupon()
        while True:
            current_time = datetime.now().time()

            if current_time >= grab_time_obj and not grab_executed:
                grab_coupon()
                grab_executed = True  # 设置标志为 True，表示已经执行过 grab_coupon()

            if current_time >= post_time_obj:
                send_post_request()
                break

            time_until_grab = (datetime.combine(datetime.today(), grab_time_obj) - datetime.combine(datetime.today(), current_time)).total_seconds()
            time_until_post = (datetime.combine(datetime.today(), post_time_obj) - datetime.combine(datetime.today(), current_time)).total_seconds()

            output = f"距离 grab_coupon 执行还有 {int(time_until_grab)} 秒 | 距离 send_post_request 执行还有 {int(time_until_post)} 秒{' ' * 20}"
            print(output, end='\r')

            time.sleep(0.1)
    except ValueError:
        print("时间格式无效，请使用 hh:mm:ss 格式输入时间。")

# 提取执行时间从配置文件中
def extractExecutionTimeFromTextFile():
    try:
        with open('config.json', 'r') as config_file:
            config_data = json.load(config_file)
            execution_time_str = config_data.get('startTime', '00:00:00')
            print(f"已从配置文件中提取执行时间：{execution_time_str}")
            
            execution_time_obj = datetime.strptime(execution_time_str, '%H:%M:%S').time()
            print(f"execution_time_obj：{execution_time_obj}")
        
            grab_time_obj = (datetime.combine(datetime.today(), execution_time_obj) - timedelta(milliseconds=advance_time_ms)).time()
            post_time_obj = (datetime.combine(datetime.today(), execution_time_obj) - timedelta(milliseconds=lead_time_ms)).time()

            print(f"grab_time_obj：{grab_time_obj}")
            print(f"post_time_obj：{post_time_obj}")

            grab_executed = False  # 增加一个标志变量来跟踪是否已执行 grab_coupon()
            while True:
                current_time = datetime.now().time()

                if current_time >= grab_time_obj and not grab_executed:
                    grab_coupon()
                    grab_executed = True  # 设置标志为 True，表示已经执行过 grab_coupon()

                if current_time >= post_time_obj:
                    send_post_request()
                    break

                time_until_grab = (datetime.combine(datetime.today(), grab_time_obj) - datetime.combine(datetime.today(), current_time)).total_seconds()
                time_until_post = (datetime.combine(datetime.today(), post_time_obj) - datetime.combine(datetime.today(), current_time)).total_seconds()

                output = f"距离 grab_coupon 执行还有 {int(time_until_grab)} 秒 | 距离 send_post_request 执行还有 {int(time_until_post)} 秒{' ' * 20}"
                print(output, end='\r')

                time.sleep(0.1)
    except FileNotFoundError:
        print("未找到配置文件 'config.json'。")

# 从cURL提取必备请求参数
def extract_curl_info(curl_command):
    global global_url, global_payload, global_headers

    def extract_url(curl_command):
        url_match = re.search(r"curl '(.*?)'", curl_command)
        if url_match:
            return url_match.group(1)
        else:
            return None

    def extract_payload(curl_command):
        payload_match = re.search(r"--data-raw '(.*?)'", curl_command)
        if payload_match:
            return payload_match.group(1)
        else:
            return None

    def extract_headers(curl_command):
        headers_match = re.findall(r"-H '(.*?)'", curl_command)
        headers = {}
        for header in headers_match:
            header_parts = header.split(': ')
            if len(header_parts) == 2:
                headers[header_parts[0]] = header_parts[1]
        return headers
    
    global_url = extract_url(curl_command)
    global_payload = extract_payload(curl_command)
    global_headers = extract_headers(curl_command)

# 主函数入口
def main():
    processAccounts()
    print("请选择运行模式：")
    print("1. 手动模式")
    print("2. 本地模式")
    mode = input("请输入模式编号（1 或 2）：")

    if mode == '1':
        prompt_execution_time()
    elif mode == '2':
        extractExecutionTimeFromTextFile()
    else:
        print("无效的模式编号。")

if __name__ == "__main__":
    main()
