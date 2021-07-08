#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from audio import media_translation
import pandas as pd
import stt, tts
# from DiabloGPT import Chat
from chinese_convo import chinese_chatbot
import platform
from english_convo import Chat
import pinyin
from PIL import Image
if platform.system() == 'Linux':
    import gesture
else:
    pass


class Chatbot:
    def __init__(self, isActing=False, sLang='en', lLang='en'):
        self.isActing = isActing
        self.listener = stt.Listener(isActing)
        self.speaker = tts.Speaker(isActing)
        self.speaker_lang = sLang
        self.listener_lang = lLang
        self.chat = Chat(language='en')
        self.last_phrase = None

    def say(self, text, speed=1, generator=False):
        response = ""
        if generator:
            if self.speaker_lang == 'cn':
                response = chinese_chatbot(text)
            else:
                response = self.chat.converse(text)
            print("response:", response)
            self.speaker.speak(response)
            self.last_phrase = response
        else:
            print("response:", text)
            self.speaker.speak(text, speed)
            self.last_phrase = text

    def listen(self):
        try:
            response = self.listener.listens()
        except:
            response = "i didn't quite hear you, can you repeat it?"
        print("You:", response)
        return response

    def change_speaker_lang(self, lang='en'):
        self.speaker.change_lang(lang)
        self.speaker_lang = lang

    def change_listener_lang(self, lang='en'):
        self.listener.change_lang(lang)
        self.listener_lang = lang


class Quiz():
    def __init__(self, chatbot, num_words=10, level=1, pos=0):
        self.pos = pos
        self.num_words = num_words
        self.level = level
        self.word_list = pd.DataFrame
        self.quiz_list = pd.DataFrame
        self.chatbot = chatbot

    def get_words(self):
        hsk = pd.read_json("json/hsk-level-{}_new.json".format(self.level))
        self.word_list = hsk.iloc[self.pos:self.pos + self.num_words, :]
        if self.quiz_list.empty:
            self.quiz_list = self.word_list
        else:
            self.quiz_list = pd.concat(self.quiz_list, self.word_list)
        # print(self.word_list.head())
        self.pos += self.num_words

    def iter_output(self):
        for word in self.quiz_list.iterrows():
            for el in word:
                self.chatbot.say(el)

    def init_quiz(self):
        num = 0
        temp_li = []
        score = {}
        Quiz.get_words(self)
        for index, row in self.quiz_list.iterrows():
            temp_li.append((row['hanzi'], row['translations']))
        while temp_li or not num:
            random.shuffle(temp_li)
            score[num] = 0
            repeat_keywords = ["repeat", "say that again", "didn't catch that", "can you repeat", "重复一遍", "重复", "再说一遍",
                               ""]
            for el in temp_li:
                user_input = ""
                res = random.randint(0, 1)
                if res:
                    while user_input in repeat_keywords:
                        self.chatbot.change_speaker_lang('en')
                        self.chatbot.say("Please provide the definition of " + ", ".join(
                            el[1]) + " in chinese")  # el[0] is in chinese
                        self.chatbot.change_listener_lang('cn')
                        user_input = self.chatbot.listen()
                    if pinyin.get(user_input) in [pinyin.get(e) for e in el[0]]:
                        score[num] += 1
                        temp_li.remove(el)
                        if self.chatbot.isActing:
                            gesture.correct(2)
                            gesture.stop_robot()
                        else:
                            Image.open("correct.png").show()
                        self.chatbot.change_speaker_lang('en')
                        self.chatbot.say("Good Job!", 1.2)
                    else:
                        if self.chatbot.isActing:
                            gesture.incorrect(2)
                            gesture.stop_robot()
                        else:
                            Image.open('incorrect.png').show()
                        self.chatbot.change_speaker_lang('en')
                        self.chatbot.say("Try again next time...", 0.8)
                else:
                    while user_input in repeat_keywords:
                        self.chatbot.change_speaker_lang('cn')
                        self.chatbot.say("请用英文说 " + el[0])
                        self.chatbot.change_listener_lang('en')
                        user_input = self.chatbot.listen()
                    if user_input in el[1] or "to "+user_input in el[1]:
                        score[num] += 1
                        temp_li.remove(el)
                        if self.chatbot.isActing:
                            gesture.correct(2)
                            gesture.stop_robot()
                        else:
                            Image.open("correct.png").show()
                        self.chatbot.change_speaker_lang('cn')
                        self.chatbot.say("恭喜，你答对了！", 0.8)
                    else:
                        if self.chatbot.isActing:
                            gesture.incorrect(2)
                            gesture.stop_robot()
                        else
                            Image.open("incorrect.png").show()
                        self.chatbot.change_speaker_lang('cn')
                        self.chatbot.say("下次再努力", 0.8)
            num += 1
        n = 1
        self.chatbot.change_speaker_lang('en')
        for s in score:
            self.chatbot.say("You got a score of {} in #{} test".format(s, n))
            if self.chatbot.isActing:
                gesture.pass_quiz() if s > .8 else gesture.fail_quiz()
            else:
                Image.open("pass_quiz.png").show() if s > .8 else Image.open("fail_quiz.png").show()
            n += 1


