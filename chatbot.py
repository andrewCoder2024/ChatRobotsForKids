#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import pandas as pd
import stt, tts
# from DiabloGPT import Chat
from chinese_convo import chinese_chatbot
import gesture
#from multiprocessing import Process,Pipe
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
        self.train()

    def train(self):
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
                self.speaker.speak(self.chat.get_response(text), speed)
                # self.speaker.speak(text, speed)
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


class Quiz(Chatbot):
    def __init__(self, num_words=10, level=1, pos=0):
        super().__init__()
        self.pos = pos
        self.num_words = num_words
        self.level = level
        self.word_list = pd.DataFrame
        self.quiz_list = pd.DataFrame

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
                Quiz.say(self, el)

    def init_quiz(self):
        num = 0
        temp_li = []
        score = {}
        Quiz.get_words(self)
        for index, row in self.quiz_list.iterrows():
            temp_li.append((row['chinese'], row['english']))
        while temp_li or not num:
            random.shuffle(temp_li)
            for el in temp_li:
                res = random.randint(0, 1)
                if res:
                    Quiz.change_speaker_lang(self, 'en')
                    Quiz.say(self, "Please provide the definition of" + el[1] + "in chinese")  # el[0] is in chinese
                else:
                    Quiz.change_speaker_lang(self, 'cn')
                    Quiz.say(self, "请告诉我英文怎么说 " + el[0])
                user_input = Quiz.listen(self)
                if res:
                    if user_input == el[0]:
                        score[num] += 1
                        temp_li.remove(el)
                        gesture.correct(2)
                        gesture.stop_robot()
                    else:
                        gesture.incorrect(2)
                        gesture.stop_robot()
                else:
                    if user_input == el[1]:
                        score[num] += 1
                        temp_li.remove(el)
                        gesture.correct(2)
                        gesture.stop_robot()
                    else:
                        gesture.incorrect(2)
                        gesture.stop_robot()
            num += 1
        n = 1
        for s in score:
            Quiz.say(self, "You got a score of {} in #{} test".format(s, n))
            if self.isActing:
                gesture.pass_quiz() if s > .8 else gesture.fail_quiz()
            n += 1
        Quiz.change_speaker_lang(self, self.speaker_lang)
        Quiz.change_listener_lang(self, self.listener_lang)


def get_quiz_info(chatbot, limit):
    error_msg = "Invalid input, please try again"
    invalid = invalid2 = invalid3 = True
    level = 0
    num_words = 0
    pos = 0
    while invalid:
        chatbot.say("What is your hsk level?")
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
                elif "开始" and "测验" in text:
                    attrs = list(get_quiz_info(pi, 10000))
                    quizzer = Quiz(attrs[0], attrs[1], attrs[2])
                    quizzer.init_quiz()
                    pi.say("测验结束")
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
                elif "start" and "quiz" in text:
                    # bot asks in english, user replies in chinese
                    attrs = list(get_quiz_info(pi, 10000))
                    quizzer = Quiz(attrs[0], attrs[1], attrs[2])
                    quizzer.init_quiz()
                    pi.say("Quiz completed")
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
