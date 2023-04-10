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
    english = db.Column(db.String(150))
    pos = db.Column(db.String(10))
    frequency = db.Column(db.Integer)
    level = db.Column(db.Integer)

class Cedict(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chinese = db.Column(db.String(25))
    chinese_traditional = db.Column(db.String(25))
    pinyin = db.Column(db.String(80))
    pinyin_numbers = db.Column(db.String(105))
    pinyin_none = db.Column(db.String(90)) # Without marks or numbers
    english = db.Column(db.String(700))
    pos = db.Column(db.String(10))
    frequency = db.Column(db.Integer)

class Sentence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chinese = db.Column(db.String(350))
    pinyin = db.Column(db.String(800))
    english = db.Column(db.String(700))
    english_clean = db.Column(db.String(700))

custom_category = db.Table('custom_category',
    db.Column('custom_id', db.Integer, db.ForeignKey('custom.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
)

# Word table is just the custom database
class Custom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chinese = db.Column(db.String(400))
    chinese_traditional = db.Column(db.String(400))
    pinyin = db.Column(db.String(800))
    english = db.Column(db.String(800))
    pos = db.Column(db.String(10))
    frequency = db.Column(db.Integer)
    level = db.Column(db.Integer)
    categories = db.relationship('Category', secondary=custom_category, backref='containing')

    # Everytime a word get's searched we look for it in this Word table
    # If it isn't there (meaning that it's new) we will update srs to 1
    # User can do srs tests where a random selection of 10 words in this table, where srs is not None.
    # If the word is guessed correctly, srs increases. This will make the word show up less in the following tests.
    # When srs reaches 3 it graduades to a learnt card and srs is set to None (this will make it appear in profile page)
    # This word will only show up in profile page if srs is equal to 0
    srs = db.Column(db.Integer) # None means that it isn't

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

