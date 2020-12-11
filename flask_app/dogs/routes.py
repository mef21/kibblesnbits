from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

from .. import dog_client
from ..forms import MovieReviewForm, SearchForm
from ..models import User, Review
from ..utils import current_time

dogs = Blueprint("dogs", __name__)

@dogs.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("dogs.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)

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

    reviews = Review.objects(id_url=dog_id)

    return render_template(
        "dog_detail.html", form=form, dog=result, reviews=reviews
    )


@dogs.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)

    return render_template("user_detail.html", username=username, reviews=reviews)