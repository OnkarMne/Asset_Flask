from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField,PasswordField
from wtforms.validators import DataRequired, Email,Length
import os
from flask_login import UserMixin, login_user, login_required, LoginManager

app = Flask(__name__)
#Create database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL")
app.config['SECRET_KEY'] = os.environ.get("API_KEY")
bootstrap = Bootstrap5(app)


#Create Extensions
db = SQLAlchemy()

# initialise the app with extension
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

users = {
    1: User(1, 'user1', 'password1')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))


class BcpForm(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    employee_name = StringField('Name', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    contact = StringField('Contact', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    reason = SelectField('Reason', choices=["New Joinee", "Replacement"], validators=[DataRequired()])
    serial_no = StringField('Serial Number', validators=[DataRequired()])
    it_request = StringField('IT Request', validators=[DataRequired()])
    status = StringField('STATUS', validators=[DataRequired()], default='open')
    submit = SubmitField('Submit')
    #admin = SubmitField('Admin')
    #search = SubmitField('Search')

#Create Table
class Bcp_search(FlaskForm):
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    search = SubmitField('Search')


class Assets(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(250), unique=True, nullable=False)
    department = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    contact = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    reason = db.Column(db.String(250), nullable=False)
    serial_no = db.Column(db.String(250), nullable=False)
    it_request = db.Column(db.String(250), nullable=False)
    status = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=["GET", "POST"])
def add():
    form = BcpForm()
    if request.method == "POST":
        print(request.method)
        # Create Record
        new_entry = Assets(
            employee_id=request.form["employee_id"],
            employee_name=request.form['employee_name'],
            department=request.form["department"],
            email=request.form["email"],
            contact=request.form["contact"],
            address=request.form['address'],
            reason=request.form["reason"],
            serial_no=request.form["serial_no"],
            it_request=request.form['it_request'],
            status=request.form['status']
        )
        #print(request.form["employee_id"])
        db.session.add(new_entry)
        db.session.commit()
        #flash("Data Entered Succesfully")
        return redirect(url_for('home'))
    return render_template("add.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users.values():
            if user.username == username and user.password == password:
                login_user(user)
                return redirect(url_for('search'))
        return 'Invalid credentials. Please try again.'

    return render_template('login.html')

@app.route('/search', methods=["GET","POST"])
@login_required
def search():
    result = None
    s_form = Bcp_search()
    if request.method == "POST":
        emp_id = request.form['employee_id']
        result = db.session.execute(db.select(Assets).where(Assets.employee_id == emp_id)).scalar()
    return render_template("search.html", form=s_form, result=result)

@app.route('/user_search', methods=["GET","POST"])
def user_search():
    result = None
    s_form = Bcp_search()
    if request.method == "POST":
        emp_id = request.form['employee_id']
        result = db.session.execute(db.select(Assets).where(Assets.employee_id == emp_id)).scalar()
    return render_template("user_search.html", form=s_form, result=result)


@app.route('/update', methods=["GET","POST"])
def update():
    if request.method == "POST":
        emp_id = request.form.get("employee_id")
        status_to_update = db.get_or_404(Assets, emp_id)
        print(status_to_update)
        status_to_update.status = request.form["status"]
        print(status_to_update.status)
        db.session.commit()
        return redirect(url_for('search'))
    emp_id = request.args.get('employee_id')
    employee_selected = db.get_or_404(Assets, emp_id)
    return render_template("update.html", emp=employee_selected)

@app.route('/delete', methods=["GET","POST"])
def delete():
    emp_id = request.args.get('employee_id')
    employee_selected = db.get_or_404(Assets, emp_id)
    db.session.delete(employee_selected)
    db.session.commit()
    return redirect(url_for('search'))



if __name__ == '__main__':
    app.run(debug=True)


