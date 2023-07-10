# -*- coding: UTF-8 -*-
"""
API
"""
import json
import os
import time
import re
from time import sleep
from urllib import request
from urllib.request import Request as Reqtype
from urllib.parse import urlencode
from geetest import dealCode
import requests
import traceback
from call import wake_up_call

class Api:
    """
    API操作
    """
    def __init__(self,proxies=None,specificID=None,sleepTime=0.15,initial_longSleep=10):
        self.proxies=proxies
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Referer":"https://show.bilibili.com/",
            "Cache-Control":"max-age=0",
            "Upgrade-Insecure-Requests":"1",
            "Sec-Fetch-Site":"same-origin",
            "Sec-Fetch-Mode":"navigate",
            "Sec-Fetch-User":"?1",
            "Sec-Fetch-Dest":"document",
            "Cookie":"a=b;",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "",
            "Connection": "keep-alive"
        }
        self.sleepTime = sleepTime
        self.initial_longSleep = initial_longSleep
        self.user_data = {}
        self.user_data["specificID"] = specificID
        self.user_data["username"] = ""
        self.user_data["project_id"] = ""
        # ALL_USER_DATA_LIST = [""]

    def load_cookie(self):
        if not os.path.exists("user_data.json"):
            t =  open("user_data.json","w")
            t.write("{}")
            t.close
        with open("user_data.json","r") as r:
            try:
                j = json.load(r)
            except:
                r.close()
                print("请重新使用login登录一次bilibili")
                t =  open("user_data.json","w")
                t.write("{}")
                t.close()
                self.error_handle("")
            if not len(j):
                print("请先使用login登录一次bilibili")
                t =  open("user_data.json","w")
                t.write("{}")
                t.close()
                self.error_handle("")
            if self.user_data["specificID"]:
                self.user_data["username"],self.headers["Cookie"] = j[self.user_data["specificID"]][0],j[self.user_data["specificID"]][1]
            else:
                j = j[list(j.keys())[0]]
                self.user_data["username"],self.headers["Cookie"] = j[0],j[1]

    def _http(self,url,j=False,data=None,raw=False):
        data = data.encode() if type(data) == type("") else data
        longSleep = self.initial_longSleep
        while True:
            try:
                if self.proxies and data:
                    opener = request.build_opener(request.ProxyHandler({'http':self.proxies,'https':self.proxies}))
                    res = opener.open(Reqtype(url,headers=self.headers,method="POST",data=data),timeout=120)
                elif self.proxies and not data:
                    opener = request.build_opener(request.ProxyHandler({'http':self.proxies,'https':self.proxies}))
                    res = opener.open(Reqtype(url,headers=self.headers,method="GET"),timeout=120)
                elif data and not self.proxies:
                    res = request.urlopen(Reqtype(url,headers=self.headers,method="POST",data=data),timeout=120)
                else:
                    res = request.urlopen(Reqtype(url,headers=self.headers,method="GET"),timeout=120)

                if res.code != 200:
                    raise Exception("ip可能被风控，请求地址: ",url)
                if j:
                    return json.loads(res.read().decode("utf-8","ignore"))
                elif raw:
                    return res
                else:
                    return res.read().decode("utf-8","ignore")
            except Exception as e:
                traceback.print_exc()
                wake_up_call("出bug了！")
                print(f"休息 {longSleep} 秒")
                time.sleep(longSleep)
                longSleep *= 2

        

    def orderInfo(self):
        # 获取目标
        self.user_data["project_id"] = re.search(r"id=\d+",self.menu("GET_SHOW")).group().split("=")[1]
        # print(self.user_data["project_id"])
        # exit(0)
        # 获取订单信息
        url = "https://show.bilibili.com/api/ticket/project/get?version=134&id=" + self.user_data["project_id"] + "&project_id="+ self.user_data["project_id"]
        data = self._http(url,True)
        if not data["data"]:
            print(data)
            return 1
        # print(self.menu("GET_ORDER_IF",data["data"]))
        self.setAuthType(data)
        self.user_data["screen_id"],self.user_data["sku_id"],self.user_data["pay_money"] = self.menu("GET_ORDER_IF",data["data"])
        # exit(0)
        # exit(0)
        # self.user_data["screen_id"],self.user_data["sku_id"],self.user_data["pay_money"] = data["data"]["screen_list"][CHOOSE_DAY-1]["id"]
        # self.user_data["screen_id"] = "131890"
        # sku_id = data["data"]["screen_list"][CHOOSE_DAY-1]["ticket_list"][CHOOSE_PRICE_LEVEL-1]["id"]
        # self.user_data["sku_id"] = "391732"
        # pay_money = int(data["data"]["screen_list"][config["screen_id"]]["ticket_list"][config["sku_id"]]["price"])
        # self.user_data["pay_money"] = "10000"
        # self.user_data["user_count"] = "1"

        # print("订单信息获取成功")
    
    def setAuthType(self,data):
        if not data:
            self.error_handle("项目不存在")
        self.user_data["auth_type"] = ""
        for i in data["data"]["performance_desc"]["list"][1]["details"]:
            if i["title"] == "实名认证":
                if "一单一证" in i["content"]:
                    self.user_data["auth_type"] = 1
                elif "一人一证" in i["content"]:
                    self.user_data["auth_type"] = 2
        if not self.user_data["auth_type"]:
            self.user_data["auth_type"] = 0

    def buyerinfo(self):
        if self.user_data["auth_type"] == 0:
            self.user_data["buyer_name"], self.user_data["buyer_phone"] = self.menu("GET_NORMAL_INFO")
            self.user_data["user_count"] = self.menu("GET_T_COUNT")
            return
        # 获取购票人
        url = "https://show.bilibili.com/api/ticket/buyer/list?is_default&projectId=" + self.user_data["project_id"]
        data = self._http(url,True)

        self.user_data["buyer"] = self.menu("GET_ID_INFO", data["data"])
        # print(self.user_data["buyer"])
        # exit(0)
        if self.user_data["auth_type"] == 2:
            self.user_data["user_count"] = len(self.user_data["buyer"])
        else:
            self.user_data["user_count"] = self.menu("GET_T_COUNT")

        for i in range(0, len(self.user_data["buyer"])):
            self.user_data["buyer"][i]["isBuyerInfoVerified"] = "true"
            self.user_data["buyer"][i]["isBuyerValid"] = "true"
        
       
        # self.user_data["buyer"] = data["data"]["list"]
        # print(self.user_data["buyer"])
        # exit()
        # print("购票人信息获取成功")

    def tokenGet(self):
        # 获取token
        url = "https://show.bilibili.com/api/ticket/order/prepare?project_id=" + self.user_data["project_id"]

        payload = "count=" + str(self.user_data["user_count"]) + "&order_type=1&project_id=" + self.user_data["project_id"] + "&screen_id=" + str(self.user_data["screen_id"]) + "&sku_id=" + str(self.user_data["sku_id"]) + "&token="
        # payload = "count=1&order_type=1&project_id=73710&screen_id=134762&sku_id=398405&token="       

        data = self._http(url,True,payload)
        if not data["data"]:
            # self.error_handle("获取token失败")
            print("失败信息: " + data["msg"])
            return 1

        if data["data"]["shield"]["verifyMethod"]:
            with open("url","w") as f:
                print(1)
                f.write(data["data"]["shield"]["naUrl"])
        self.user_data["token"] = data["data"]["token"]
        # print(data)
        # print(self.user_data["user_count"])
        print("\n购买Token获取成功")

    def orderCreate(self):
        # 创建订单
        # url = "https://show.bilibili.com/api/ticket/order/createV2?project_id=" + config["projectId"]
        url = "https://show.bilibili.com/api/ticket/order/createV2?project_id=" + self.user_data["project_id"]

        if self.user_data["auth_type"] == 0:
            payload = {
                "buyer": self.user_data["buyer_name"],
                "tel": self.user_data["buyer_phone"],
                "count": self.user_data["user_count"],
                "deviceId": "",
                "order_type": 1,
                "pay_money": int(self.user_data["pay_money"]) * int(self.user_data["user_count"]),
                "project_id": self.user_data["project_id"],
                "screen_id": self.user_data["screen_id"],
                "sku_id": self.user_data["sku_id"],
                "timestamp": int(round(time.time() * 1000)),
                "token": self.user_data["token"]
            }
        else:
            payload = {
                "buyer_info": self.user_data["buyer"],
                "count": self.user_data["user_count"],
                "deviceId": "",
                "order_type": 1,
                "pay_money": int(self.user_data["pay_money"]) * int(self.user_data["user_count"]),
                "project_id": self.user_data["project_id"],
                "screen_id": self.user_data["screen_id"],
                "sku_id": self.user_data["sku_id"],
                "timestamp": int(round(time.time() * 1000)),
                "token": self.user_data["token"]
            }

        data = self._http(url,True,urlencode(payload).replace("%27true%27","true").replace("%27","%22"))
        if data["errno"] == 0:
            print("已成功抢到票, 请在10分钟内完成支付")
            return 1
        elif data["errno"] == 209002:
            print("未获取到购买人信息")
        elif data["errno"] == 100050:    # Token过期
            print("Token已过期! 正在重新获取")
            self.tokenGet()
        else:
            print("错误信息: ", data)
            # print(data)
        return 0

    def error_handle(self,msg):
        print(msg)
        os.system("pause")
        exit(0)

    def menu(self,mtype,data=None):
        if mtype == "GET_SHOW":
            i = input("请输入购票链接并按回车继续 格式例如 https://show.bilibili.com/platform/detail.html?id=73711\n>>> ").strip()
            if "bilibili" not in i or "id" not in i:
                self.error_handle("网址格式错误")
            return i
        elif mtype == "GET_ORDER_IF":
            print("\n演出名称: " + data["name"])
            print("票务状态: " + data["sale_flag"])
            print("\n请选择场次序号并按回车继续，格式例如 1")
            for i in range(len(data["screen_list"])):
                print(str(i+1) + ":",data["screen_list"][i]["name"])
            date = input("场次序号 >>> ").strip()
            try:
                date = int(date) - 1
                if date not in [i for i in range(len(data["screen_list"]))]:
                    self.error_handle("请输入正确序号")
            except:
                self.error_handle("请输入正确数字")
            print("已选择：", data["screen_list"][date]["name"])
            print("\n请输入票种并按回车继续，格式例如 1")
            for i in range(len(data["screen_list"][date]["ticket_list"])):
                print(str(i+1) + ":",data["screen_list"][date]["ticket_list"][i]["desc"],"-",data["screen_list"][date]["ticket_list"][i]["price"]//100,"RMB")
            choice = input("票种序号 >>> ").strip()
            try:
                choice = int(choice) - 1
                if choice not in [i for i in range(len(data["screen_list"][date]["ticket_list"]))]:
                    self.error_handle("请输入正确序号")
            except:
                self.error_handle("请输入正确数字")
            print("\n已选择：", data["name"],data["screen_list"][date]["name"], data["screen_list"][date]["ticket_list"][choice]["desc"],data["screen_list"][date]["ticket_list"][choice]["price"]//100,"RMB")
            return data["screen_list"][date]["id"],data["screen_list"][date]["ticket_list"][choice]["id"],data["screen_list"][date]["ticket_list"][choice]["price"]
        elif mtype == "GET_ID_INFO":
            if not data:
                self.error_handle("用户信息为空，请登录或先上传身份信息后重试")
            if self.user_data["auth_type"] == 1:
                print("\n此演出为一单一证，只需选择1个购票人，如 1")
                for i in range(len(data["list"])):
                    print(str(i+1) + ":" , "姓名: " + data["list"][i]["name"], "手机号:" , data["list"][i]["tel"], "身份证:", data["list"][i]["personal_id"])
                p = input("购票人序号 >>> ").strip()
                try:
                    t = []
                    print("\n已选择: ",data["list"][int(p)-1]["name"])
                    t.append(data["list"][int(p)-1])
                    return t
                except:
                    self.error_handle("请输入正确序号")
            if self.user_data["auth_type"] == 2:
                print("\n此演出为一人一证，请选择购票人, 全部购票请输入0，其他请输入购票人序号，多个购票请用空格分隔，如 1 2")
                for i in range(len(data["list"])):
                    print(str(i+1) + ":" , "姓名: " + data["list"][i]["name"], "手机号:" , data["list"][i]["tel"], "身份证:", data["list"][i]["personal_id"])
                p = input("购票人序号 >>> ").strip()

                t = []
                if p == "0":
                    print("\n已选择列表中全部购票人")
                    return data["list"]
                elif " " in p:
                    try:
                        print("\n已选择: ",end="")
                        for i in p.split(" "):
                            if i:
                                print(data["list"][int(i)-1]["name"],end=" ")
                                t.append(data["list"][int(i)-1])
                        print("")
                        return t
                    except:
                        self.error_handle("请输入正确序号")
                else:
                    try:
                        print("\n已选择: ",data["list"][int(p)-1]["name"])
                        t.append(data["list"][int(p)-1])
                        return t
                    except:
                        self.error_handle("请输入正确序号")
        
        elif mtype == "GET_NORMAL_INFO":
            print("\n此演出无需身份电话信息，请填写姓名和联系方式后按回车")
            name = input("姓名 >>> ").strip()
            tel = input("电话 >>> ").strip()
            if not re.match(r"^\d{9,14}$",tel):
                self.error_handle("请输入正确格式的电话号码")
            return name, tel

        elif mtype == "GET_T_COUNT":
            print("\n请输入购买数量")
            n = input(">>> ").strip()
            if not re.match(r"^\d{1,2}$",n):
                self.error_handle("请输入正确的数量")
            return n


    def start(self):
        # 加载登录信息
        self.load_cookie()
        # 加载演出信息
        while True:
            try:
                sleep(1.7)
                if not self.orderInfo():
                    break
            except Exception as e:
                pass
        # 加载购买人信息
        self.buyerinfo()
        # 获取购票token
        self.tokenGet()
        # 购票
        i = 0
        while True:
            i = 1+i
            sleep(self.sleepTime)
            print("正在尝试第: %d次抢票"%i)
            # if self.tokenGet():
                # continue
            if self.orderCreate():
                wake_up_call("成功了？")
                input("")
                break

    def test(self):
        pass


if __name__ == '__main__':
    Api("").start()