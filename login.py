import re
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

os.environ["no_proxy"] = "*.bilibili.com,bilibili.com,*.hdslb.com,*.amap.com"

def deal_cookies(raw):
    cookies = ""
    for i in raw:
        cookies += i["name"] + "=" + i["value"] + "; "
    return cookies

def get_login():
    print("请在网页端登录b站\n")
    if not os.path.exists("user_data.json"):
        t =  open("user_data.json","w")
        t.write("{}")
        t.close
    with open("./user_data.json") as r:
        config = json.load(r)
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.binary_location = '/opt/google/chrome/google-chrome'
    WebDriver = webdriver.Chrome(options=options)
    WebDriver.get("https://show.bilibili.com/")
    WebDriver.find_element(By.CLASS_NAME, "nav-header-register").click()
    while True:
        sleep(0.1)
        if "登录" not in WebDriver.page_source:
            break
    print("登录成功\n")
    cookies = WebDriver.get_cookies()
    
    WebDriver.get("https://account.bilibili.com/account/home")
    username = WebDriver.find_element(By.CLASS_NAME, "home-top-msg-name").text
    userid = re.search(r"/\d{1,15}/",WebDriver.find_element(By.CLASS_NAME, "home-to-space").get_attribute("href")).group()[1:-1]
    config[userid] = [username,deal_cookies(cookies)]

    WebDriver.quit()
    print("cookie已保存\n运行结束\n")
    with open("./user_data.json", "w") as f:
        json.dump(config, f, indent=2)
    input("")

if __name__ == '__main__':
    get_login()