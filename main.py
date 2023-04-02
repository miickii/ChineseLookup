from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import cross_origin
from config import Config
import os
import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")
message_history = [{"role": "system", "content": "You are a chinese tutor and will respond to all my questions"}, {"role": "assistant", "content": "OK"}]

db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

from models import Custom, Category

from searcher import Searcher
with app.app_context():
    searcher = Searcher()

@app.route("/search", methods=['POST'])
@cross_origin()
def search():
    data = request.json['text']
    input_text = data.lower()
    input_text = input_text.strip() # Remove leading and trailing whitespace

    examples = []
    output = []

    output = searcher.search_word(input_text)

    return jsonify(output)

@app.route("/analyze", methods=['POST'])
@cross_origin()
def analyze():
    text = request.json['text']
    result = searcher.analyze_sentence(text)

    return jsonify(result)

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
    
    return jsonify(results)

def update_custom(word, chinese, chinese_traditional, pinyin, english, pos, frequency, level):
    word.chinese = chinese
    word.chinese_traditional = chinese_traditional
    word.pinyin = pinyin
    word.english = english
    word.pos = pos
    word.frequency = frequency
    word.level = level

# Adds word to profile database ("Word" table)
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
        print("new word!")
        db.session.add(custom)

    # Create categories that aren't already in database
    db_categories = []
    for name in categories:
        category = Category.query.filter_by(name=name.lower()).first()
        if not category:
            category = Category(name=name.lower())
            print("new category!")
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify("deleted")

@app.route("/get-categories", methods=['GET'])
@cross_origin()
def get_categories():
    categories = Category.query.all()
    result = [{"name": c.name} for c in categories]
    return jsonify(result)

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


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
