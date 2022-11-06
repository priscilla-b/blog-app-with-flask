from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

from .forms import CreatePostForm
from .models import Post, Tag, User, db

views = Blueprint("views", __name__)

@views.route('/')
@views.route('/home')
def home():

    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/contact')
def contact():
    return render_template('contact.html')

@views.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():

    form = CreatePostForm(request.form)
    user_id = current_user.get_id()
    if request.method == 'POST':
       
        new_post = Post(
            title = form.title.data,
            summary = form.summary.data,
            body = form.body.data,
            author_id = user_id,
            author = User.query.get(user_id)
        )
        
        for tag in form.tags.data:
            tag_obj = Tag.query.filter_by(name=tag).first()
            tag_obj.posts_associated.append(new_post)
            db.session.add(tag_obj)
            

        db.session.add(new_post)
        db.session.commit()

        flash('Your post has been successfully created !', 'success')

        return redirect(url_for('views.home'))

    return render_template('create_post.html', form=form)


@views.route('create_post/add_tag', methods=['GET', 'POST'])
@login_required
def add_tag():

    if request.method == 'POST':
        name = request.form.get('name')
        tag_exists = Tag.query.filter_by(name=name).first()
        if tag_exists:
            flash('Tag already exists! Check select input to choose')
        else:
            new_tag = Tag(name=name)
            db.session.add(new_tag)
            db.session.commit()

        return redirect(url_for('views.create_post'))

    return render_template('add_tag.html')

@views.route("/view-post/<id>")
@login_required
def view_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')

    return render_template('view_post.html', post=post)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


@views.route("/edit-post/<id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user != post.author:
        flash('You do not have permission to edit this post.', category='error')
    else:
        form = CreatePostForm(obj=post)
        if request.method == 'POST' and form.validate:
            post.title = form.title.data
            post.summary = form.summary.data
            post.body = form.body.data
            
            for tag in form.tags.data:
                tag_obj = Tag.query.filter_by(name=tag).first()
                tag_obj.posts_associated.append(post)
                db.session.add(tag_obj)

            db.session.add(post)
            db.session.commit()
            flash('Your post has been edited.', category='success')

            return redirect(url_for('views.home'))

    return render_template('create_post.html', form=form)


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = Post.query.filter_by(author=user.id).all()
    return render_template("posts.html", user=current_user, posts=posts, username=username)