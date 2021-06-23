#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import pandas as pd
import stt
import tts
from DiabloGPT import Chat
from chinese_convo import chinese_chatbot
from language_detect import detect_language


class Chatbot:
    def __init__(self) -> None:
        self.listener = stt.Listener()
        self.speaker = tts.Speaker()
        self.chat = Chat()
        self.isActing = True
        self.isChinese = False

    def say(self, text, speed=1, generator=False):
        if generator:
            if self.isChinese:
                self.speaker.speak(chinese_chatbot(text), speed)
            else:
                self.chat.raw(text)
                self.speaker.speak(self.chat.generated_text(), speed)
        else:
            self.speaker.speak(self, text, speed)

    def listen(self):
        return self.listener.listens()


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
        repeat = True
        for word in self.quiz_list.rows:
            temp_li.append((word['chinese'], word['english']))
        while temp_li or not num:
            li_len = len(temp_li)
            random.shuffle(temp_li)
            for el in temp_li:
                Quiz.say(self, "Please provide the definition of" + el[0] + "in english")  # el[0] is in chinese
                user_input = Quiz.listen(self)
                score[num] += 1, temp_li.remove(el) if user_input == el[1] else score
            score[num] /= li_len
            num += 1
        n = 1
        for s in score:
            tts.tts("You got a score of {} in #{} test".format(s, n))
            if self.isActing:
                gesture.happy() if s > .8 else gesture.sad()
            n += 1


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
    pi.say("hello", 1.3)
    try:
        while True:
            text = pi.listen()
            if detect_language(text) == 'cn':
                pi.isChinese = True
                pi.say(text,generator=True)
            elif text.contains("start" and "quiz"):
                attrs = list(get_quiz_info(pi))
                quizzer = Quiz(attrs[0], attrs[1], attrs[2])
                quizzer.init_quiz()
                pi.say("Quiz completed")
            elif text == "bye":
                pi.say("goodbye")
                exit()
            else:
                pi.say(text, generator=True)

            print(text)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
