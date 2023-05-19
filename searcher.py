from models import Sentence, HSK, Cedict
from analyzer import Analyzer
import pinyin
import re

class Searcher:
    def __init__(self):
        self.hsk = HSK.query.all()
        self.analyzer = Analyzer()

    # Starts by looking for word in HSK database, if not found it will scrape train chinese
    def search_word(self, word):
        results = self.search_hsk(word)
        
        # Search Cedict database with chinese and pinyin
        if len(results) == 0:
            results = self.search_cedict(word, pinyin=word)

        # Add example sentences to all results
        for r in results:
            # Search through all sentences and add to examples if they contain the chinese
            r["examples"] = self.get_sentences_containing(r["chinese"])
        
        # Sort the results by frequency
        results = self.analyzer.sort_words_by_freq(results)

        return results 

    def search_hsk(self, text):
        results = []
        for w in self.hsk:
            c, e = w.chinese, w.english
            # Check if input text matches either this words chinese, english or pinyin
            if c == text or e == text or pinyin.get(c, format="strip") == text:
                # First check if one of the other results has the same chinese character (if the word is english, there could be multiple chinese characters with same meaning)
                already_found = False
                for r in results:
                    if r["chinese"] == c:
                        # Add this alternate english meaning to the result
                        r["english"] += "; " + e
                        already_found = True
                
                # If this is a new chinese character, add it to results
                if not already_found:
                    #results.append({"id": w.id, "chinese" : c, "pinyin" : w.pinyin, "english" : e, "examples" : [], "frequency": w.frequency})
                    results.append(self.word_json(w, source="HSK"))
        
        return results

    def search_cedict(self, chinese, pinyin=None):
        cedict = Cedict.query.filter_by(chinese=chinese).all()
        if len(cedict) == 0:
            # Search by pinyin
            cedict = Cedict.query.filter_by(pinyin_none=pinyin).all()
        
        return [self.word_json(cd, source="CEDICT") for cd in cedict]

    # Takes in a word and returns a formatted json object that can be returned as response by api
    def word_json(self, word, source="", split_characters=False):
        traditional, level, pinyin_numbers = None, None, None
        sentence_c, sentence_p, sentence_e = "", "", ""
        try:
            sentence_c, sentence_p, sentence_e = word.split(";")
        except:
            pass
        try:
            traditional = word.chinese_traditional
        except:
            pass
        try:
            level = word.level
        except:
            pass
        
        try:
            pinyin_numbers = word.pinyin_numbers
        except:
            pass

        return {"id": word.id, "chinese": self.analyzer.split_characters(word.chinese) if split_characters else word.chinese, "chinese_traditional": traditional, "pinyin": word.pinyin, "pinyin_numbers": pinyin_numbers, "english" : word.english, "short_english": re.split(r"; |,", word.english)[0], "examples" : [], "pos": word.pos, "frequency": word.frequency, "level": level, "source": source, "sentence_chinese": sentence_c, "sentence_pinyin": sentence_p, "sentence_english": sentence_e}
    
    def profile_word_json(self, word):
        sentence_c, sentence_p, sentence_e = word.split(";")
        return {"id": word.id, "chinese": word.chinese, "chinese_traditional": word.chinese_traditional, "pinyin": word.pinyin, "english" : word.english, "short_english": re.split(r"; |,", word.english)[0], "examples" : [], "pos": word.pos, "frequency": word.frequency, "level": word.level, "categories": [cat.name for cat in word.categories], "sentence_chinese": sentence_c, "sentence_pinyin": sentence_p, "sentence_english": sentence_e}
    
    # Breaks down sentence into tokens and returns words from database
    def analyze_sentence(self, chinese):
        tokens = self.analyzer.tokenize(chinese)
        all_pinyin = ""
        words = []
        for c in tokens:
            e, p, pos = self.search_cedict_simple(c)
            all_pinyin += p + " "

            words.append({"chinese" : c, "pinyin": p, "english": e, "pos": pos})

        sentence = Sentence.query.filter_by(chinese=chinese).first()
        return {"sentence" : {"chinese": chinese, "pinyin": all_pinyin, "english": "" if not sentence else sentence.english}, "words": words}

    # Only returns english, pinyin and pos translation of character
    def search_cedict_simple(self, chinese):
        word = Cedict.query.filter_by(chinese=chinese).first()

        if word:
            return word.english, word.pinyin, word.pos
        else:
            return "", pinyin.get(chinese), self.analyzer.get_word_pos(chinese)

    def get_sentences_containing(self, chinese=None, english=None):
        sentences = []
        if chinese:
            sentences = Sentence.query.filter(Sentence.chinese.contains(chinese)).all()
        if english:
            sentences.extend(Sentence.query.filter(Sentence.english_clean.contains(" " + english + " ")).all())
            
        return [{"chinese": s.chinese, "pinyin": s.pinyin, "english": s.english} for s in sentences]
