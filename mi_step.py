# -*- coding: utf-8 -*-

import requests, time, re, json, random
import os
from datetime import datetime, timedelta

# 获取环境变量
def get_env_vars():
    XM_TG_BOT_TOKEN = os.environ.get("XM_TG_BOT_TOKEN", "")
    XM_TG_USER_ID = os.environ.get("XM_TG_USER_ID", "")
    MI_USER = os.environ.get("MI_USER", "")  # 格式：账号1#账号2
    MI_PASSWD = os.environ.get("MI_PASSWD", "")  # 格式：密码1#密码2
    STEP_MIN = int(os.environ.get("STEP_MIN", "8000"))  # 默认最小步数
    STEP_MAX = int(os.environ.get("STEP_MAX", "10000"))  # 默认最大步数
    return XM_TG_BOT_TOKEN, XM_TG_USER_ID, MI_USER, MI_PASSWD, STEP_MIN, STEP_MAX

# Telegram 通知
def telegram_bot(title, content):
    XM_TG_BOT_TOKEN, XM_TG_USER_ID, _, _, _, _ = get_env_vars()
    if not XM_TG_BOT_TOKEN or not XM_TG_USER_ID:
        print("Telegram推送的xm_tg_bot_token或者xm_tg_user_id未设置!!\n取消推送")
        return
    print("Telegram 推送开始")
    send_data = {"chat_id": XM_TG_USER_ID, "text": title + '\n\n' + content, "disable_web_page_preview": "true"}
    response = requests.post(url=f'https://api.telegram.org/bot{XM_TG_BOT_TOKEN}/sendMessage', data=send_data)
    print(response.text)

# 获取当前时间戳
def get_time():
    url = "http://mshopact.vivo.com.cn/tool/config"
    headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; MI 6 MIUI/20.6.18)'}
    response = requests.get(url, headers=headers).json()
    return response["data"]["nowTime"]

# 获取 app_token
def get_app_token(login_token):
    url = f"https://account-cn.huami.com/v1/client/app_tokens?app_name=com.xiaomi.hm.health&dn=api-user.huami.com%2Capi-mifit.huami.com%2Capp-analytics.huami.com&login_token={login_token}"
    headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; MI 6 MIUI/20.6.18)'}
    response = requests.get(url, headers=headers).json()
    return response['token_info']['app_token']

# 获取登录 code
def get_code(location):
    code_pattern = re.compile("(?<=access=).*?(?=&)")
    return code_pattern.findall(location)[0]

# 登录小米运动
def login(user, password):
    url1 = f"https://api-user.huami.com/registrations/{user}/tokens"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2"
    }
    data1 = {
        "client_id": "HuaMi",
        "password": password,
        "redirect_uri": "https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
        "token": "access"
    }
    r1 = requests.post(url1, data=data1, headers=headers, allow_redirects=False)
    location = r1.headers["Location"]
    try:
        code = get_code(location)
    except:
        return 0, 0

    url2 = "https://account.huami.com/v2/client/login"
    data2 = {
        "allow_registration": "false",
        "app_name": "com.xiaomi.hm.health",
        "app_version": "6.3.5",
        "code": code,
        "country_code": "CN",
        "device_id": "2C8B4939-0CCD-4E94-8CBA-CB8EA6E613A1",
        "device_model": "phone",
        "dn": "api-user.huami.com,api-mifit.huami.com,app-analytics.huami.com",
        "grant_type": "access_token",
        "lang": "zh_CN",
        "os_version": "1.5.0",
        "source": "com.xiaomi.hm.health",
        "third_name": "email"
    }
    r2 = requests.post(url2, data=data2, headers=headers).json()
    login_token = r2["token_info"]["login_token"]
    userid = r2["token_info"]["user_id"]
    return login_token, userid

# 模拟步数逐步增加
def calculate_step_increment(total_steps, start_hour=7, end_hour=22):
    current_hour = datetime.now().hour
    total_hours = end_hour - start_hour + 1
    if current_hour < start_hour or current_hour > end_hour:
        return 0  # 非运行时间不增加步数
    elapsed_hours = current_hour - start_hour + 1
    step_per_hour = total_steps // total_hours
    current_target = step_per_hour * elapsed_hours
    return min(current_target, total_steps)  # 返回当前目标步数

