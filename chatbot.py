#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import pandas as pd
import stt
import tts
#from DiabloGPT import Chat
from chinese_convo import chinese_chatbot
import gesture

class Chatbot:
    def __init__(self, isActing=True, sLang='en', lLang='en'):
        self.listener = stt.Listener()
        self.speaker = tts.Speaker()
        #self.chat = Chat()
        self.isActing = isActing
        self.speaker_lang = sLang
        self.listener_lang = lLang

    def say(self, text, speed=1, generator=False):
        if generator:
            if self.speaker_lang == 'cn':
                self.speaker.speak(chinese_chatbot(text), speed)
            else:
                pass
                self.speaker.speak(text, speed)
                #self.chat.raw(text) # from GPT
                #self.speaker.speak(self.chat.generated_text(), speed)
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
        print(self.word_list.head())
        self.pos += self.num_words

    def iter_output(self):
        for word in self.quiz_list.rows:
            for el in word:
                Quiz.say(self, el)

    def init_quiz(self):
        num = 0
        temp_li = []
        score = []
        Quiz.get_words(self)
        for word in self.quiz_list.rows:
            temp_li.append((word['chinese'], word['english']))
        Quiz.change_listener_lang(self, 'cn')
        while temp_li or not num:
            li_len = len(temp_li)
            random.shuffle(temp_li)
            for el in temp_li:
                Quiz.say(self, "Please provide the definition of" + el[1] + "in chinese")  # el[0] is in chinese
                # can' mix languages
                user_input = Quiz.listen(self)
                score[num] += 1, temp_li.remove(el) if user_input == el[1] else score
            num += 1
        n = 1
        for s in score:
            tts.speak("You got a score of {} in #{} test".format(s, n))
            if self.isActing:
                gesture.correct() if s > .8 else gesture.incorrect()
            n += 1
        Quiz.change_listener_lang(self, 'en')

def get_quiz_info(chatbot):
    chatbot.say("What is your hsk level?")
    temp = chatbot.listen()
    level = 0
    try:
        if 1 <= int(temp) <= 6:
            level = int(temp)
        else:
            chatbot.say("Invalid Input")
    except ValueError:
        chatbot.say("Invalid input")
    chatbot.say("How many words would you like to learn a session?")
    temp = chatbot.listen()
    num_words = 0
    try:
        num_words = int(temp)
    except ValueError:
        chatbot.say("Invalid Input")
    chatbot.say("How many words did you leave off at last time?")
    temp = chatbot.listen()
    pos = 0
    try:
        pos = int(temp)
    except ValueError:
        chatbot.say("Invalid Input")
    return num_words, level, pos


def main():
    pi = Chatbot()
    pi.say("hello", 1)
    try:
        while True:
            text = pi.listen()
            print(text)
            if pi.speaker_lang == 'cn':
                if "换成" and "英文" in text:
                    pi.say("开始说英文啦")
                    pi.change_speaker_lang('en')
                    pi.change_listener_lang('en')
                    pi.say(text, generator=True)
                elif "开始" and "测验" in text:
                    pass
                    # bot asks in chinese, user replies in english
                    pi.say("测验结束")
                elif text == "再见":
                    pi.say("下次见")
                    exit()
                else:
                    pi.say(text, generator=True)
            else:
                if "switch" and "Chinese" in text:
                    print("switching")
                    pi.say("let's talk in chinese")
                    pi.change_speaker_lang('cn')
                    pi.change_listener_lang('cn')
                    pi.say(text, generator=True)
                elif "start" and "quiz" in text:
                    # bot asks in english, user replies in chinese
                    attrs = list(get_quiz_info(pi))
                    quizzer = Quiz(attrs[0], attrs[1], attrs[2])
                    quizzer.init_quiz()
                    pi.say("Quiz completed")
                elif text == "bye":
                    pi.say("goodbye")
                    exit()
                else:
                    pi.say(text, generator=True)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
