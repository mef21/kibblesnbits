from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import dog_client
from ..forms import MovieReviewForm, SearchForm, MainPageForm
from ..models import User, Review, Post
from ..utils import current_time
import io 
import base64
from werkzeug.utils import secure_filename

dogs = Blueprint("dogs", __name__)
def images(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image
def images2(img_obj):
    bytes_im = io.BytesIO(img_obj.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

@dogs.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()
    form2 = MainPageForm()
    if form.validate_on_submit():
        return redirect(url_for("dogs.query_results", query=form.search_query.data))
    
    if form2.validate_on_submit() and current_user.is_authenticated:
        img = form2.propic.data
        post = Post(
            poster=current_user._get_current_object(),
            text1=form2.text.data,
            date=current_time(),
        )
        if img != None:
            filename = secure_filename(img.filename)
            post.pic.put(img.stream, content_type='images/png')
        post.save()
        return redirect(url_for('dogs.index'))
    main_posts = Post.objects.order_by('-date').all()
    print(main_posts)
    posts = []
    for r in main_posts:
        posts.append({
            'date': r.date,
            'username': r.poster.username,
            'content': r.text1,
            'profpic':images(r.poster.username),
            'image': images2(r.pic)
        })

    return render_template("index.html", form1=form, post_form=form2, posts=posts)

@dogs.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = dog_client.search(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("dogs.index"))

    return render_template("query.html", results=results)


@dogs.route("/dogs/<dog_id>", methods=["GET", "POST"])
def dog_detail(dog_id):
    try:
        result = dog_client.retrieve_dog_by_id(dog_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("users.login"))

    form = MovieReviewForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            id_url=dog_id,
            dog_title=result.id_url,
        )
        review.save()

        return redirect(request.path)

    reviews_m = Review.objects(id_url=dog_id)

    reviews = []
    for r in reviews_m:
        reviews.append({
            'date': r.date,
            'username': r.commenter.username,
            'content': r.content,
            'image': images(r.commenter.username)
        })

    return render_template(
        "dog_detail.html", form=form, dog=result, reviews=reviews
    )


@dogs.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    return render_template("user_detail.html", username=username, reviews=reviews)
