from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, equal_to
from appfleshi.models import User

class PhotoForm(FlaskForm):
    photo = FileField('Photo', validators=[DataRequired()])
    submit = SubmitField('Postar')
    delete = SubmitField('Excluir Foto')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("Usuário não encontrado!")
        return None


class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=60)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Criar Conta')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("E-mail já cadastrado")
        return None
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username já existe")
        return None
