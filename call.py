import time
import requests
from call_token import TOKEN
from multiprocessing import Process
def _wake_up_call(msg):
    def notify():
        headers = {
            "Authorization": "key=AAAASwElybY:APA91bFaTT_zKLcLYqB0soW8PJmFFG7x1F3wiR0MGta9lLsU22uAVa0VD_3zzz-OremJKDEWEf52OD554byamcwAmZldgrQKfwAjjbhZz_5DYT-z1gcflUBFSWVQQ9lSE9KwDBNHULvfVKmQwxa7xNwuPHz-VfdTbw"
            
        }

        r = requests.post('https://fcm.googleapis.com/fcm/send' ,json = {
            "to": TOKEN,
            "time_to_live": 60,
            "priority": "high",
            "data": {
                "link": {
                    "title": msg,
                    "url": "https://mall.bilibili.com/mall-dayu/neul/shareticket?page=ticket_detail&id=73710&from=itemshare&noTitleBar=1&share_source=&share_medium=android&bbid=05D6BDA4-F658-C8E9-CB15-92C6F7A2CEB139279infoc&ts=1688797845801"
                }
            }
        },
        headers=headers)

    for i in range(10):
        notify()
        time.sleep(1)

def wake_up_call(msg):
    Process(target=_wake_up_call, args=(msg,)).start()

