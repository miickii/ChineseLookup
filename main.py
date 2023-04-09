from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import cross_origin
from config import Config
import os
import openai
from dotenv import load_dotenv
load_dotenv()
import random

openai.api_key = os.getenv("OPENAI_KEY")
message_history = [{"role": "system", "content": "You are a chinese tutor and will respond to all my questions"}, {"role": "assistant", "content": "OK"}]

db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

from models import Custom, Category, Sentence

from searcher import Searcher
with app.app_context():
    searcher = Searcher()

# DICTIONARY
@app.route("/search", methods=['POST'])
@cross_origin()
def search():
    data = request.json['text']
    input_text = data.lower()
    input_text = input_text.strip() # Remove leading and trailing whitespace

    examples = []
    output = []

    output = searcher.search_word(input_text)
    print(f'Searched for "{input_text}", returned:')
    for o in output:
        print(f'{o["id"]}, {o["chinese"]}, {o["pinyin"]}, {o["english"]}')

    return jsonify(output)

@app.route("/analyze", methods=['POST'])
@cross_origin()
def analyze():
    text = request.json['text']
    result = searcher.analyze_sentence(text)

    return jsonify(result)


# CHATBOT
@app.route("/chat", methods=['POST'])
@cross_origin()
def chat():
    global message_history
    text = request.json['text']
    message_history.append({"role": "user", "content": text})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )
    reply_content = completion.choices[0].message.content
    message_history.append({"role": "assistant", "content": reply_content})

    return jsonify(reply_content)

@app.route("/reset-chat", methods=['POST'])
@cross_origin()
def reset_chat():
    global message_history
    message_history = [{"role": "system", "content": "You are a chinese tutor and will respond to all my questions"}, {"role": "assistant", "content": "OK"}]

    return jsonify("OK")


# CUSTOM DATA MANIPULATION
@app.route("/fetch-profile-data", methods=['GET'])
@cross_origin()
def fetch_profile_data():
    results = [] # index 0: words, index 1: categories
    words = Custom.query.all()

    # Adding words
    results.append([searcher.profile_word_json(w) for w in words])

    # Adding categories
    categories = Category.query.all()
    results.append([{"name": c.name} for c in categories])
    print("Profile custom entries returned")
    
    return jsonify(results)

def update_custom(word, chinese, chinese_traditional, pinyin, english, pos, frequency, level):
    print(f'Updated {word.chinese} to: {chinese}, {chinese_traditional}, {pinyin}, {english}, {pos}, {frequency}, {level}')
    word.chinese = chinese
    word.chinese_traditional = chinese_traditional
    word.pinyin = pinyin
    word.english = english
    word.pos = pos
    word.frequency = frequency
    word.level = level

@app.route("/add-custom", methods=['POST'])
@cross_origin()
def add_custom():
    c, c_trad, p, p_num, e, e_short, pos, freq, level, categories = request.json['word']
    add = request.json['add']

    custom = Custom.query.filter_by(chinese=c).first()
    if custom:
        if add:
            return jsonify("word in database")
        update_custom(custom, c, c_trad, p, e, pos, freq, level)
    else:
        custom = Custom(chinese=c, chinese_traditional=c_trad, pinyin=p, english=e, pos=pos, frequency=freq, level=level, srs=0)
        print("new word added!")
        db.session.add(custom)

    # Create categories that aren't already in database
    db_categories = []
    for name in categories:
        category = Category.query.filter_by(name=name.lower()).first()
        if not category:
            category = Category(name=name.lower())
            print("new category added: " + name)
            db.session.add(category)
        
        db_categories.append(category)

    custom.categories = db_categories

    db.session.commit()

    return jsonify("done")

