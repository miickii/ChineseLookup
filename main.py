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
