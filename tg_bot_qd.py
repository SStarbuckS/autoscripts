import os
import time
from telethon import TelegramClient, events

async def send_messages():
    #你的TG App api_id 用，分开
    api_id = [12345678,23456789]
    #你的App api_hash放在''内用,分开
    api_hash = ['abcdefghigklmnopqrstuvwxyz0123', 'abcdefghigklmnopqrstuvwxyz0123']
    # 创建一个列表，每个元素是一个包含联系人和消息的元组
    #前面是机器人的用户名@开头 后面放签到的内容 例如/checkin
    contacts_and_messages = [
        ("@my_bot", "/checkin")
    ]

    for num in range(len(api_id)):
        client = TelegramClient(f"id_{api_id[num]}", api_id[num], api_hash[num])
        await client.start()

        for contact, message in contacts_and_messages:
            sent_message = await client.send_message(contact, message)
            time.sleep(5)# 等待机器人回应，根据需要调整等待时间
            await client.send_read_acknowledge(contact)# 将机器人回应标记为已读

            # 获取最后一条消息并打印
            messages = await client.get_messages(contact, limit=1)
            last_message = messages[0] if messages else None
            if last_message:
                print(f"Last message: {last_message.text}")

        print(f"Done! Session name: id_{api_id[num]}")

    os._exit(0)

async def main():
    await send_messages()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
