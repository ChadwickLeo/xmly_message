#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

# @Time    : 2020/11/13 9:44
# @Author  : TNanko
# @File    : xmly_speed.py
# @Software: PyCharm
'''
基于 https://github.com/Zero-S1/xmly_speed 的代码，98%都是相同的，修复一些bug，增加bark选项
'''
import requests
import json
import rsa
import base64
import time
from itertools import groupby
import hashlib
from datetime import datetime, timedelta
import os
import traceback

# 喜马拉雅极速版
# 使用方案2：本地或者vps
cookies1 = ''
cookies2 = ''
cookiesList = [cookies1, cookies2]  # 多账号准备
XMLY_ACCUMULATE_TIME = 0    # 希望刷时长的,此处置1
bark_machine_code = ''  # 填写bark机器码
maximum_duration = 1440
safe_mode = 0  # 默认是不安全模式

# 使用方案1：GitHub action自动运行,此处无需填写;
if "XMLY_SPEED_COOKIE" in os.environ:
    """
    判断是否运行自GitHub action,"XMLY_SPEED_COOKIE" 该参数与 repo里的Secrets的名称保持一致
    """
    print('执行自GitHub action')
    xmly_speed_cookie = os.environ["XMLY_SPEED_COOKIE"]
    bark_machine_code = os.environ["BARK_MACHINE_CODE"]
    cookiesList = []  # 重置cookiesList
    for line in xmly_speed_cookie.split('\n'):
        if not line:
            continue
        cookiesList.append(line)
    # GitHub action运行需要填写对应的secrets
    if "XMLY_ACCUMULATE_TIME" in os.environ and os.environ["XMLY_ACCUMULATE_TIME"] == 'zero_s1':
        XMLY_ACCUMULATE_TIME = 1
        print('action 自动刷时长打开')
    if "SAFE_MODE" in os.environ and os.environ["SAFE_MODE"] == 'true':
        safe_mode = 1
        print('action 打开安全模式')
    try:
        if "MAXIMUM_DURATION" in os.environ and os.environ["MAXIMUM_DURATION"] != '':
            maximum_duration = int(os.environ['MAXIMUM_DURATION'])
        else:
            maximum_duration = 1440
    except:
        maximum_duration = 1440
    print('时长限制：%d' % maximum_duration)

UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 iting/1.0.12 kdtunion_iting/1.0 iting(main)/1.0.12/ios_1"

def str_to_dict(str_cookie):
    if type(str_cookie) == dict:
        return str_cookie
    tmp = str_cookie.split(";")
    dict_cookie = {}
    try:
        for i in tmp:
            j = i.split("=")
            if not j[0]:
                continue
            dict_cookie[j[0].strip()] = j[1].strip()
        print(dict_cookie)
    except:
        print("cookie格式填写错误")
    return dict_cookie

# def get_gtm8_time():
if not cookiesList[0]:
    print("cookie为空 跳出X")
    exit()
mins = int(time.time())
date_stamp = (mins-57600) % 86400
utc_dt = datetime.utcnow()  # UTC时间
bj_dt = utc_dt+timedelta(hours=8)  # 北京时间
_datatime = bj_dt.strftime("%Y%m%d", )
print(f"北京时间: {bj_dt}")
print(_datatime)
print("今日已过秒数: ", date_stamp)
print("当前时间戳", mins)

