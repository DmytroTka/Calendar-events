from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import DateField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from models import User, db
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'Key'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# events = {}
# users = {}


# class User(UserMixin):
    # pass


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')


class EventForm(FlaskForm):
    date = DateField('Select date')
    submit = SubmitField('Add random event')


def get_cat_image():
    cat_url = 'https://api.thecatapi.com/v1/images/search'
    response = requests.get(cat_url)
    data = response.json()
    # print(data)
    return data[0]['url']


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = EventForm()
    user_events = json.loads(current_user.events)
    if form.validate_on_submit():
        api_upl = 'https://www.boredapi.com/api/activity/'
        response = requests.get(api_upl)
        data = response.json()
        print(data)
        activity = data.get('activity', 'No activity found')
        date_str = form.date.data.strftime('%Y-%m-%d')

        if date_str not in user_events:
            user_events[date_str] = []

        get_cat_image_url = get_cat_image()
        user_events[date_str].append({'activity': activity, 'cat_image': get_cat_image_url})
        user = User.query.filter_by(id=current_user.id).first()
        user.events = json.dumps(user_events)
        db.session.commit()
        return redirect('/')
    # return 'hello world'
    return render_template('index.html', form=form, events=user_events)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.username.data
        # users[username] = generate_password_hash(password)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password, events=json.dumps({}))

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.username.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect('/')
    return render_template('login.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # get_cat_image()
    app.run(debug=True)
