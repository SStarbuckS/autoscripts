import requests
from datetime import datetime
import time

'''
神舟租车顺风车爬虫
'''

class HitchInfoFetcher:
    def __init__(self):
        self.hitch_list = []
        self.printed_hitch_ids = set()

    def fetch_hitch_info(self):
        url = "https://m.zuche.com/api/gw.do?uri=/action/carrctapi/order/hitchList/v1"
        payload = 'data=%7B%22pickupCityId%22%3A%22%22%2C%22returnCityId%22%3A%22%22%2C%22useCarTime%22%3A%22%22%2C%22pageNo%22%3A1%2C%22pageSize%22%3A1500%2C%22source%22%3A2%7D'
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://m.zuche.com',
            'Pragma': 'no-cache',
            'Referer': 'https://m.zuche.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Cookie': ''
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                success, message = self.process_hitch_info(data)
                return success, message
            else:
                message = f"顺风车信息获取失败，状态码: {response.status_code}"
                self.send_webhook_notification(message)
                return False, message
        except requests.RequestException as e:
            message = f"顺风车信息获取失败: 发生异常 {e}"
            self.send_webhook_notification(message)
            return False, message

    def process_hitch_info(self, data):
        if data is None:
            message = "顺风车信息获取失败或为空，请检查"
            self.send_webhook_notification(message)
            return False, message

        if 'content' in data and 'hitchList' in data['content']:
            self.hitch_list = data['content']['hitchList']
            message = f"顺风车信息获取成功！共获取 {len(self.hitch_list)} 条信息"
            return True, message
        else:
            message = "顺风车信息获取成功！但没有获取到任何信息"
            self.send_webhook_notification(message)
            return False, message

    def search_hitch_info(self, keywords, pickup_city):
        result = []
        count = 0
        for item in self.hitch_list:
            for keyword in keywords:
                if keyword in item.get('modelName', ''):
                    if item.get('pickupCityName', '').startswith(pickup_city):
                        hitchId = item.get('hitchId', 'N/A')
                        if hitchId not in self.printed_hitch_ids:
                            modelName = item.get('modelName', 'N/A')
                            realTotalPrice = item.get('realTotalPrice', 'N/A')
                            limitTenancyDay = item.get('limitTenancyDay', 'N/A')
                            pickupCityName = item.get('pickupCityName', 'N/A')
                            returnCityName = item.get('returnCityName', 'N/A')

                            output = f"{hitchId} {modelName} {realTotalPrice}￥ {limitTenancyDay}天 {pickupCityName}>{returnCityName}"
                            result.append(output)
                            count += 1
                            self.printed_hitch_ids.add(hitchId)

        return count, result

class HitchSearchApp:
    def __init__(self):
        self.fetcher = HitchInfoFetcher()

    def run(self):
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("\r")
            print(f"执行时间: {current_time}")

            success, message = self.fetcher.fetch_hitch_info()
            print(message)  # 打印获取信息条数的消息

            if success:
                keywords = ["奥迪", "特斯拉", "奔驰", "宝马", "小鹏", "理想", "大众CC", "英菲尼迪", "沃尔沃", "凯迪拉克"]
                pickup_city = "北京", "上海"
                count, search_results = self.fetcher.search_hitch_info(keywords, pickup_city)
                self.print_search_results(count, search_results)
            else:
                print("顺风车信息获取失败，请检查网络或配置")

            time.sleep(60)

    def print_search_results(self, count, results):
        if results:
            output = "\n".join(results)
            print(output)
            for _ in range(10):  # 强推送提醒
              self.send_webhook_notification(output)
        else:
            print("未找到包含任何关键字的顺风车信息")

        print(f"总共找到 {count} 条包含关键字的顺风车信息")

    def send_webhook_notification(self, message):
        webhook_url = "webhook_url"
        params = {
            'title': '神舟租车',
            'msg': message
        }

        try:
            response = requests.post(webhook_url, params=params)
            if response.status_code == 200:
                print("Webhook通知发送成功")
            else:
                print(f"Webhook通知发送失败: HTTP状态码 {response.status_code}")
        except requests.RequestException as e:
            print(f"Webhook通知发送失败: 发生异常 {e}")

if __name__ == "__main__":
    app = HitchSearchApp()
    app.run()