def read(cookies, uid):
    print("\n【阅读】")
    # global response
    headers = {
        'Host': '51gzdhh.xyz',
        'accept': 'application/json, text/plain, */*',
        'origin': 'http://xiaokuohao.work',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MI 6 Plus Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 iting(main)/1.8.18/android_1 kdtUnion_iting/1.8.18',
        'referer': 'http://xiaokuohao.work/static/web/dxmly/index.html',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,en-US;q=0.8',
        'x-requested-with': 'com.ximalaya.ting.lite',
    }
    params = (
        ('hid', '233'),
    )
    try:
        response = requests.get(
            'https://51gzdhh.xyz/api/new/newConfig', headers=headers, params=params)
        result = response.json()
        print(result)
        pid = str(result["pid"])
        headers = {
            'Host': '51gzdhh.xyz',
            'content-length': '37',
            'accept': 'application/json, text/plain, */*',
            'origin': 'http://xiaokuohao.work',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MI 6 Plus Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 iting(main)/1.8.18/android_1 kdtUnion_iting/1.8.18',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'http://xiaokuohao.work/static/web/dxmly/index.html',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,en-US;q=0.8',
            'x-requested-with': 'com.ximalaya.ting.lite',
        }
        data = {"pid": str(pid), "mtuserid": uid}
        try:
            response = requests.post(
                'https://51gzdhh.xyz/api/new/hui/complete', headers=headers, data=json.dumps(data))
        except:
            print(traceback.format_exc())
        result = response.json()
        print(result)
        if result["status"] == -2:
            print("无法阅读,尝试从安卓端手动开启")
            return
        print(result["completeList"])
        if result["isComplete"]:
            print("今日完成阅读")
            return
        headers = {
            'Host': '51gzdhh.xyz',
            'accept': 'application/json, text/plain, */*',
            'origin': 'http://xiaokuohao.work',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MI 6 Plus Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 iting(main)/1.8.18/android_1 kdtUnion_iting/1.8.18',
            'referer': 'http://xiaokuohao.work/static/web/dxmly/index.html',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,en-US;q=0.8',
            'x-requested-with': 'com.ximalaya.ting.lite',
        }
        taskIds = set(['242', '239', '241', '240', '238', '236', '237', '235', '234'])-set(result["completeList"])
        params = (
            ('userid', str(uid)),
            ('pid', pid),
            ('taskid', taskIds.pop()),
            ('imei', ''),
        )
        try:
            response = requests.get(
                'https://51gzdhh.xyz/new/userCompleteNew', headers=headers, params=params)
            result = response.json()
            print(result)
        except:
            print(traceback.format_exc())
    except:
        print(traceback.format_exc())

def ans_receive(cookies, paperId, lastTopicId, receiveType):
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
    }
    _checkData = f"""lastTopicId={lastTopicId}&numOfAnswers=3&receiveType={receiveType}"""
    checkData = rsa_encrypt(str(_checkData), pubkey_str)
    data = {
        "paperId": paperId,
        "checkData": checkData,
        "lastTopicId": lastTopicId,
        "numOfAnswers": 3,
        "receiveType": receiveType
    }
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/topic/receive',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print("ans_receive: ",response.text)
    except:
        print(traceback.format_exc())

def ans_restore(cookies):
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
    }
    checkData = rsa_encrypt("restoreType=2", pubkey_str)

    data = {
        "restoreType": 2,
        "checkData": checkData,
    }
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/topic/restore',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print("ans_restore: ",response.text)
    except:
        print(traceback.format_exc())

def ans_getTimes(cookies):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/topic/user', headers=headers, cookies=cookies)
        result = json.loads(response.text)
        print("ans_getTimes: ", result)
        stamina = result["data"]["stamina"]
        remainingTimes = result["data"]["remainingTimes"]
        return {"stamina": stamina,
                "remainingTimes": remainingTimes}
    except:
        print(traceback.format_exc())

def ans_start(cookies):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/topic/start', headers=headers, cookies=cookies)
        result = json.loads(response.text)
        print("ans_start: ", result)
        if not (result and ("data" in result) and result["data"] and ("paperId" in result["data"]) and ("dateStr" in result["data"]) and ("topics" in result["data"]) and (type(result["data"]["topics"]) is list) and (len(result["data"]["topics"])>2) and ("topicId" in result["data"]["topics"][2]) ): return None
        paperId = result["data"]["paperId"]
        dateStr = result["data"]["dateStr"]
        lastTopicId = result["data"]["topics"][2]["topicId"]
        print(paperId, dateStr, lastTopicId)
        return paperId, dateStr, lastTopicId
    except:
        print(traceback.format_exc())

