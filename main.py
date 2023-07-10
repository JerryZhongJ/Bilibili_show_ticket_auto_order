# import sys
import os
from api import Api
from geetest import dealCode
from datetime import datetime
os.environ["no_proxy"] = "*.bilibili.com,bilibili.com,*.hdslb.com,*.amap.com"

if not os.path.exists("config.txt"):
    print("config.txt文件缺失")
    input("")
    exit(0)

a = open("config.txt", "r").readlines()
proxies = None if a[0].split("=")[1].strip(
) == "None" else a[0].split("=")[1].strip()
specificID = None if a[1].split("=")[1].strip(
) == "None" else a[1].split("=")[1].strip()
sleep = eval(a[2].split("=")[1].strip())
initial_longSleep = eval(a[3].split("=")[1].strip())
if __name__ == '__main__':
    if not os.path.exists("url"):
        with open("url", "w") as f:
            f.write("")
    
    logfile = datetime.now().strftime('%y-%m-%d-%H-%M-%S.log')
    with open(logfile, "w") as f:
        f.write("")

    Api(proxies=proxies, 
        specificID=specificID, 
        sleepTime=sleep,
        initial_longSleep=initial_longSleep,
        logfile=logfile).start()
