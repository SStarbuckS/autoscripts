import os
import time
from telethon import TelegramClient, events

api_id = [12345678,23456789]
#你的TG App api_id 用，分开
api_hash = ['abcdefghigklmnopqrstuvwxyz0123', 'abcdefghigklmnopqrstuvwxyz0123']
#你的App api_hash放在''内用,分开
# 创建一个列表，每个元素是一个包含联系人和消息的元组
contacts_and_messages = [
("@Contact1Username", "Message for Contact 1"),
("@Contact2Username", "Message for Contact 2"),
("@Contact3Username", "Message for Contact 3"),
("@Contact4Username", "Message for Contact 4"),
("@Contact5Username", "Message for Contact 5")
]
#前面是机器人的用户名@开头 后面放签到的内容 例如/checkin
# 循环处理每个联系人和消息
for num in range(len(api_id)):
  # 发送消息给联系人
    client = TelegramClient(f"id_{api_id[num]}", api_id[num], api_hash[num])
    client.start()

    for contact, message in contacts_and_messages:
        client.send_message(contact, message)
        time.sleep(5)# 等待机器人回应，根据需要调整等待时间
        client.send_read_acknowledge(contact)# 将机器人回应标记为已读

    print(f"Done! Session name: id_{api_id[num]}")

os._exit(0)
