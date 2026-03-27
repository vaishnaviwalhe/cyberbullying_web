from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pickle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# LOAD MODEL
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# USER TABLE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# MESSAGE TABLE
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    result = db.Column(db.String(50))
    user_id = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# HOME
@app.route('/')
def home():
    return redirect(url_for('login'))

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html')

# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

# PREDICT
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    text = request.form['text']
    data = vectorizer.transform([text])
    result = model.predict(data)[0]

    msg = Message(text=text, result=result, user_id=current_user.id)
    db.session.add(msg)
    db.session.commit()

    return render_template('result.html', text=text, result=result)

# VIEW DATA
@app.route('/view')
@login_required
def view():
    data = Message.query.filter_by(user_id=current_user.id).all()
    return render_template('view.html', data=data)

# DELETE
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    msg = Message.query.get(id)
    db.session.delete(msg)
    db.session.commit()
    return redirect('/view')

# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# CREATE DB
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
