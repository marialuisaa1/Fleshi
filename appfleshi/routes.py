from flask import render_template, url_for, redirect, request, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.sql.functions import user
from sqlalchemy.testing.provision import register
from appfleshi import app, database, bcrypt
from appfleshi.models import User, Photo, Like
from appfleshi.forms import LoginForm, RegisterForm, PhotoForm
from appfleshi import app
import os
from werkzeug.utils import secure_filename

@app.route('/', methods=['GET', 'POST'])
def homepage():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('feed'))
    return render_template('homepage.html', form=login_form)

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    register_form = RegisterForm()
    # Estou acessando minha rota, e estou perguntado meu formulario foi dado o submit
    if register_form.validate_on_submit():
        password = bcrypt.generate_password_hash(register_form.password.data)
        user = User(username=register_form.username.data, password=password, email= register_form.email.data)
        database.session.add(user) # Vai adicionar o usuário no meu banco de dados
        database.session.commit() # Vai validar minha sessão
        login_user(user, remember=True)
        return redirect(url_for('profile', user_id=user.id))
    return render_template('createaccount.html', form=register_form)

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if int (user_id) == int(current_user.id):
        photo_form = PhotoForm()
        if photo_form.validate_on_submit():
            file= photo_form.photo.data

            secure_name = secure_filename(file.filename)
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_name)
            file.save(path)
            photo = Photo(file_name=secure_name, user_id= current_user.id)
            database.session.add(photo)
            database.session.commit()

        return render_template('profile.html', user=current_user, form=photo_form)
    else:
        user = User.query.get(int(user_id))
        return render_template('profile.html', user=user, form=None)
#botão excluir- rota
@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    if photo.user_id != current_user.id:
        return redirect(url_for('profile', user_id=current_user.id))

    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        app.config['UPLOAD_FOLDER'],
        photo.file_name
    )

    if os.path.exists(path):
        os.remove(path)

    database.session.delete(photo)
    database.session.commit()

    return redirect(url_for('profile', user_id=current_user.id))
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/feed')
@login_required
def feed():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    return render_template('feed.html', photos=photos, Like=Like)

#curtir-rota
@app.route('/like/<int:photo_id>', methods=['POST'])
@login_required
def like(photo_id):
    like = Like.query.filter_by(user_id=current_user.id, photo_id=photo_id).first()

    if like:

        database.session.delete(like)
    else:

        new_like = Like(user_id=current_user.id, photo_id=photo_id)
        database.session.add(new_like)

    database.session.commit()
    return redirect(url_for('feed'))
#baixar foto -  rota
@app.route('/download/<int:photo_id>')
@login_required
def download_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)

    upload_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        app.config['UPLOAD_FOLDER']
    )

    return send_from_directory(
        upload_path,
        photo.file_name,
        as_attachment=True
    )
