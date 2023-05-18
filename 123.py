import requests
import json
import datetime
import time

def send_post_request(url, payload, headers):
    response = requests.post(url, headers=headers, data=payload)
    return response.text

def run_script(request_count, delay_time):
    url = ""

    payload = json.dumps({
      
    })
    headers = {
      
    }
    
    current_time = datetime.datetime.now()
    scheduled_time = input("请输入脚本的执行时间（格式为HH:MM:SS）：")
    
    scheduled_datetime = datetime.datetime.combine(current_time.date(), datetime.datetime.strptime(scheduled_time, '%H:%M:%S').time())
    time_diff = (scheduled_datetime - current_time).total_seconds()
    
    if time_diff > 0:
        print(f"等待 {time_diff:.0f} 秒后开始执行脚本...")
        while time_diff > 0:
            minutes, seconds = divmod(int(time_diff), 60)
            print(f"\r剩余时间：{minutes:02d}:{seconds:02d}", end="")
            time.sleep(1)
            current_time = datetime.datetime.now()
            time_diff = (scheduled_datetime - current_time).total_seconds()
        print("\n开始执行脚本...")
    else:
        print("指定的执行时间已过，立即开始执行脚本")
    
    for i in range(request_count):
        start_time = time.time()  # 记录请求开始时间
        response_text = send_post_request(url, payload, headers)
        end_time = time.time()  # 记录请求结束时间
        
        # 输出日志
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log = f"[{current_datetime}] - 请求 {i+1}/{request_count} - 响应时间：{end_time - start_time:.3f}秒 - 响应内容：{response_text}"
        print(log)
        
        time.sleep(delay_time / 1000)  # 延迟指定时间（毫秒转换为秒）

# 主程序入口
if __name__ == "__main__":
    request_count = int(input("请输入要发送的请求次数："))
    delay_time = float(input("请输入每个请求之间的延迟时间（毫秒）："))
    
    run_script(request_count, delay_time)