def _str2key(s):
    b_str = base64.b64decode(s)
    if len(b_str) < 162:
        return False
    hex_str = ''
    for x in b_str:
        h = hex(x)[2:]
        h = h.rjust(2, '0')
        hex_str += h
    m_start = 29 * 2
    e_start = 159 * 2
    m_len = 128 * 2
    e_len = 3 * 2
    modulus = hex_str[m_start:m_start + m_len]
    exponent = hex_str[e_start:e_start + e_len]
    return modulus, exponent

def rsa_encrypt(s, pubkey_str):
    key = _str2key(pubkey_str)
    modulus = int(key[0], 16)
    exponent = int(key[1], 16)
    pubkey = rsa.PublicKey(modulus, exponent)
    return base64.b64encode(rsa.encrypt(s.encode(), pubkey)).decode()

pubkey_str = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCVhaR3Or7suUlwHUl2Ly36uVmboZ3+HhovogDjLgRE9CbaUokS2eqGaVFfbxAUxFThNDuXq/fBD+SdUgppmcZrIw4HMMP4AtE2qJJQH/KxPWmbXH7Lv+9CisNtPYOlvWJ/GHRqf9x3TBKjjeJ2CjuVxlPBDX63+Ecil2JR9klVawIDAQAB"

def lottery_info(cookies):
    print("\n【幸运大转盘】")
    """
    转盘信息查询
    """
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-ad-sweepstake-h5/home',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/inspire/lottery/info', headers=headers, cookies=cookies)
        result = response.json()
        remainingTimes = result["data"]["remainingTimes"]
        print(f'转盘info: {result["data"]}\n')
        if remainingTimes in [0, 1]:
            print("今日完毕")
            return
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/inspire/lottery/token', headers=headers, cookies=cookies)
        print("token: ", response.json())
        token = response.json()["data"]["id"]
        data = {
            "token": token,
            "sign": rsa_encrypt(f"token={token}&userId={get_uid(cookies)}", pubkey_str),
        }
        response = requests.post('https://m.ximalaya.com/speed/web-earn/inspire/lottery/chance',
                                 headers=headers, cookies=cookies, data=json.dumps(data))

        result = response.json()
        print("chance: ", result)
        data = {
            "sign": rsa_encrypt(str(result["data"]["chanceId"]), pubkey_str),
        }
        response = requests.post('https://m.ximalaya.com/speed/web-earn/inspire/lottery/action',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print(response.text)
    except:
        print(traceback.format_exc())

def index_baoxiang_award(cookies):
    print("\n  【首页、宝箱奖励及翻倍】")
    headers = {
        'User-Agent': UserAgent,
        'Host': 'mobile.ximalaya.com',
    }
    uid = cookies["1&_token"].split("&")[0]
    currentTimeMillis = int(time.time()*1000)-2
    response = requests.post('https://mobile.ximalaya.com/pizza-category/activity/getAward?activtyId=baoxiangAward',
                             headers=headers, cookies=cookies)

    result = response.json()
    print("宝箱奖励: ", result)
    if "ret" in result and result["ret"] == 0:
        awardReceiveId = result["awardReceiveId"]
        headers = {
            'Host': 'mobile.ximalaya.com',
            'Accept': '*/*',
            'User-Agent': UserAgent,
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        params = (
            ('activtyId', 'baoxiangAward'),
            ('awardReceiveId', awardReceiveId),
        )
        try:
            response = requests.get('http://mobile.ximalaya.com/pizza-category/activity/awardMultiple',
                                    headers=headers, params=params, cookies=cookies)
        except:
            print(traceback.format_exc())
        print("翻倍 ", response.text)
    uid = get_uid(cookies)
    ###################################
    params = (
        ('activtyId', 'indexSegAward'),
        ('ballKey', str(uid)),
        ('currentTimeMillis', str(currentTimeMillis)),
        ('sawVideoSignature', f'{currentTimeMillis}+{uid}'),
        ('version', '2'),
    )
    try:
        response = requests.get('https://mobile.ximalaya.com/pizza-category/activity/getAward',
                                headers=headers, cookies=cookies, params=params)
        result = response.json()
        print("首页奖励: ", result)
        if "ret" in result and result["ret"] == 0:
            awardReceiveId = result["awardReceiveId"]
            headers = {
                'Host': 'mobile.ximalaya.com',
                'Accept': '*/*',
                'User-Agent': UserAgent,
                'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            params = (
                ('activtyId', 'indexSegAward'),
                ('awardReceiveId', awardReceiveId),
            )
            try:
                response = requests.get('http://mobile.ximalaya.com/pizza-category/activity/awardMultiple',
                                        headers=headers, params=params, cookies=cookies)
                print("翻倍: ", response.text)
            except:
                print(traceback.format_exc())
    except:
        print(traceback.format_exc())

def checkin(cookies):
    print("\n【连续签到】")
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/welfare',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    params = (
        ('time', f"""{int(time.time()*1000)}"""),
    )
    try:
        response = requests.get('https://m.ximalaya.com/speed/task-center/check-in/record',
                                headers=headers, params=params, cookies=cookies)

        result = json.loads(response.text)
        print("checkin:", result)
        print(f"""连续签到{result["continuousDays"]}/{result["historyDays"]}天""")
        print(result["isTickedToday"])
        if not result["isTickedToday"]:
            print("!!!开始签到")
            if result["canMakeUp"]:
                print("canMakeUp 第30天需要手动")
                return
            headers = {
                'User-Agent': UserAgent,
                'Content-Type': 'application/json;charset=utf-8',
                'Host': 'm.ximalaya.com',
                'Origin': 'https://m.ximalaya.com',
                'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/welfare',
            }
            uid = get_uid(cookies)
            data = {
                "checkData": rsa_encrypt(f"date={_datatime}&uid={uid}", pubkey_str),
                "makeUp": False
            }

            response = requests.post('https://m.ximalaya.com/speed/task-center/check-in/check',
                                     headers=headers, cookies=cookies, data=json.dumps(data))
            print("签到结果: ",response.text)
    except:
        print(traceback.format_exc())

def ad_score(cookies, businessType, taskId):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain ,*/*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Content-Type': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        response = requests.get(
            'https://m.ximalaya.com/speed/task-center/ad/token', headers=headers, cookies=cookies)
    except:
        print("网络请求异常,为避免GitHub action报错,直接退出")
        exit()
    
    print("ad_score: ", response.text)
    result = response.json()
    token = result["id"]
    uid = get_uid(cookies)
    data = {
        "taskId": taskId,
        "businessType": businessType,
        "rsaSign": rsa_encrypt(f"""businessType={businessType}&token={token}&uid={uid}""", pubkey_str),
    }
    try:
        response = requests.post(f'https://m.ximalaya.com/speed/task-center/ad/score',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print(response.text, '\n')
    except:
        print(traceback.format_exc())

def bubble(cookies):
    print("\n【bubble】")
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-open-components/bubble',
    }
    uid = get_uid(cookies)
    data = {"listenTime": "41246", "signature": "2b1cc9ee020db596d28831cff8874d9c",
            "currentTimeMillis": "1596695606145", "uid": uid, "expire": False}
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/listen/bubbles',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        result = response.json()
        print("bubble: ", result)
        if not result["data"]["effectiveBubbles"]:
            print("暂无有效气泡")
            return
        for i in result["data"]["effectiveBubbles"]:
            print(i["id"])
            receive(cookies, i["id"])
            time.sleep(1)
            ad_score(cookies, 7, i["id"])
        for i in result["data"]["expiredBubbles"]:
            ad_score(cookies, 6, i["id"])
    except:
        print(traceback.format_exc())

def receive(cookies, taskId):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-open-components/bubble',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        response = requests.get(
            f'https://m.ximalaya.com/speed/web-earn/listen/receive/{taskId}', headers=headers, cookies=cookies)
        print("receive: ", response.text)
    except:
        print(traceback.format_exc())

def getOmnipotentCard(cookies):
    print("\n 【领取万能卡】")
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
    }
    try:
        count = requests.get('https://m.ximalaya.com/speed/web-earn/card/omnipotentCardInfo',
                             headers=headers, cookies=cookies,).json()["data"]["count"]
    except:
        print(traceback.format_exc())
    if count == 5:
        print("今日已满")
        return

    token = requests.get('https://m.ximalaya.com/speed/web-earn/card/token/1',
                         headers=headers, cookies=cookies,).json()["data"]["id"]
    print("token: ", token)
    uid = get_uid(cookies)
    data = {
        "listenTime": mins-date_stamp,
        "signData": rsa_encrypt(f"{_datatime}{token}{uid}", pubkey_str),
        "token": token
    }
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/card/getOmnipotentCard',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print(response.text)
    except:
        print(traceback.format_exc())

def cardReportTime(cookies):
    print("\n【收听获得抽卡机会】")
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
    }
    listenTime = mins-date_stamp
    uid = get_uid(cookies)
    data = {"listenTime": listenTime,
            "signData": rsa_encrypt(f"{_datatime}{listenTime}{uid}", pubkey_str), }
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/card/reportTime',
                                 headers=headers, cookies=cookies, data=json.dumps(data)).json()
        print("cardReportTime: ", response)
        if response and ("data" in response) and response["data"] and ("upperLimit" in response["data"]) and response["data"]["upperLimit"]:
            print("今日已达上限")
        else:
            print("Invalid response")
    except:
        print(traceback.format_exc())

def answer(cookies):
    print("\n【答题】")
    ans_times = ans_getTimes(cookies)
    if ans_times["stamina"] == 0:
        print("时间未到")
    for _ in range(ans_times["stamina"]):
        ret = ans_start(cookies)
        if not ret: continue
        paperId, _, lastTopicId = ret
        ans_receive(cookies, paperId, lastTopicId, 1)
        time.sleep(1)
        ans_receive(cookies, paperId, lastTopicId, 2)
        time.sleep(1)

    if ans_times["remainingTimes"] > 0:
        print("[看视频恢复体力]")
        ans_restore(cookies)
        for _ in range(5):
            ret = ans_start(cookies)
            if not ret: continue
            paperId, _, lastTopicId = ret 
            ans_receive(cookies, paperId, lastTopicId, 1)
            time.sleep(1)
            ans_receive(cookies, paperId, lastTopicId, 2)
            time.sleep(1)


def saveListenTime(cookies):
    print("\n【刷时长1】")
    headers = {
        'User-Agent': UserAgent,
        'Host': 'mobile.ximalaya.com',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    listentime = date_stamp
    print(f"上传本地收听时长1: {listentime//60}分钟")
    if listentime//60 >= int(maximum_duration):
        print('已到达设置时长,将不再刷时长')
    else:
        currentTimeMillis = int(time.time()*1000)-2
        uid = get_uid(cookies)
        sign = hashlib.md5(
            f'currenttimemillis={currentTimeMillis}&listentime={listentime}&uid={uid}&23627d1451047b8d257a96af5db359538f081d651df75b4aa169508547208159'.encode()).hexdigest()
        data = {
            'activtyId': 'listenAward',
            'currentTimeMillis': currentTimeMillis,
            'listenTime': str(listentime),
            'nativeListenTime': str(listentime),
            'signature': sign,
            'uid': uid
        }
        try:
            response = requests.post('http://mobile.ximalaya.com/pizza-category/ball/saveListenTime',
                                     headers=headers, cookies=cookies, data=data)
            print("saveListenTime", response.text)
        except:
            print(traceback.format_exc())

def listenData(cookies):
    print("\n【刷时长2】")
    headers = {
        'User-Agent': 'ting_v1.1.9_c5(CFNetwork, iOS 14.0.1, iPhone9,2)',
        'Host': 'm.ximalaya.com',
        'Content-Type': 'application/json',
    }
    listentime = date_stamp
    print(f"上传本地收听时长2: {listentime//60}分钟")
    if listentime//60 >= int(maximum_duration):
        print('已到达设置时长,将不再刷时长')
    else:
        currentTimeMillis = int(time.time()*1000)-2
        uid = get_uid(cookies)
        sign = hashlib.md5(
            f'currenttimemillis={currentTimeMillis}&listentime={listentime}&uid={uid}&23627d1451047b8d257a96af5db359538f081d651df75b4aa169508547208159'.encode()).hexdigest()
        data = {
            'currentTimeMillis': currentTimeMillis,
            'listenTime': str(listentime),
            'signature': sign,
            'uid': uid
        }
        try:
            response = requests.post('http://m.ximalaya.com/speed/web-earn/listen/client/data',
                                     headers=headers, cookies=cookies, data=json.dumps(data))
            print(response.text)
        except:
            print(traceback.format_exc())


def card_exchangeCoin(cookies, themeId, cardIdList):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    token = requests.get('https://m.ximalaya.com/speed/web-earn/card/token/3',
                         headers=headers, cookies=cookies,).json()["data"]["id"]
    print("token: ", token)
    uid = get_uid(cookies)
    data = {
        "cardIdList": cardIdList,
        "themeId": themeId,
        "signData": rsa_encrypt(f"{_datatime}{token}{uid}", pubkey_str),
        "token": token
    }
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
    }
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/card/exchangeCoin',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print("card_exchangeCoin: ", response.text)
    except:
        print(traceback.format_exc())

def card_exchangeCard(cookies, toCardAwardId, fromRecordIdList):
    fromRecordIdList = sorted(fromRecordIdList)
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
    }
    data = {
        "toCardAwardId": toCardAwardId,
        "fromRecordIdList": fromRecordIdList,
        "exchangeType": 1,
    }
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/card/exchangeCard',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print(response.text)
    except:
        print(traceback.format_exc())

def draw_5card(cookies, drawRecordIdList):  # 五连抽
    drawRecordIdList = sorted(drawRecordIdList)
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
    }
    uid = get_uid(cookies)
    data = {
        "signData": rsa_encrypt(f"{''.join(str(i) for i in drawRecordIdList)}{uid}", pubkey_str),
        "drawRecordIdList": drawRecordIdList,
        "drawType": 2,
    }
    try:
        response = requests.post('https://m.ximalaya.com/speed/web-earn/card/draw',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print("五连抽: ", response.text)
    except:
        print(traceback.format_exc())

def card(cookies):
    print("\n【抽卡】")
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/card/userCardInfo', headers=headers, cookies=cookies)
        print("card: ", response.text)
        data = response.json()["data"]
        #######
        # 5连抽
        drawRecordIdList = data["drawRecordIdList"]
        print("抽卡机会: ", drawRecordIdList)
        for _ in range(len(drawRecordIdList)//5):
            tmp = []
            for _ in range(5):
                tmp.append(drawRecordIdList.pop())
            draw_5card(cookies, tmp)
        ########
        # 手牌兑换金币
        # 1 万能卡  10 碎片
        print("检查手牌，卡牌兑金币")
        themeId_id_map = {
            2: [2, 3],
            3: [4, 5, 6, 7],
            4: [8, 9, 10, 11, 12],
            5: [13, 14, 15, 16, 17, 18],
            6: [19, 20, 21, 22],
            7: [23, 24, 25, 26, 27],
            8: [28, 29, 30, 31, 32],
            9: [33, 34, 35, 36, 37]
        }
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/card/userCardInfo', headers=headers, cookies=cookies)
        data = response.json()["data"]
        userCardsList = data["userCardsList"]  # 手牌
        lstg = groupby(userCardsList, key=lambda x: x["themeId"])
        for key, group in lstg:
            if key in [1, 10]:
                continue
            themeId = key
            ids = list(group)
            tmp_recordId = []
            tmp_id = []
            for i in ids:
                if i["id"] in tmp_id:
                    continue
                tmp_recordId.append(i["recordId"])
                tmp_id.append(i["id"])
            if len(tmp_recordId) == len(themeId_id_map[key]):
                print("可以兑换")
                card_exchangeCoin(cookies, themeId, tmp_recordId)
        ###############
        # 万能卡兑换稀有卡
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/card/userCardInfo', headers=headers, cookies=cookies)
        data = response.json()["data"]
        userCardsList = data["userCardsList"]
        omnipotentCard = [i for i in userCardsList if i["id"] == 1]
        cityCardId = [i["id"] for i in userCardsList if i["themeId"] == 9]
        need = set(themeId_id_map[9])-set(cityCardId)

        print("万能卡: ", [i['recordId'] for i in omnipotentCard])
        for _ in range(len(omnipotentCard)//4):
            tmp = []
            for _ in range(4):
                tmp.append(omnipotentCard.pop())
            fromRecordIdList = [i['recordId'] for i in tmp]
            if need:
                print("万能卡兑换稀有卡:")
                card_exchangeCard(cookies, need.pop(), fromRecordIdList)
    except:
        print(traceback.format_exc())

def account(cookies):
    print("\n【 打印账号信息】")
    headers = {
        'Host': 'm.ximalaya.com',
        'Content-Type': 'application/json;charset=utf-8',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': UserAgent,
        'Referer': 'https://m.ximalaya.com/speed/web-earn/wallet',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    try:
        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/account/coin', headers=headers, cookies=cookies)
        result = response.json()
        print(f"""
    当前剩余:{result["total"]/10000}
    今日获得:{result["todayTotal"]/10000}
    累计获得:{result["historyTotal"]/10000}
    """)
        account_info = '%s: 获得金币 %.4f(%.4f)' % (cookies['device_model'], float(result["total"]/10000), float(result["todayTotal"]/10000))
        print(account_info)
        return account_info
    except:
        print(traceback.format_exc())

def get_uid(cookies):
    return cookies["1&_token"].split("&")[0]
##################################################################

def main():
    bark_content = ''
    for idx, ck in enumerate(cookiesList):
        print(">>>>>>>>>【账号%d开始】" % idx)
        cookies = str_to_dict(ck)
        try:
            uid = cookies["1&_token"].split("&")[0]
        except:
            print(" !!!!!!!  cookie填写错误")
            uid = cookies["1&_token"].split("&")[0]  # 强制action报错提醒
        if XMLY_ACCUMULATE_TIME == 1:
            if safe_mode == 1:
                if 0 < bj_dt.hour < 1 or 6 < bj_dt.hour < 11 or 13 < bj_dt.hour < 23:
                    saveListenTime(cookies)
                    listenData(cookies)
                else:
                    print('不在安全时间内！')
            else:
                saveListenTime(cookies)
                listenData(cookies)
        #read(cookies, uid)  # 阅读
        bubble(cookies)  # 收金币气泡
        checkin(cookies)  # 自动签到
        # lottery_info(cookies)  # 大转盘4次
        answer(cookies)      # 答题赚金币
        cardReportTime(cookies)  # 卡牌
        getOmnipotentCard(cookies)  # 领取万能卡
        card(cookies)  # 抽卡
        index_baoxiang_award(cookies)  # 首页、宝箱奖励及翻倍
        account_info = account(cookies)
        bark_content = bark_content + account_info + '\n'
    if bj_dt.hour % 18 == 0 and bj_dt.hour / 18 == 1 and bj_dt.minute <= 30:
        requests.get('https://api.day.app/%s/喜马拉雅极速版/%s' % (bark_machine_code, bark_content[:-1]))

if __name__ == '__main__':
    main()
