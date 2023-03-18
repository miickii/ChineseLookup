# import pinyin
# from chinese import ChineseAnalyzer
# import sqlite3
# import re
# import os
# from cedict_utils.cedict import CedictParser
# from main import db, app
# from models import Sentence, HSK, Cedict
# from analyzer import Analyzer

# analyzer = Analyzer()

# """------------------------------------------------------"""
# # RETRIEVE SENTENCES AND HSK WORDS
# """------------------------------------------------------"""
# def retrieve_sentences():
#     result = []
#     lines = []
#     chinese_analyzer = ChineseAnalyzer()
 
#     # open .tsv file
#     with open("files/sentence_pairs.tsv") as f:
    
#         # Read data line by line
#         for line in f:
            
#             # split data by tab
#             # store it in list
#             l=line.split('\t')
            
#             # append list to ans
#             lines.append(l)
    
#     # print data line by line
#     for i in lines:
#         chinese = i[1]
#         english = i[3]
#         english_clean = ""
#         pinyin_text = ""

#         # Convert characters to pinyin
#         text = chinese_analyzer.parse(chinese)
#         words = text.tokens()
#         for w in words:
#             pinyin_text += pinyin.get(w) + " "
        
#         # Modify english sentence to make it easier to search for words
#         # "I have a goal, it's (very) important to me!" would change to: " i have a goal it's very important to me " 
#         english_clean = english.lower()
#         english_clean = english_clean.rstrip('\n') # Remove endline that is added to all lines when reading text file above
#         english_clean = " " + english_clean + " " # Space is added to front and end so the first and last word is also included in database query (the query checks if sentence contains " " + text + " ")
#         english_clean = re.sub(r"[^\w\s']", "", english_clean) # \w: any word, \s any whitespace, ^ means match all but words, whitespace and ' character
        
#         result.append((chinese, pinyin_text, english, english_clean))
#     return result

# def retrieve_hsk_with_level():
#     result = []
#     con = sqlite3.connect("files/HSK.db")
#     cursor = con.cursor()
#     all_hsk = []

#     # fetchall() returns list of tuples: (chinese,)
#     # We only choose the first element from the tuple because the second is empty
#     # We convert all words to lowercase so they can be easily compared
#     cursor.execute("SELECT * FROM HSK1")
#     all_hsk.append([w for w in cursor.fetchall()])
#     cursor.execute("SELECT * FROM HSK2")
#     all_hsk.append([w for w in cursor.fetchall()])
#     cursor.execute("SELECT * FROM HSK3")
#     all_hsk.append([w for w in cursor.fetchall()])
#     cursor.execute("SELECT * FROM HSK4")
#     all_hsk.append([w for w in cursor.fetchall()])
#     cursor.execute("SELECT * FROM HSK5")
#     all_hsk.append([w for w in cursor.fetchall()])
#     cursor.execute("SELECT * FROM HSK6")
#     all_hsk.append([w for w in cursor.fetchall()])

#     for i, hsk in enumerate(all_hsk):
#         level = i + 1

#         for w in hsk:
#             c, p, e = w
#             frequency = analyzer.get_word_freq(c)
#             pos = analyzer.get_word_pos(c)

#             # if there are multiple english translations, add them each separately
#             if ';' in e or ',' in e:
#                 english_words = re.split(r"; |,", e) # Separate words by ; or ,
#                 for eng_word in english_words:
#                     new_eng_word = re.sub("[.]", "", eng_word) # Remove . from word
#                     new_eng_word = new_eng_word.strip()
#                     result.append((c, p, new_eng_word, pos, frequency, level)) # strip() removes leading and trailing whitespace

#             else:
#                 result.append((c, p, e, pos, frequency, level))

#     cursor.close()
#     con.close()

#     return result

# def retrieve_cedict():
#     parser = CedictParser()
#     entries = parser.parse()
#     result = []
#     for entry in entries:
#         c = entry.simplified
#         if "𰻝" in c:
#             continue
#         p_none = re.sub(r'\d+', '', entry.pinyin)
#         english = ""
#         for i, m in enumerate(entry.meanings):
#             if i+1 < len(entry.meanings):
#                 english += m + "; "
#             else:
#                 english += m + " "

#         frequency = analyzer.get_word_freq(c)
#         pos = analyzer.get_word_pos(c)
#         result.append((c, entry.traditional, pinyin.get(c), entry.pinyin, p_none, english, pos, frequency))
    
#     return result

# """------------------------------------------------------"""
# # ADD SENTENCES AND HSK WORDS TO SQLALCHEMY DATABASE
# """------------------------------------------------------"""
# def add_sentences():
#     sentences = retrieve_sentences()
#     print(len(sentences))
#     for s in sentences:
#         c, p, e, e_clean = s
#         sentence = Sentence(chinese=c, pinyin=p, english=e, english_clean=e_clean)
#         db.session.add(sentence)