def get_quiz_info(chatbot, limit):
    error_msg = "Invalid input, please try again"
    invalid = invalid2 = invalid3 = True
    level = 0
    num_words = 0
    pos = 0
    while invalid:
        chatbot.say("Please answer in English. What is your hsk level?")
        temp = chatbot.listen()
        try:
            if 1 <= int(temp) <= 6:
                level = int(temp)
                invalid = False
            else:
                chatbot.say(error_msg)
        except ValueError:
            chatbot.say(error_msg)
    while invalid2:
        chatbot.say("How many words would you like to learn a session?")
        temp = chatbot.listen()
        try:
            num_words = int(temp)
            if num_words > limit:
                chatbot.say(error_msg)
            else:
                invalid2 = False
        except ValueError:
            chatbot.say(error_msg)
    while invalid3:
        chatbot.say("How many words did you leave off at last time?")
        temp = chatbot.listen()
        try:
            pos = int(temp)
            invalid3 = False
        except ValueError:
            chatbot.say(error_msg)
    return num_words, level, pos


def main():
    if platform.system() == 'Linux':
        pi = Chatbot(isActing=True)
    else:
        pi = Chatbot(isActing=False)  # add isActing = True to make robot move
    if pi.isActing:
        gesture.random_movement()
    pi.say("Hello, welcome back!", 1.1)
    try:
        while True:
            text = pi.listen()
            text = text.lower()
            if pi.isActing:
                gesture.random_movement()
            if pi.speaker_lang == 'cn':
                if "换成" in text and "英文" in text:
                    pi.say("开始说英文啦")
                    pi.change_speaker_lang('en')
                    pi.change_listener_lang('en')
                    pi.say("hello", generator=True)
                elif "开始" in text and "测验" in text:
                    pi.change_speaker_lang('en')
                    pi.change_listener_lang('en')
                    attrs = list(get_quiz_info(pi, 10000))
                    quizzer = Quiz(pi, attrs[0], attrs[1], attrs[2])
                    quizzer.init_quiz()
                    pi.change_speaker_lang('cn')
                    pi.change_listener_lang('cn')
                    pi.say("测验结束")
                elif "翻译" in text:
                    pi.say("请说一句话，我把它翻译成英文！")
                    to_translate = pi.listen()
                    to_translate = to_translate.lower()
                    pi.change_speaker_lang('en')
                    pi.say(media_translation.translate_text('en', to_translate))
                    pi.change_speaker_lang('cn')
                elif "再见" in text:
                    pi.say("下次见")
                    exit()
                elif "重复" in text and "英文" in text:
                    pi.change_speaker_lang('en')
                    pi.say(media_translation.translate_text('en', pi.last_phrase))
                    pi.change_speaker_lang('cn')
                else:
                    pi.say(text, generator=True)
            else:
                if "switch" in text and "chinese" in text:
                    pi.say("let's talk in chinese")
                    pi.change_speaker_lang('cn')
                    pi.change_listener_lang('cn')
                    pi.say("你好", generator=True)
                elif "start" in text and "quiz" in text:
                    # bot asks in english, user replies in chinese
                    attrs = list(get_quiz_info(pi, 10000))
                    quizzer = Quiz(pi, attrs[0], attrs[1], attrs[2])
                    quizzer.init_quiz()
                    pi.change_speaker_lang('en')
                    pi.change_listener_lang('en')
                    pi.say("Quiz completed")
                elif "translate" in text:
                    pi.say("Please say a phrase, I'll translate it into Chinese")
                    to_translate = pi.listen()
                    to_translate = to_translate.lower()
                    pi.change_speaker_lang('cn')
                    pi.say(media_translation.translate_text('zh-CN', to_translate))
                    pi.change_speaker_lang('en')
                elif "bye" in text:
                    pi.say("see you")
                    exit()
                elif "say yes" in text:
                    if pi.isActing:
                        gesture.correct(3)
                        gesture.stop_robot()
                    else:
                        Image.open("correct.png").show()
                elif "say no" in text:
                    if pi.isActing:
                        gesture.incorrect(3)
                        gesture.stop_robot()
                    else:
                        Image.open("incorrect.png").show()
                elif "repeat" in text and "chinese" in text:
                    pi.change_speaker_lang('cn')
                    pi.say(media_translation.translate_text('zh-CN', pi.last_phrase))
                    pi.change_speaker_lang('en')
                else:
                    pi.say(text, generator=True)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