@app.route("/delete-custom", methods=['DELETE'])
@cross_origin()
def delete_custom():
    id = request.json['id']
    try:
        custom = Custom.query.filter_by(id=id).delete()
        db.session.commit()
        print("Deleted custom entry with id: " + id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify("deleted")

@app.route("/get-categories", methods=['GET'])
@cross_origin()
def get_categories():
    categories = Category.query.all()
    result = [{"name": c.name} for c in categories]
    return jsonify(result)


# TEST ROUTES
@app.route("/get-test-words", methods=["POST"])
@cross_origin()
def get_test_words():
    levels, amount, categories = request.json['options']

    # Remove sentence from categories to get words from
    if "sentence" in categories:
        categories.remove("sentence")

    # levels is a list of strings, it has to be numbers
    levels = [eval(l) for l in levels]

    words = []
    # Get all categories selected from database
    db_categories = Category.query.filter(Category.name.in_(categories)).all()
    # Go through each category and add all words from that category
    for category in db_categories:
        for custom in category.containing:
            # Make sure that the word hasn't been added already (some categories have the same word), and that the word has one of the selected levels
            if custom not in words and custom.level in levels:
                words.append(custom)

    # after getting all words filtered by category and level:
    # we sort them by their srs count
    # and choose the "amount" first words from the list, if there are more words than required
    words.sort(key=lambda w: w.srs)
    
    if len(words) > amount:
        words = words[0:amount]
        #words = random.sample(words, amount)
    
    # Randomize order of words
    random.shuffle(words)

    # Print words to console
    print("Test words returned:")
    for w in words:
        print(f'{w.id}, {w.chinese}, {w.pinyin}, {w.english}, srs: {w.srs}')

    # Each chinese word is split into all seperate characters, so that player can choose characters in the English test
    results = [searcher.word_json(w, split_characters=True) for w in words]

    # Add an example sentence too each word
    for r in results:
        print(f'{r["id"]}, {r["chinese"][0]}, {r["pinyin"]}, {r["english"]}, srs: {r["srs"]}')
        # Search through all sentences and add to examples if they contain the chinese
        sentence = Sentence.query.filter(Sentence.chinese.contains(r["chinese"][0]), func.length(Sentence.chinese) < 30).first() # r["chinese"] is a list where the first element is the chinese word
        if sentence:
            r["examples"].append({"chinese": sentence.chinese, "pinyin": sentence.pinyin, "english": sentence.english})

    return jsonify(results)

@app.route("/get-test-sentences", methods=["POST"])
@cross_origin()
def get_test_sentences():
    levels, amount, categories = request.json['options']

    # levels is a list of strings, it has to be numbers
    levels = [eval(l) for l in levels]

    results = []
    
    # Get sentence category
    sentence_cat = Category.query.filter_by(name="sentence").first()

    sentences = sentence_cat.containing
    if len(sentences) > amount:
        sentences = random.sample(sentences, amount)
    
    # Each chinese word is split into all seperate characters, so that player can choose characters in the English test
    results = [searcher.word_json(s, split_characters=True) for s in sentences]
    
    
    # Randomize order of sentences
    random.shuffle(results)

    return jsonify(results)

@app.route("/update-srs", methods=['POST'])
@cross_origin()
def update_srs():
    correct_words_id = request.json['correct']
    wrong_words_id = request.json['wrong']

    words = Custom.query.filter(Custom.id.in_(correct_words_id)).all()
    print("Correct words:")
    for word in words:
        print(word.chinese)
        word.srs += 1
    
    words = Custom.query.filter(Custom.id.in_(wrong_words_id)).all()
    print("\nFailed words:")
    for word in words:
        print(word.chinese)
        word.srs = 0
    
    db.session.commit()
    return jsonify("done")

@app.route("/print-srs", methods=['POST'])
@cross_origin()
def print_srs():
    ids = request.json['words']
    words = Custom.query.filter(Custom.id.in_(ids)).all()
    for word in words:
        print(word.chinese, word.english, word.srs)
    return '', 204

@app.route("/print-worst-srs")
@cross_origin()
def print_worst_srs():
    words = Custom.query.filter(~Custom.categories.any(Category.name == 'sentence')).all()
    words.sort(key=lambda w: w.srs)
    for word in words:
        print(word.chinese, word.english, word.srs)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