# def add_hsk():
#     hsk = retrieve_hsk_with_level()
#     print(len(hsk))
#     for h in hsk:
#         c, p, e, pos, f, l = h
#         word = HSK(chinese=c, pinyin=p, english=e.lower(), pos=pos, frequency=f, level=l)
#         db.session.add(word)

# def add_cedict():
#     cedict = retrieve_cedict()
#     print(len(cedict))
#     for cd in cedict:
#         c, t, p, p_num, p_none, e, pos, f = cd
#         word = Cedict(chinese=c, chinese_traditional=t, pinyin=p, pinyin_numbers=p_num, pinyin_none=p_none, english=e, pos=pos, frequency=f)
#         db.session.add(word)
    
# """------------------------------------------------------"""
# # PRINT SENTENCES AND HSK WORDS FROM SQLALCHEMY DATABASE
# """------------------------------------------------------"""
# def print_sentences():
#     sentences = Sentence.query.all()
    
#     for s in sentences:
#         print(s.id)
#         print(s.chinese)
#         print(s.pinyin)
#         print(s.english)
#         print("Clean: " + s.english_clean)
#         print("\n")

#     print("Sentences: " + str(len(sentences)) + "\n")

# # Words: 5456
# # Words: 8963
# def print_hsk():
#     hsk = HSK.query.all()
#     pos_amt = 0
#     freq_amt = 0

#     for w in hsk:
#         print(w.id)
#         print(w.chinese)
#         print(w.pinyin)
#         print(w.english)

#         print(w.pos)
#         if w.pos != "":
#             pos_amt += 1
#         print(w.frequency)
#         if w.frequency > 0:
#             freq_amt += 1
        
#         print("Level: " + str(w.level))
#         print("\n")
    
#     print("pos: " + str(pos_amt) + "    freq: " + str(freq_amt))
#     print("Words: " + str(len(hsk)) + "\n")

# # Words: 118838
# def print_cedict():
#     cedict = Cedict.query.all()
#     pos_amt = 0
#     freq_amt = 0

#     for w in cedict:
#         print(w.id)
#         print(w.chinese)
#         print(w.chinese_traditional)
#         print(w.pinyin)
#         print(w.pinyin_numbers)
#         print(w.pinyin_marks)
#         print(w.english)

#         print(w.pos)
#         if w.pos != "":
#             pos_amt += 1
#         print(w.frequency)
#         if w.frequency != 0.0:
#             freq_amt += 1
#         print("\n")
    
#     print("pos: " + str(pos_amt) + "    freq: " + str(freq_amt))
#     print("Words: " + str(len(cedict)) + "\n")

# def print_db_tables():
#     # table_names = []
#     # for clazz in db.Model._decl_class_registry.values():
#     #     try:
#     #         table_names.append(clazz.__tablename__)
#     #     except:
#     #         pass
    
#     table_names = [(mapper.class_.__name__, mapper.column_attrs) for mapper in db.Model.registry.mappers]
    
#     for table in table_names:
#         print("Name: " + table[0])
#         print("Coluns:")
#         for column in table[1]:
#             print(column.key)
#         print("\n")

# # Init db, create all tables and add all data with above functions (PREVIOUS DATABASE SHOULD BE DELETED BEFORE)
# def rebuild_database(test=False):
#     if test and os.path.exists("app_test.db"):
#         os.remove("app_test.db")
#     elif os.path.exists("app.db"):
#         os.remove("app.db") 
    
#     db.create_all()

#     # Add sentences and hsk to database
#     add_sentences()
#     add_hsk()
#     add_cedict()


# # WORK WITH DATABASE (activates a Flask context)
# def handle_database(commit=False):
#     with app.app_context():
#         # NEEDS commit=True
#         #db.create_all() #ONLY USE WHEN NEW CLASSES ARE ADDED (doesn't overwrite or change others)
#         #add_sentences() READDS IF ALREADY ADDED
#         #add_hsk(True) READDS IF ALREADY ADDED
#         #add_cedict() READDS IF ALREADY ADDED
#         rebuild_database() #DOES EVERYTHING ABOVE
#         #empty_profile_db()

#         # DOESN'T NEED commit=True
#         #print_sentences()
#         #print_hsk()
#         #print_hsk_clean()
#         #print_cedict()
#         #print_db_tables()

#         # print(len(chinese))
#         # print(len(freqs))
#         # print(len(ps))

#         if commit:
#             db.session.commit()



# handle_database(commit=True)

# # Checking if hsk with level is the same size as hsk in database
# # hsk = retrieve_hsk_with_level(False)
# # hskother = retrieve_hsk(False)
# # print(len(hsk))
# # print(len(hskother))

# # Commit db session
# #handle_database(commit=True)

