from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from config import Config
import os

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


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
