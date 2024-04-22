from market import app, db
from market.models import User, Review,Comment,Like
from market.forms import RegisterForm, LoginForm, ReviewForm,CommentForm,SearchForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.exceptions import abort
from sqlalchemy import desc
import pickle
import numpy as np
import pandas as pd
import os
from werkzeug.utils import secure_filename
import os
import secrets
from PIL import Image
from flask import current_app


pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_score.pkl','rb'))

@app.route('/')
@app.route('/home')
def home_page():
    
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))


app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'market/static/image'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_picture(form_picture, book_name):
    """
    Save the uploaded picture file to the server and return the filename.

    :param form_picture: The uploaded picture file
    :param book_name: The name of the book for which the picture is being uploaded
    :return: The filename of the saved picture file
    """
    # Generate a random filename for the picture to avoid conflicts
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = f"{book_name}_{random_hex}{f_ext}"
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)

    # Resize and save the picture file
    output_size = (500, 500)  # Set the desired output size for the picture
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_filename


@app.route('/write_review', methods=['GET', 'POST'])
@login_required
def reviews_page():
    form = ReviewForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, form.book_name.data)
            review = Review(book_name=form.book_name.data,
                            book_author=form.book_author.data,
                            description=form.description.data,
                            user_id=current_user.id,
                            image_file=picture_file)

            db.session.add(review)
            db.session.commit()

            flash('Post Created', category='success')
            return redirect(url_for('home_page'))
    return render_template('write_review.html', form=form)


@app.route('/reviews')
def review_detail():
    review = Review.query.all()
    return render_template('review_detail.html',user=current_user,review=review)

@app.route("/delete-review/<id>")
@login_required
def delete_post(id):
    review = Review.query.filter_by(id=id).first()
    if not review:
        flash("Review does not exist",category='error')
    elif review.user_id != current_user.id:
        flash('You do not have permission to delete this review', category='error')
    else:
        db.session.delete(review)
        db.session.commit()
        flash('Post Deleted',category='success')

    return redirect(url_for('home_page'))

@app.route("/review/<username>")
@login_required
def review(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('No user with that username exists', category='error')
        return redirect(url_for('home_page'))
    
    reviews = Review.query.filter_by(user_id=user.id).all()
    return render_template("review.html", username=username, reviews=reviews)


@app.route('/create-comment/<int:review_id>', methods=['POST'])
@login_required
def create_comment(review_id):
    description = request.form.get('description')
    if not description:
        flash('Comment can not be empty', category='error')
        return redirect(url_for('review_detail'))

    review = Review.query.filter_by(id=review_id).first()
    if not review:
        flash('Post does not exist', category='error')
        return redirect(url_for('review_detail'))

    comment = Comment(description=description, user_id=current_user.id, review_id=review_id)
    db.session.add(comment)
    db.session.commit()
    flash('Comment created', category='success')
    return redirect(url_for('review_detail'))


@app.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment=Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.',category='error')

    elif current_user.id != comment.user_id and current_user.id != comment.review.user_id:
        flash('You do not have permisson to delete this comment',category='error')

    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('home_page'))

@app.route("/like-review/<int:review_id>", methods=["GET", "POST"])
@login_required
def like(review_id):
    review = Review.query.filter_by(id=review_id).first()
    if not review:
        flash("Post does not exist", category="error")
        return redirect(url_for("home_page"))
    like = Like.query.filter_by(user_id=current_user.id, review_id=review_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        flash("You unliked this review", category="success")
    else:
        like = Like(user_id=current_user.id, review_id=review_id)
        db.session.add(like)
        db.session.commit()
        flash("You liked this review", category="success")
    return redirect(url_for('review_detail'))


@app.route('/search', methods=["POST"])
@login_required
def search():
    form = SearchForm()
    reviews = Review.query
    if form.validate_on_submit():
        searched = form.searched.data
        reviews = db.session.query(Review).join(Like).filter(Review.book_name.like(f"%{searched}%")).distinct().all()

    return render_template("search.html", form=form, reviews=reviews, user=current_user)


@app.route('/recommend')
@login_required
def recommend_ui():
    return render_template('recommend.html')



@app.route('/recommend_books',methods=['GET', 'POST'])

@login_required
def recommend():
    user_input = request.args.get('user_input')
    data = []
    if user_input and len(pt.index) > 0:
        if user_input in pt.index:
            index = np.where(pt.index == user_input)[0][0]
            similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]
            for i in similar_items:
                item = []
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
                data.append(item)
    return render_template('recommend.html',data=data)
