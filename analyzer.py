import jieba
import jieba.posseg as posseg # For splitting sentences
from wordfreq import word_frequency
import os.path
import re

class Analyzer:
    def __init__(self):
        self.jieba_dict_path = os.path.join(os.path.dirname(__file__), "files/jieba_dict.txt")
        self.load_dict()

    def load_dict(self):
        """
        Load dictionary
        """
        if not os.path.exists(self.jieba_dict_path):
            print("jieba dictionary not found")
            return

        jieba.load_userdict(self.jieba_dict_path)

    # Get Parts Of Speech for word
    def get_word_pos(self, word):
        words = posseg.cut(word)
        flags = []
        for w in words:
            flags.append(w.flag)

        if len(flags) == 1:
            return flags[0]
        
        return ""
    
    def get_word_freq(self, word):
        return word_frequency(word, 'zh')
    
    # Splits a chinese text into individual words
    def tokenize(self, text):
        return [tk for tk in jieba.lcut(text, cut_all=False) if (tk not in ' 。，“”--：；')]
    
    # Splits chinese word into each seperate character, returns array where first element is the word and second is the list of characters
    def split_characters(self, word):
        # Some words in the HSK database also has example usage in parenthesis, which should be ignored.
        # only_word = word.split('（')[0]
        only_word = re.split(r'[(（]', word)[0].strip()
        return [only_word, [c for c in only_word]]
    
    # Takes in a list of chinese words from database and orders them by their frequency
    def sort_words_by_freq(self, words):
        frequencies = [w['frequency'] for w in words]
        
        # for w in words:
        #     freq = self.get_word_freq(w)
        #     frequencies.append(freq if freq else 0)
        
        # Here sorted returns the indicies to frequencies after it's sorted
        # range(len(frequencies)) is an iterable that loops over length of the frequencies list
        # key is a function. This function takes the value from the iterable and returns a transformed value.
        # Its the transformed values that get's sorted
        # .__getitem__ is a magic method that gives the value at an index. If the range iterable is at 2, __getitem__ would return frequencies[2]
        indicies = sorted(range(len(frequencies)), key=frequencies.__getitem__, reverse=True) # reverse because we want the highest score to be first
        # ALTERNATIVELY: sorted(range(len(s)), key=lambda k: s[k])

        # PRINTING ORDERED FREQUENCIES
        # for i in range(len(words)):
        #     print(words[i]['chinese'] + "   " + str(frequencies[i]))
        # With the indicies list we can now get the sorted sequence for words as well as their frequencies
        return [words[i] for i in indicies]
    
        