import pinyin
from chinese import ChineseAnalyzer
import sqlite3
import re
import os
from cedict_utils.cedict import CedictParser
from main import db, app
from models import Sentence, HSK, Cedict, Custom, Category, custom_category
from analyzer import Analyzer

analyzer = Analyzer()

"""------------------------------------------------------"""
# RETRIEVE SENTENCES AND HSK WORDS
"""------------------------------------------------------"""
def retrieve_sentences():
    result = []
    lines = []
    chinese_analyzer = ChineseAnalyzer()
 
    # open .tsv file
    with open("files/sentence_pairs.tsv") as f:
    
        # Read data line by line
        for line in f:
            
            # split data by tab
            # store it in list
            l=line.split('\t')
            
            # append list to ans
            lines.append(l)
    
    # print data line by line
    for i in lines:
        chinese = i[1]
        english = i[3]
        english_clean = ""
        pinyin_text = ""

        # Convert characters to pinyin
        text = chinese_analyzer.parse(chinese)
        words = text.tokens()
        for w in words:
            pinyin_text += pinyin.get(w) + " "
        
        # Modify english sentence to make it easier to search for words
        # "I have a goal, it's (very) important to me!" would change to: " i have a goal it's very important to me " 
        english_clean = english.lower()
        english_clean = english_clean.rstrip('\n') # Remove endline that is added to all lines when reading text file above
        english_clean = " " + english_clean + " " # Space is added to front and end so the first and last word is also included in database query (the query checks if sentence contains " " + text + " ")
        english_clean = re.sub(r"[^\w\s']", "", english_clean) # \w: any word, \s any whitespace, ^ means match all but words, whitespace and ' character
        
        result.append((chinese, pinyin_text, english, english_clean))
    return result

def retrieve_hsk_with_level():
    result = []
    con = sqlite3.connect("files/HSK.db")
    cursor = con.cursor()
    all_hsk = []

    # fetchall() returns list of tuples: (chinese,)
    # We only choose the first element from the tuple because the second is empty
    # We convert all words to lowercase so they can be easily compared
    cursor.execute("SELECT * FROM HSK1")
    all_hsk.append([w for w in cursor.fetchall()])
    cursor.execute("SELECT * FROM HSK2")
    all_hsk.append([w for w in cursor.fetchall()])
    cursor.execute("SELECT * FROM HSK3")
    all_hsk.append([w for w in cursor.fetchall()])
    cursor.execute("SELECT * FROM HSK4")
    all_hsk.append([w for w in cursor.fetchall()])
    cursor.execute("SELECT * FROM HSK5")
    all_hsk.append([w for w in cursor.fetchall()])
    cursor.execute("SELECT * FROM HSK6")
    all_hsk.append([w for w in cursor.fetchall()])

    for i, hsk in enumerate(all_hsk):
        level = i + 1

        for w in hsk:
            c, p, e = w
            frequency = analyzer.get_word_freq(c)
            pos = analyzer.get_word_pos(c)

            # if there are multiple english translations, add them each separately
            if ';' in e or ',' in e:
                english_words = re.split(r"; |,", e) # Separate words by ; or ,
                for eng_word in english_words:
                    new_eng_word = re.sub("[.]", "", eng_word) # Remove . from word
                    new_eng_word = new_eng_word.strip()
                    result.append((c, p, new_eng_word, pos, frequency, level)) # strip() removes leading and trailing whitespace

            else:
                result.append((c, p, e, pos, frequency, level))

    cursor.close()
    con.close()

    return result

def retrieve_cedict():
    parser = CedictParser()
    entries = parser.parse()
    result = []
    for entry in entries:
        c = entry.simplified
        if "𰻝" in c:
            continue
        p_none = re.sub(r'\d+', '', entry.pinyin)
        english = ""
        for i, m in enumerate(entry.meanings):
            if i+1 < len(entry.meanings):
                english += m + "; "
            else:
                english += m + " "

        frequency = analyzer.get_word_freq(c)
        pos = analyzer.get_word_pos(c)
        result.append((c, entry.traditional, pinyin.get(c), entry.pinyin, p_none, english, pos, frequency))
    
    return result

