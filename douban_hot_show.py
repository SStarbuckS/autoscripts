import requests
import os
import sys
from os import environ, path
from bs4 import BeautifulSoup

'''
爬取豆瓣电影指定地区影院上映的影片
替换url尾部地区
'''

url = "https://movie.douban.com/cinema/nowplaying/beijing"
headers = {
    'Referer': 'https://movie.douban.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5762.223 Safari/537.36'
}

response = requests.get(url, headers=headers)
movie_info = ""

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    nowplaying_div = soup.find("div", id="nowplaying")
    if nowplaying_div:
        movie_list = nowplaying_div.find_all("li", class_="list-item")
        for movie in movie_list:
            data_title = movie.get("data-title")
            data_release = movie.get("data-release")
            data_region = movie.get("data-region")
            data_score = movie.get("data-score")
            data_actors = movie.get("data-actors")
            movie_link = movie.find("a", class_="ticket-btn")['href']
            
            movie_info += f"电影: {data_title} ({data_release})\n"
            movie_info += f"地区: {data_region}\n"
            movie_info += f"评分: {data_score}\n"
            movie_info += f"主演: {data_actors}\n"
            movie_info += f"豆瓣: {movie_link}\n"
            movie_info += "\n"
    else:
        movie_info = "未找到电影列表"
else:
    movie_info = "请求失败"

#加载推送服务
def load_send():
    global send
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/sendNotify.py"):
        try:
            from sendNotify import send
            print("加载通知服务成功！")
        except:
            send=False
            print("加载通知服务失败~")
    else:
        send=False
        print("加载通知服务失败~")
load_send()

send('豆瓣今日热映', movie_info)
