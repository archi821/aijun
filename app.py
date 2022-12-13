from __future__ import unicode_literals

import errno
import os
import sys
sys.path.insert(0, "../.") # "../../../../app/aiml-master/.
import re
import tempfile
import random
import requests
from bs4 import BeautifulSoup

from argparse import ArgumentParser

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)

from linebot.models import *

import aiml
# The Kernel object is the public interface to the AIML interpreter.
k = aiml.Kernel()
# Use the learn method to load the contents of AIML files into the Kernel.
k.learn("tw-startup.xml")
k.respond("load aiml tw") # must be the same with pattern in tw-startup.xml

app = Flask(__name__)

line_bot_api = LineBotApi('uyZ0FhFlFo1h8zxPI4Y7Vur6KcxiDL3MDJ3m9/+e6Fx7I7mvkKyKrKjZ0umcy6R/6IhhGvsqPOtqEMrfLBfhatmCjd720c/yWXWCAXUSlw1pItpdDC9J2oQNKYYxbYXuCnKdVzlYt4QQ/2I73Z7l8AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b7265fc36914b169b6a5cd0e19b5976b')

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@app.route("/", methods=['POST'])
def index():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if event.message.text == "貼圖":
        line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=1, sticker_id=2))    
    elif event.message.text == "妳很可愛": 
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://i2.kknews.cc/SIG=3lv23he/568n0000357p73q91ns7.jpg', preview_image_url='https://i2.kknews.cc/SIG=3lv23he/568n0000357p73q91ns7.jpg'))
    elif event.message.text == "我出門了": 
        line_bot_api.reply_message(event.reply_token,ImageSendMessage(original_content_url='https://i1.kknews.cc/SIG=foio9r/ctp-vzntr/1533882150237o531n8o082.jpg', preview_image_url='https://i1.kknews.cc/SIG=foio9r/ctp-vzntr/1533882150237o531n8o082.jpg'))
    elif event.message.text == "近期上映電影":
        content = movie()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    elif event.message.text == "近期上映動畫":
        content = anime()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    elif event.message.text == "今日運勢":
        content = Horoscopes()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
    elif event.message.text == "給我看水族板文章":
        content = ptt_Aquarium()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)) 
    elif event.message.text == "關西將棋會館": 
        line_bot_api.reply_message(event.reply_token,LocationSendMessage(title='関西将棋会館',address='大阪',latitude=34.6988588,longitude=135.4872425))
    else:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=k.respond(event.message.text))
    )

# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])
        
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)

def ptt_Aquarium():
    target_url = 'https://www.ptt.cc/bbs/Aquarium/index.html'
    print('Start parsing auarium ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('div.title a')):
        if index == 20:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "https://www.ptt.cc/bbs/" + data['href']
        content += '{}\n{}\n'.format(title, link)
    return content

def movie():
    target_url = 'http://www.atmovies.com.tw/movie/next/0/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('ul.filmListAll a')):
        if index == 20:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "http://www.atmovies.com.tw" + data['href']
        content += '{}\n{}\n'.format(title, link)
    return content

def anime():
    target_url = 'https://www.myvideo.net.tw/cartoon'
    print('Start parsing anime ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('div.sliderTwoLine a')):
        if index == 20:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "https://www.myvideo.net.tw/" + data['href']
        content += '{}\n{}\n'.format(title, link)
    return content

def Horoscopes():
    target_url = 'https://horoscope.dice4rich.com/'
    print('Start parsing Horoscopes ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('div.horoscope-signs a')):
        if index == 20:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "https://horoscope.dice4rich.com/" + data['href']
        content += '{}\n{}\n'.format(title, link)
    return content

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)