"""------------------------------------------------------"""
# ADD SENTENCES AND HSK WORDS TO SQLALCHEMY DATABASE
"""------------------------------------------------------"""
def add_sentences():
    sentences = retrieve_sentences()
    print(len(sentences))
    for s in sentences:
        c, p, e, e_clean = s
        sentence = Sentence(chinese=c, pinyin=p, english=e, english_clean=e_clean)
        db.session.add(sentence)

def add_hsk():
    hsk = retrieve_hsk_with_level()
    print(len(hsk))
    for h in hsk:
        c, p, e, pos, f, l = h
        print(e)
        word = HSK(chinese=c, pinyin=p, english=e.lower(), pos=pos, frequency=f, level=l)
        db.session.add(word)

def add_cedict():
    cedict = retrieve_cedict()
    print(len(cedict))

    for cd in cedict:
        c, t, p, p_num, p_none, e, pos, f = cd
        word = Cedict(chinese=c, chinese_traditional=t, pinyin=p, pinyin_numbers=p_num, pinyin_none=p_none, english=e, pos=pos, frequency=f)
        db.session.add(word)
    
"""------------------------------------------------------"""
# PRINT SENTENCES AND HSK WORDS FROM SQLALCHEMY DATABASE
"""------------------------------------------------------"""
def print_sentences():
    sentences = Sentence.query.all()
    
    for s in sentences:
        print(s.id)
        print(s.chinese)
        print(s.pinyin)
        print(s.english)
        print("Clean: " + s.english_clean)
        print("\n")

    print("Sentences: " + str(len(sentences)) + "\n")

# Words: 5456
# Words: 8963
def print_hsk():
    hsk = HSK.query.all()
    pos_amt = 0
    freq_amt = 0

    for w in hsk:
        print(w.id)
        print(w.chinese)
        print(w.pinyin)
        print(w.english)

        print(w.pos)
        if w.pos != "":
            pos_amt += 1
        print(w.frequency)
        if w.frequency > 0:
            freq_amt += 1
        
        print("Level: " + str(w.level))
        print("\n")
    
    print("pos: " + str(pos_amt) + "    freq: " + str(freq_amt))
    print("Words: " + str(len(hsk)) + "\n")

# Words: 118838
def print_cedict():
    cedict = Cedict.query.all()
    pos_amt = 0
    freq_amt = 0

    for w in cedict:
        print(w.id)
        print(w.chinese)
        print(w.chinese_traditional)
        print(w.pinyin)
        print(w.pinyin_numbers)
        print(w.pinyin_marks)
        print(w.english)

        print(w.pos)
        if w.pos != "":
            pos_amt += 1
        print(w.frequency)
        if w.frequency != 0.0:
            freq_amt += 1
        print("\n")
    
    print("pos: " + str(pos_amt) + "    freq: " + str(freq_amt))
    print("Words: " + str(len(cedict)) + "\n")

def print_db_tables():
    # table_names = []
    # for clazz in db.Model._decl_class_registry.values():
    #     try:
    #         table_names.append(clazz.__tablename__)
    #     except:
    #         pass
    
    table_names = [(mapper.class_.__name__, mapper.column_attrs) for mapper in db.Model.registry.mappers]
    
    for table in table_names:
        print("Name: " + table[0])
        print("Coluns:")
        for column in table[1]:
            print(column.key)
        print("\n")

