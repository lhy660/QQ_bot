from flask import Flask, request, jsonify
from datetime import datetime
import requests
import random
import configparser
import re
from openai import OpenAI
import os
from collections import deque
import json

#2509082202修改
app = Flask(__name__)
api_key = os.getenv('AIKEY')
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
user_histories = {}

# 历史记录存储目录
HISTORY_DIR = "chat_histories"

# 确保存储目录存在
os.makedirs(HISTORY_DIR, exist_ok=True)

def load_user_histories():
    global user_histories
    if not os.path.exists(HISTORY_DIR):
        return
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith('.json'):
            user_id = filename[:-5]  # 移除 .json 后缀
            filepath = os.path.join(HISTORY_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    # 将加载的列表转换为 deque
                    user_histories[user_id] = deque(history_data, maxlen=10)
                    print(f"已加载用户 {user_id} 的对话历史，共 {len(history_data)} 条记录")
            except Exception as e:
                print(f"加载用户 {user_id} 的历史记录失败: {e}")


def save_user_history(user_id, history):
    filepath = os.path.join(HISTORY_DIR, f"{user_id}.json")
    try:
        # 将 deque 转换为列表以便 JSON 序列化
        history_list = list(history)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存用户 {user_id} 的历史记录失败: {e}")


load_user_histories()

#————————————#

def chat(user_id, group_id, message_type, parameter, at_qq, message2):
    if at_qq is None:
        at_qq = 0
    if int(at_qq) == 3035397258 or message_type == "private":
        stime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config = configparser.ConfigParser()
        config.read('data.ini')
        coins = int(config.get(str(user_id), 'coins', fallback=0))
        if coins < 15:
            url1 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=聊天功能%0A—————————————%0A您的金币不够，每次对话需要消耗15金币。%0A要不试试“抽金币”或者“签到”来获得金币？%0A—————————————%0A✨北京时间✨%0A{stime}"
            response = requests.get(url1)
            return
        new_coins = coins - 15
        config.set(str(user_id), 'coins', str(new_coins))
        with open('data.ini', 'w') as configfile:
            config.write(configfile)
        user_id_str = str(user_id)
        if user_id_str not in user_histories:
            user_histories[user_id_str] = deque(maxlen=10)
        user_dialogue_history = user_histories[user_id_str]
        if message2.strip():
            user_dialogue_history.append({"role": "user", "content": message2.strip()})
        model_name = "deepseek-chat"
        system_prompt = """你叫芒果,为人热情.回答需自然简短,1-2句话即可,无需表达状态."""
        messages = [{"role": "system", "content": system_prompt.strip()}]
        messages.extend(user_dialogue_history)
        try:
            response = client.chat.completions.create(model=model_name, messages=messages, max_tokens=80, temperature=0.7, presence_penalty=0.3)
            ai_reply = response.choices[0].message.content.strip().replace('\n', ' ')
            user_dialogue_history.append({"role": "assistant", "content": ai_reply})
            save_user_history(user_id_str, user_dialogue_history)
            url2 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message={ai_reply}%0A—————————————%0A您金币剩余{new_coins}"
            response = requests.get(url2)
        except Exception as e:
            url3 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message={str(e)}"
            response = requests.get(url3)
    else:
        print("芒果暂不处理")
        return


def liaotiangongneng(user_id, group_id, message_type, parameter, at_qq):
    stime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=聊天功能%0A—————————————%0A关于聊天功能，用户需要注意一些内容%0A1.机器人回复的内容均为deepseek聊天模型生成，非人为回复。%0A2.由于网络问题，机器人并不能秒回你信息，会有延迟。%0A和机器人聊天的格式如下%0A—————————————%0A“@机器人”“你要发的信息”%0A例如%0A@芒果 你好呀。%0A—————————————%0A✨北京时间✨%0A{stime}"
    response = requests.get(url)

#——————————————#


def toujinbi(user_id, group_id, message_type, parameter, at_qq):
    if at_qq is None:
        print("芒果暂不处理")
        return
    if int(at_qq) == int(user_id):
        url1 =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=偷金币%0A—————————————%0A这是个毫无意义的行为。"
        response1 = requests.get(url1)
        return
    config = configparser.ConfigParser()
    config.read('data.ini')
    coins = int(config.get(str(user_id), 'coins', fallback=0))
    at_qq_coins = int(config.get(str(at_qq), 'coins', fallback=0))
    coins_tou = random.randint(100, 400)
    if at_qq_coins <= 0:
        url2 =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=偷金币%0A—————————————%0A对方没有钱，偷取金币失败。"
        response2 = requests.get(url2)
        return
    if at_qq_coins <= coins_tou:
        url3 =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=偷金币%0A—————————————%0A运气可能不太好，没偷到。"
        response3 = requests.get(url3)
        return
    new_coins = coins + coins_tou
    new_at_qq_coins = at_qq_coins - coins_tou
    config.set(str(user_id), 'coins', str(new_coins))
    config.set(str(at_qq), 'coins', str(new_at_qq_coins))
    with open('data.ini', 'w') as configfile:
        config.write(configfile)
    url4 =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=偷金币%0A—————————————%0A偷取成功，您偷了对方{coins_tou}个金币。%0A—————————————%0A您的金币有{new_coins}"
    response4 = requests.get(url4)


def yinhangxitong(user_id, group_id, message_type, parameter, at_qq):
    url =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=银行系统%0A—————————————%0A银行存款|银行取款%0A—————————————%0A格式如下%0A“存款+金额”%0A“取款+金额”%0A例如下方信息%0A存款520将金币存入银行可防止被偷哦~%0A%0A—————————————%0A转账%0A—————————————%0A可以将自己的金币转给他人，格式如下：%0A“转账+金额+@对象”%0A例如以下信息%0A“转账520@cnlhy”"
    response = requests.get(url)


def cunkuan(user_id, group_id, message_type, parameter, at_qq):
    if parameter == 0:
        print("无参数指令，不处理。")
        return
    config = configparser.ConfigParser()
    config.read('data.ini')
    coins = int(config.get(str(user_id), 'coins', fallback=0))
    bank_coins = int(config.get(str(user_id), 'bank_coins', fallback=0))
    if parameter <= 0:
        url1 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=您输入有效金额"
        response1 = requests.get(url1)
        return
    if coins < parameter:
        url2 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=[CQ:at,qq={user_id}]您的账户没有充足的余额用来存钱%0A—————————————%0A持有余额：{coins}"
        response2 = requests.get(url2)
        return
    new_coins = coins - parameter
    new_bank_coins = bank_coins + parameter
    config.set(str(user_id), 'coins', str(new_coins))
    config.set(str(user_id), 'bank_coins', str(new_bank_coins))
    with open('data.ini', 'w') as configfile:
        config.write(configfile)
    url3 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=[CQ:at,qq={user_id}]存款{parameter}成功%0A—————————————%0A持有余额：{new_coins}%0A银行余额：{new_bank_coins}"
    response3 = requests.get(url3)


def qukuan(user_id, group_id, message_type, parameter, at_qq):
    if parameter == 0:
        print("无参数指令，不处理。")
        return  
    config = configparser.ConfigParser()
    config.read('data.ini')
    coins = int(config.get(str(user_id), 'coins', fallback=0))
    bank_coins = int(config.get(str(user_id), 'bank_coins', fallback=0))
    if parameter <= 0:
        url1 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=您输入有效金额"
        response1 = requests.get(url1)
        return
    if bank_coins < parameter:
        url2 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=[CQ:at,qq={user_id}]您的银行没有充足的余额用来存钱%0A—————————————%0A银行余额：{bank_coins}"
        response2 = requests.get(url2)
        return
    new_coins = coins + parameter
    new_bank_coins = bank_coins - parameter
    config.set(str(user_id), 'coins', str(new_coins))
    config.set(str(user_id), 'bank_coins', str(new_bank_coins))
    with open('data.ini', 'w') as configfile:
        config.write(configfile)
    url3 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=[CQ:at,qq={user_id}]取款{parameter}成功%0A—————————————%0A持有余额：{new_coins}%0A银行余额：{new_bank_coins}"
    response3 = requests.get(url3)

def zhanghu(user_id, group_id, message_type, parameter, at_qq):
    config = configparser.ConfigParser()
    config.read('data.ini')
    coins = int(config.get(str(user_id), 'coins', fallback=0))
    bank_coins = int(config.get(str(user_id), 'bank_coins', fallback=0))
    url1 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=[CQ:at,qq={user_id}]您的账户如下%0A—————————————%0A银行余额：{bank_coins}%0A账户余额：{coins}"
    response1 = requests.get(url1)


def qiandao(user_id, group_id, message_type, parameter, at_qq):
    today = datetime.now().strftime('%Y-%m-%d')
    config = configparser.ConfigParser()
    config.read('data.ini')
    if config.has_section(str(user_id)):
        qiandao_limit = config.get(str(user_id), 'time_limit', fallback='')
        if qiandao_limit == today:
            url1 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=您今日已签到，明天再来哦~"
            response1 = requests.get(url1)
            return
    else:
        config[str(user_id)] = {}
    coins_today = random.randint(100, 200)
    coins = int(config.get(str(user_id), 'coins', fallback=0)) + coins_today
    config.set(str(user_id), 'coins', str(coins))
    config.set(str(user_id), 'time_limit', today)
    with open('data.ini', 'w') as configfile:
        config.write(configfile)
    url2 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&auto_escape=false&message=签到成功%0A—————————————%0A您获得了{coins_today}个金币%0A余额：{coins}%0A—————————————%0A"
    response2 = requests.get(url2)

def dianzan(user_id, group_id, message_type, parameter, at_qq):
    today = datetime.now().strftime('%Y-%m-%d')
    config = configparser.ConfigParser()
    config.read('data.ini')
    if config.has_section(str(user_id)):
        last_like = config.get(str(user_id), 'dianzan_limit', fallback='')
        if last_like == today:
            url1 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=今天已经为您点过赞啦，明天再来吧~"
            response1 = requests.get(url1)
            return
    else:
        config[str(user_id)] = {}
    coins = int(config.get(str(user_id), 'coins', fallback=0))
    if coins < 100:
        url2 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=你的余额不够哦~%0A—————————————%0A余额：{coins}"
        response2 = requests.get(url2)
        return
    new_coins = coins - 100
    config.set(str(user_id), 'coins', str(new_coins))
    config.set(str(user_id), 'dianzan_limit', today)
    with open('data.ini', 'w') as configfile:
        config.write(configfile)
    url3 = f"http://127.0.0.1:5700/send_like?times=10&user_id={user_id}"
    response3 = requests.get(url3)
    url4 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=给你点过了哦❤️%0A—————————————%0A剩余余额：{new_coins}"
    response4 = requests.get(url4)

def choujinbi(user_id, group_id, message_type, parameter, at_qq):
    config = configparser.ConfigParser()
    config.read('data.ini')
    coins = int(config.get(str(user_id), 'coins', fallback=0))
    if coins < 50:
        url1 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=[CQ:at,qq={user_id}]您的余额不足50，无法支付抽金币的费用。%0A—————————————%0A持有余额：{coins}"
        response1 = requests.get(url1)
    else:
        prize = random.randint(75, 200)
        new_coins = coins - 50 + prize
        config.set(str(user_id), 'coins', str(new_coins))
        with open('data.ini', 'w') as configfile:
            config.write(configfile)
        url2 = f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=[CQ:at,qq={user_id}]恭喜您抽到了{prize}个金币。%0A—————————————%0A持有余额：{new_coins}"
        response2 = requests.get(url2)

def caidan(user_id, group_id, message_type, parameter, at_qq):
    stime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=✨菜单✨%0A—————————————%0A🔔帮助🔔|🔥签到🔥%0A💻小游戏💻|🔥抽金币🔥%0A💳银行系统💳|💢禁言💢%0A🌚聊天功能🌝|❤给我点赞❤%0A—————————————%0A✨北京时间✨%0A{stime}"
    response = requests.get(url)


def zhuanzhang(user_id, group_id, message_type, parameter, at_qq):
    if at_qq is None:
        print("芒果暂不处理")
        return
    stime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if int(at_qq) == int(user_id):
        url1 =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=转账%0A—————————————%0A这是个毫无意义的行为。%0A—————————————%0A✨北京时间✨%0A{stime}"
        response1 = requests.get(url1)
        return
    config = configparser.ConfigParser()
    config.read('data.ini')
    coins = int(config.get(str(user_id), 'coins', fallback=0))
    at_qq_coins = int(config.get(str(at_qq), 'coins', fallback=0))
    if coins < parameter:
        url2 =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=转账%0A—————————————%0A转账失败，您没有足够资金。%0A—————————————%0A✨北京时间✨%0A{stime}"
        response1 = requests.get(url2)
    else:
        new_coins = coins - parameter
        new_at_qq_coins = at_qq_coins + parameter
        config.set(str(user_id), 'coins', str(new_coins))
        config.set(str(at_qq), 'coins', str(new_at_qq_coins))
        with open('data.ini', 'w') as configfile:
            config.write(configfile)
        url3 =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=转账%0A—————————————%0A转账{parameter}成功。您目前还剩余{new_coins}个金币。%0A—————————————%0A✨北京时间✨%0A{stime}"
        response2 = requests.get(url3)


def bangzhu(user_id, group_id, message_type, parameter, at_qq):
    stime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url =f"http://127.0.0.1:5700/send_msg?message_type={message_type}&group_id={group_id}&user_id={user_id}&message=帮助%0A—————————————%0A当前机器人设定有两种系统，第一种是机器人服务系统，第二种类是机器人聊天系统。%0A当机器人被@并且附带信息时，这时候机器人处于聊天系统，回复一切内容均与机器人服务无关。%0A例如：@芒果 你好呀%0A你好我是芒果。%0A—————————————%0A当回复设定指令时，所有回复内容都是机器人服务，例如“签到”“给我点赞”等等相关指令。%0A提醒：菜单上的关键词基本都是指令。%0A—————————————%0A✨北京时间✨%0A{stime}"
    response = requests.get(url)

toolbox = {
    "给我点赞": dianzan,
    "菜单": caidan,
    "签到": qiandao,
    "存款": cunkuan,
    "取款": qukuan,
    "账户": zhanghu,
    "抽金币": choujinbi,
    "银行系统": yinhangxitong,
    "偷金币": toujinbi,
    "聊天功能": liaotiangongneng,
    "转账": zhuanzhang,
    "帮助": bangzhu
    }


@app.route('/', methods=['POST'])
def post_data():
    data = request.get_json(force=True)# 获取请求体中的数据
    self_id = data.get('self_id')
    post_type = data.get('post_type')
    flag = data.get('flag')
    message_type = data.get('message_type')#消息的类型，私聊和群聊
    sub_type = data.get('sub_type')
    message_id = data.get('message_id')
    target_id = data.get('target_id')
    peer_id = data.get('peer_id')
    user_id = data.get('user_id')#发送者的信息
    raw_message = data.get('raw_message')#完整的消息，包括@详细信息
    font = data.get('font')
    group_id = data.get('group_id')#发送到某个群的群号
    sender_user_id = data.get('sender', {}).get('user_id')
    sender_nickname = data.get('sender', {}).get('nickname')
    sender_role = data.get('sender', {}).get('role')
    message1 = data.get('message', [])
    at_qq = None
    for item in message1:
        if item.get('type') == 'at':
            at_qq = item.get('data', {}).get('qq')
            break
    message2 = next((item['data']['text'] for item in message1 if item.get('type') == 'text'), None)#获取对方发送的信息
    parameter = 0
    if post_type == "request":
        url =f"http://127.0.0.1:5700/set_friend_add_request?flag={flag}&approve=true"
        response1 = requests.get(url)
        print("同意了用户（", user_id, "）的好友请求")
        return "_"
    if message_type == "group":
        print("收到用户：", sender_nickname, "（", user_id, "）在(", group_id, ")发送的消息：", message2)
    else:
        print("收到用户：", sender_nickname, "（", user_id, "）发送的消息：", message2)
    if message2 is None:
        print("芒果暂不处理")
    else:
        match = re.match(r'([^\d]+)(\d+)', message2)
        if match:
            # 如果匹配成功，提取指令和参数
            instruction = match.group(1)  # 提取指令
            parameter = int(match.group(2))  # 提取并转换参数为整数
            if instruction in toolbox:
                toolbox[instruction](user_id, group_id, message_type, parameter, at_qq)
            else:
                chat(user_id, group_id, message_type, parameter, at_qq, message2)
        else:
            if message2 in toolbox:
                toolbox[message2](user_id, group_id, message_type, parameter, at_qq)
            else:
                chat(user_id, group_id, message_type, parameter, at_qq, message2)
    return "_"
 

if __name__ == '__main__':
    app.run(debug=True, port=5800, host="0.0.0.0")
