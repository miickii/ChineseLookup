from main import db

# HSK_CLEAN is used when we search for english words in webapp
# ; and . symbols removed (for better search results to frontend)
# This will only contain 1 english translation per chinese
# In HSK we can have something like: "oneself; self"
# In HSK_CLEAN this would instead be two different rows with same chinese. One for "oneself" and another for "self"
class HSK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chinese = db.Column(db.String(20))
    pinyin = db.Column(db.String(60))
    english = db.Column(db.String(60))
    pos = db.Column(db.String(10))
    frequency = db.Column(db.Integer)
    level = db.Column(db.Integer)

class Cedict(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chinese = db.Column(db.String(20))
    chinese_traditional = db.Column(db.String(20))
    pinyin = db.Column(db.String(60))
    pinyin_numbers = db.Column(db.String(60))
    pinyin_none = db.Column(db.String(60)) # Without marks or numbers
    english = db.Column(db.String(200))
    pos = db.Column(db.String(10))
    frequency = db.Column(db.Integer)

class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chinese = db.Column(db.String(150))
    pinyin = db.Column(db.String(400))
    english = db.Column(db.String(500))
    english_clean = db.Column(db.String(500))

