from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
from sqlalchemy import func
from datetime import datetime
from sqlalchemy import desc

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    # items = db.relationship('Item', backref='owned_user', lazy=True)
    review = db.relationship('Review', backref='user', passive_deletes=True,lazy=True)
    comment = db.relationship('Comment',backref='user',passive_deletes=True)
    likes = db.relationship('Like',backref='user',passive_deletes=True)
    
    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Review(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    book_name = db.Column(db.String(length=50), nullable=False)
    book_author = db.Column(db.String(length=50), nullable=False)
    # book_photo = db.Column(db.LargeBinary(), nullable=False)
    description = db.Column(db.String(length=1000), nullable=False)
    image_file = db.Column(db.String(), nullable=True,default='birth.jpg')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True),default = func.now())
    comment = db.relationship('Comment',backref='review',passive_deletes=True)
    likes = db.relationship('Like', backref='review', passive_deletes=True)


    def __repr__(self):
        return f"Review('{self.book_name}', '{self.book_author}', '{self.description}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id', ondelete="CASCADE"), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
     
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id', ondelete="CASCADE"), nullable=False)
