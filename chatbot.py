#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from audio import media_translation
import pandas as pd
import stt, tts
# from DiabloGPT import Chat
from chinese_convo import chinese_chatbot
import gesture
import time
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

class Chatbot:
    def __init__(self, isActing=True, sLang='en', lLang='en'):
        self.listener = stt.Listener()
        self.speaker = tts.Speaker()
        # self.chat = Chat()
        self.isActing = isActing
        self.speaker_lang = sLang
        self.listener_lang = lLang
        self.chat = ChatBot('Raspberry Pi')
        self.trainer = ChatterBotCorpusTrainer(self.chat)
        self.trainer.train("chatterbot.corpus.english.greetings")
        self.trainer.train("chatterbot.corpus.english.conversations")

    def training(self):
        # Train the chatbot based on the english corpus
        self.trainer.train("chatterbot.corpus.english")
        # Train based on english greetings corpus
        self.trainer.train("chatterbot.corpus.english.greetings")
        # Train based on the english conversations corpus
        self.trainer.train("chatterbot.corpus.english.conversations")

    def say(self, text, speed=1, generator=False):
        if generator:
            if self.speaker_lang == 'cn':
                self.speaker.speak(chinese_chatbot(text), speed)
            else:
                self.speaker.speak(str(self.chat.get_response(text)), speed)
                #self.speaker.speak(text, speed)
                # self.chat.raw(text) # from GPT
                # self.speaker.speak(self.chat.generated_text(), speed)
        else:
            self.speaker.speak(text, speed)

    def listen(self):
        return self.listener.listens()

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
        hsk = pd.read_csv("hsk_csv-master/hsk{}.csv".format(self.level), names=['chinese', 'pinyin', 'english'])
        self.word_list = hsk.iloc[self.pos:self.pos + self.num_words, :]
        if self.quiz_list.empty:
            self.quiz_list = self.word_list
        else:
            self.quiz_list = pd.concat(self.quiz_list, self.word_list)
        #print(self.word_list.head())
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
            temp_li.append((row['chinese'], row['english']))
        while temp_li or not num:
            random.shuffle(temp_li)
            score[num] = 0
            for el in temp_li:
                res = random.randint(0, 1)
                if res:
                    self.chatbot.change_speaker_lang('en')
                    self.chatbot.say("Please provide the definition of" + el[1] + "in chinese")  # el[0] is in chinese
                    self.chatbot.change_listener_lang('cn')
                else:
                    self.chatbot.change_speaker_lang('cn')
                    self.chatbot.say("请用英文说 " + el[0])
                    self.chatbot.change_listener_lang('en')
                user_input = self.chatbot.listen()
                user_input = user_input.lower()
                print(user_input)
                no_response_msg = "I didn't catch that. Say again?"
                no_response_msg_cn = "没听清，可以再说一遍吗？"
                no_response = True if user_input == "i didn't catch that. say again?" else False
                while no_response:
                    if self.chatbot.speaker_lang == 'en':
                        self.chatbot.say(no_response_msg)
                    else:
                        self.chatbot.say(no_response_msg_cn)
                    user_input = self.chatbot.listen()
                    user_input = user_input.lower()
                    print(user_input)
                    no_response = True if user_input == "i didn't catch that. say again?" else False
                if res:
                    if el[0] in user_input:
                        score[num] += 1
                        temp_li.remove(el)
                        gesture.correct(2)
                        gesture.stop_robot()
                    else:
                        gesture.incorrect(2)
                        gesture.stop_robot()
                else:
                    if el[1] in user_input:
                        score[num] += 1
                        temp_li.remove(el)
                        gesture.correct(2)
                        gesture.stop_robot()
                    else:
                        gesture.incorrect(2)
                        gesture.stop_robot()
            num += 1
        n = 1
        self.chatbot.change_speaker_lang('en')
        for s in score:
            self.chatbot.say("You got a score of {} in #{} test".format(s, n))
            if self.chatbot.isActing:
                gesture.pass_quiz() if s > .8 else gesture.fail_quiz()
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
        print(temp)
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
        print(temp)
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
        print(temp)
        try:
            pos = int(temp)
            invalid3 = False
        except ValueError:
            chatbot.say(error_msg)
    return num_words, level, pos


def main():
    pi = Chatbot()
    gesture.random_movement()
    pi.say("Hello, welcome back!", 1.1)
    try:
        while True:
            text = pi.listen()
            print(text)
            text = text.lower()
            gesture.random_movement()
            if pi.speaker_lang == 'cn':
                if "换成" and "英文" in text:
                    pi.say("开始说英文啦")
                    pi.change_speaker_lang('en')
                    pi.change_listener_lang('en')
                    pi.say("hello", generator=True)
                elif text == "i didn't catch that. say again?":
                    pi.say("我沒有听清楚，再说一遍？", generator=False)
                elif "开始" and "测验" in text:
                    pi.change_speaker_lang('en')
                    pi.change_listener_lang('en')
                    attrs = list(get_quiz_info(pi, 10000))
                    quizzer = Quiz(pi, attrs[0], attrs[1], attrs[2])
                    quizzer.init_quiz()
                    pi.change_speaker_lang('cn')
                    pi.change_listener_lang('cn')
                    pi.say("测验结束")
                elif "翻译" in text:
                    invalid = True
                    while invalid:
                        pi.say("请说一句话，我把它翻译成英文！")
                        to_translate = pi.listen()
                        to_translate = to_translate.lower()
                        if "i didn't catch that. say again?" not in to_translate:
                            invalid = False
                        if invalid:
                            pi.say("请再说一次")
                    pi.change_speaker_lang('en')
                    pi.say(media_translation.translate_text('en', to_translate))
                    pi.change_speaker_lang('cn')
                elif "再见" in text:
                    pi.say("下次见")
                    exit()
                else:
                    pi.say(text, generator=True)
            else:
                if "switch" and "chinese" in text:
                    pi.say("let's talk in chinese")
                    pi.change_speaker_lang('cn')
                    pi.change_listener_lang('cn')
                    pi.say("你好", generator=True)
                elif text == "i didn't catch that. say again?":
                    pi.say(text, generator=False)
                elif "start" and "quiz" in text:
                    # bot asks in english, user replies in chinese
                    attrs = list(get_quiz_info(pi, 10000))
                    quizzer = Quiz(pi, attrs[0], attrs[1], attrs[2])
                    quizzer.init_quiz()
                    pi.change_speaker_lang('en')
                    pi.change_listener_lang('en')
                    pi.say("Quiz completed")
                elif "translate" in text:
                    invalid = True
                    pi.say("Please say a phrase, I'll translate it into Chinese")
                    while invalid:
                        to_translate = pi.listen()
                        to_translate = to_translate.lower()
                        if "i didn't catch that. say again?" not in to_translate:
                            invalid = False
                        if invalid:
                            pi.say("Can you repeat that?")
                    pi.change_speaker_lang('cn')
                    pi.say(media_translation.translate_text('zh-CN', to_translate))
                    pi.change_speaker_lang('en')
                elif "bye" in text:
                    pi.say("see you")
                    exit()
                elif "say yes" in text:
                    gesture.correct(3)
                    gesture.stop_robot()
                elif "say no" in text:
                    gesture.incorrect(3)
                    gesture.stop_robot()
                else:
                    pi.say(text, generator=True)
                gesture.random_movement()
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