# 修改步数
def modify_steps(user, passwd, target_steps):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if not user or not passwd:
        print("用户名或密码填写有误！")
        return f"{user[:4]}****{user[-4:]}: [{now}] 用户名或密码填写有误！"

    login_token, userid = login(user, passwd)
    if login_token == 0:
        print("登录失败！")
        return f"{user[:4]}****{user[-4:]}: [{now}] 登录失败！"

    app_token = get_app_token(login_token)
    t = get_time()
    today = time.strftime("%Y-%m-%d")

    # 当前步数（逐步增加）
    current_steps = calculate_step_increment(target_steps)
    if current_steps == 0:
        return f"{user[:4]}****{user[-4:]}: [{now}] 当前时间不在步数增加范围内！"

    # 完整的 data_json 模板，动态替换日期和步数
    data_json = f'%5B%7B%22date%22%3A%22{today}%22%2C%22summary%22%3A%22%7B%5C%22stp%5C%22%3A%7B%5C%22ttl%5C%22%3A{current_steps}%2C%5C%22dis%5C%22%3A{int(current_steps * 0.7)}%2C%5C%22cal%5C%22%3A{int(current_steps * 0.05)}%7D%2C%5C%22slp%5C%22%3A%7B%5C%22ttl%5C%22%3A0%2C%5C%22dp%5C%22%3A0%2C%5C%22lgt%5C%22%3A0%2C%5C%22wk%5C%22%3A0%7D%2C%5C%22exr%5C%22%3A%7B%5C%22ttl%5C%22%3A0%2C%5C%22cal%5C%22%3A0%7D%2C%5C%22hr%5C%22%3A%7B%5C%22avg%5C%22%3A0%2C%5C%22max%5C%22%3A0%2C%5C%22min%5C%22%3A0%7D%2C%5C%22spo2%5C%22%3A%7B%5C%22avg%5C%22%3A0%2C%5C%22max%5C%22%3A0%2C%5C%22min%5C%22%3A0%7D%2C%5C%22strs%5C%22%3A%7B%5C%22lvl%5C%22%3A0%7D%2C%5C%22stand%5C%22%3A%7B%5C%22ttl%5C%22%3A0%7D%7D%22%2C%22detail%22%3A%22%7B%5C%22stp%5C%22%3A%5B%7B%5C%22val%5C%22%3A{current_steps}%2C%5C%22tm%5C%22%3A{today}%7D%5D%2C%5C%22slp%5C%22%3A%5B%5D%2C%5C%22exr%5C%22%3A%5B%5D%2C%5C%22hr%5C%22%3A%5B%5D%2C%5C%22spo2%5C%22%3A%5B%5D%2C%5C%22stand%5C%22%3A%5B%5D%7D%22%7D%5D'

    url = f'https://api-mifit-cn.huami.com/v1/data/band_data.json?&t={t}'
    head = {"apptoken": app_token, "Content-Type": "application/x-www-form-urlencoded"}
    data = f'userid={userid}&last_sync_data_time=1597306380&device_type=0&last_deviceid=DA932FFFFE8816E7&data_json={data_json}'

    response = requests.post(url, data=data, headers=head).json()
    result = f"{user[:4]}****{user[-4:]}: [{now}] 修改步数（{current_steps}/{target_steps}）" + response['message']
    print(result)
    return result

# 主函数
def main():
    XM_TG_BOT_TOKEN, XM_TG_USER_ID, MI_USER, MI_PASSWD, STEP_MIN, STEP_MAX = get_env_vars()
    user_list = MI_USER.split('#') if MI_USER else []
    passwd_list = MI_PASSWD.split('#') if MI_PASSWD else []

    if len(user_list) != len(passwd_list) or not user_list:
        msg = "用户名和密码数量不匹配或未设置！"
        print(msg)
        telegram_bot("小米运动错误", msg)
        return

    push_msg = ""
    for i in range(len(user_list)):
        target_steps = random.randint(STEP_MIN, STEP_MAX)  # 随机目标步数
        result = modify_steps(user_list[i], passwd_list[i], target_steps)
        push_msg += result + "\n"

    telegram_bot("小米运动步数修改", push_msg)

if __name__ == "__main__":
    main()
