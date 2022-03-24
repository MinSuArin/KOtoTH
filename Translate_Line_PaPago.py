# -*- coding: utf-8 -*-

import requests
import re
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from flask import Flask, jsonify, request, abort

app = Flask(__name__)

channel_secret = 'b67316df3e87f829070222d53b9af01f'
channel_access_token = 'vuiFZILMzlez0+fMPWjvd0q7GHTkHCLiZ64qh7mGfZEJpf1nm5HoI4JgPQwKXw+GeLdVUBNnNIA49RoC+yEEmmBfiaqf0GJ8qa7Kx3OTj3frmDbPwQzP4GUWxh4Ds/Sk6ez1omgYe5YDDkRUNXurzwdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def is_hangul(text):
    hangul_re = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
    return hangul_re.search(text) is not None

def translate(text):
    if is_hangul(text):
        return _translate(text, 'ko', 'th')
    else:
        return _translate(text, 'th', 'ko')

def _translate(text, source='th', target='ko'):

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Naver-Client-Id': 'FMyOqb8zMexu6Ne64qgt',
        'X-Naver-Client-Secret': 'mWOj_IIYyI',
    }

    data = {'source': source,
            'target': target,
            'text': text.encode('utf-8')}

    response = requests.post('https://openapi.naver.com/v1/papago/n2mt', headers=headers, data=data)
    res_code = response.status_code

    if res_code is not 200:
        print("Error Code:" + str(res_code))
        return 'Cannot translate'

    json = response.json()

    return json['message']['result']['translatedText']

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        # Translate
        translated = translate(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=translated)
        )

    return 'OK'

## For Kakao
#@app.route('/message', methods=['POST'])
#def message():
#    data = request.json
#    translated = translate(data['content'])
#    return jsonify({"message": {"text": translated}})

@app.route('/keyboard')
def keyboard():
    return jsonify({'type': 'text'})

if __name__ == "__main__":

    app.run(debug=False, port=8000)