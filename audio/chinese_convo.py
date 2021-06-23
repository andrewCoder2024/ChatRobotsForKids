import json
import requests

answer = ''

while True:
    text = input("User: ")
    sess = requests.get('https://api.ownthink.com/bot?spoken=' + text)

    answer = sess.text

    answer = json.loads(answer)

    answer = answer["data"]["info"]['text']

    print("Chatbot: " + answer)

    if text == '再见':
        break

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