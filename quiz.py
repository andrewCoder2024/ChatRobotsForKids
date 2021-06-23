import random
import pandas as pd


class Quiz:
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
        score = {}
        Quiz.get_words(self)
        print("test", self.quiz_list)
        for index, row in self.quiz_list.iterrows():
            temp_li.append((row['chinese'], row['english']))
        print(temp_li)
        while temp_li or not num:
            score[num] = 0
            li_len = len(temp_li)
            random.shuffle(temp_li)
            print("test 2",temp_li)
            for el in temp_li:
                # Quiz.say(self, "Please provide the definition of" + el[0] + "in english")   el[0] is in chinese
                user_input = input("What is the english definition of " + el[0])
                print("score test",score[num])
                if user_input == el[1]:
                    score[num] += 1
                    temp_li.remove(el)
            score[num] /= li_len
            num += 1
        n = 1
        for s in score:
            print("You got a score of {} in #{} test".format(s, n))
            n += 1


quizzer = Quiz()

quizzer.init_quiz()
