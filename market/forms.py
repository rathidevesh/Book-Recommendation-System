from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User, Review,Comment
from flask_login import current_user
from flask_wtf.file import FileField,FileAllowed

class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class ReviewForm(FlaskForm):
    book_name = StringField(label='Book Name:', validators=[DataRequired()])
    book_author = StringField(label='Author Name:', validators=[DataRequired()])
    description = TextAreaField(label='Description:', validators=[DataRequired()])
    picture = FileField(label="Book Pic",validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField(label='Add Review')

    def validate_book_name(self, book_name):
        review = Review.query.filter_by(book_name=book_name.data).first()
        if review:
            raise ValidationError('This book is already reviewed! Please try a different book name.')
        
class CommentForm(FlaskForm):
    text = StringField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post')

class SearchForm(FlaskForm):
    searched = StringField("Searched",validators=[DataRequired()])
    submit = SubmitField("Submit")
