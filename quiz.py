import pandas as pd
import tts
import random
import pronounce
import gesture


class Quiz:
    def __init__(self, pos, num_words, level):
        self.pos = pos
        self.num_words = num_words
        self.level = level
        self.word_list = pd.DataFrame
        self.quiz_list = pd.DataFrame

    def get_words(self):
        hsk = pd.read_table("hsk_{}.csv".format(self.level))
        self.word_list = hsk.iloc[self.pos:self.pos + self.num_words, :]
        if self.quiz_list.empty:
            self.quiz_list = self.word_list
        else:
            self.quiz_list = pd.concat(self.quiz_list, self.word_list)
        print(self.word_list.head())
        self.pos += self.num_words

    def iter_output(self):
        for word in self.quiz_list.rows:
            tts.tts(word['character'])

    def init_quiz(self):
        num = 0
        temp_li = []
        score = []
        for word in self.quiz_list.rows:
            temp_li.append(word['character'])
        while temp_li or not num:
            li_len = len(temp_li)
            random.shuffle(temp_li)
            for el in temp_li:
                tts.tts(el)
                score[num] += 1, temp_li.remove(el) if pronounce.pronounce(el) > .8 else score
            score[num] /= li_len
            num += 1
        n = 1
        for s in score:
            tts.tts("You got a score of {} in #{} test".format(s, n))
            gesture.happy() if s > .8 else gesture.sad()
            n += 1