def build_custom():
    con_old = sqlite3.connect("files/curr_custom.db")
    cursor_old = con_old.cursor()

    # Categories
    cursor_old.execute("SELECT * FROM Category")
    categories_old = cursor_old.fetchall()
    for c in categories_old:
        category = Category(id=c[0], name=c[1])
        db.session.add(category)
        #cursor_new.execute("INSERT INTO Category VALUES (?, ?)", (c[0], c[1]))

    # Words
    cursor_old.execute("SELECT * FROM Word")
    words_old = cursor_old.fetchall()
    for i in range(len(words_old)):
        custom = Custom(id=words_old[i][0], chinese=words_old[i][2], chinese_traditional=words_old[i][3], pinyin=words_old[i][4], english=words_old[i][5], pos=words_old[i][6], frequency=words_old[i][7], level=words_old[i][8], srs=words_old[i][9])
        db.session.add(custom)
        #cursor_new.execute("INSERT INTO Custom VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (words_old[i][0], words_old[i][2], words_old[i][3], words_old[i][4], words_old[i][5], words_old[i][6], words_old[i][7], words_old[i][8], words_old[i][9]))
    
    db.session.commit()

    # Relationship
    cursor_old.execute("SELECT * FROM word_category")
    links_old = cursor_old.fetchall()
    for l in links_old:
        custom = Custom.query.filter_by(id=l[0]).first()
        category = Category.query.filter_by(id=l[1]).first()
        if custom is not None and category is not None:
            print(custom.english, category.name)
            custom.categories.append(category)

        #cursor_new.execute("INSERT INTO custom_category VALUES (?, ?)", (l[0], l[1]))

    db.session.commit()
    # con_new.commit()
    # con_new.close()
    con_old.close()

# Init db, create all tables and add all data with above functions (PREVIOUS DATABASE SHOULD BE DELETED BEFORE)
def rebuild_database(test=False):
    if test and os.path.exists("app_test.db"):
        os.remove("app_test.db")
    elif os.path.exists("app.db"):
        os.remove("app.db") 
    
    db.create_all()

    # Add sentences and hsk to database
    add_sentences()
    add_hsk()
    add_cedict()

    db.session.commit()

def empty_custom_db():
    words = Custom.query.all()
    for w in words:
        db.session.delete(w)

# WORK WITH DATABASE (activates a Flask context)
def handle_database(commit=False):
    with app.app_context():
        # NEEDS commit=True
        #db.create_all() #ONLY USE WHEN NEW CLASSES ARE ADDED (doesn't overwrite or change others)
        #add_sentences() #READDS IF ALREADY ADDED
        #add_hsk(True) READDS IF ALREADY ADDED
        #add_cedict() #READDS IF ALREADY ADDED
        #rebuild_database() #DOES EVERYTHING ABOVE
        #empty_custom_db()
        #add_hsk()
        #build_custom()

        # DOESN'T NEED commit=True
        #print_sentences()
        #print_hsk()
        #print_hsk_clean()
        #print_cedict()
        #print_db_tables()

        if commit:
            db.session.commit()


handle_database(commit=False)

# HOW I CONVERTED SQLITE3 TO MYSQL:
# 1. Created local mysql database with commandline:
# mysql -u root -p
# mysql> CREATE DATABASE mysqldb

# 2. Assigned SQLALCHEMY_DATABASE_URI in config.py to: 'mysql+pymysql://root:password123@localhost/mysqldb'
# 3. Ran rebuild_database() function
# 4. Ran build_custom() function
# 4. Made a dump file, connected to railway database and imported the dump file on commandline:
# mysqldump -uroot -p mysqldb > dump.sql
# railway connect MySQL
# mysql> SOURCE dump.sql

# GET DATA FROM RAILWAY MySQL DATABASE
# mysqldump -hcontainers-us-west-70.railway.app -uroot -pNxWYoZaY78cydE9yW6Gt --port 6688 --protocol=TCP railway > dump.sql

# ADDED sentence COLUMN TO CUSTOM
# logged in to railway again with: railway login --browserless. Then: railway connect MySQL
# mysql> ALTER TABLE custom ADD COLUMN sentence VARCHAR(2000);

