import json
import requests

answer = ''


def chinese_chatbot():
    text = input("User: ")

    if text == '再见':
        return 'bye'
    sess = requests.get('https://api.ownthink.com/bot?spoken=' + text)

    answer = sess.text

    answer = json.loads(answer)

    return answer["data"]["info"]['text']


"""
{
    "message": "success",               // 请求是否成功
    "data": {
        "type": 5000,                   // 答案类型，5000文本类型
        "info": {
            "text": "姚明的身高是226厘米"  // 机器人返回的答案
        }
    }
}
"""
