from flask import Flask, render_template, url_for, redirect, session, request,flash
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash,check_password_hash
from flask_bcrypt import check_password_hash
import re


vj = Flask(__name__)

static_url_path = '/static'
vj.secret_key = "Vijay@006"
vj.config["MYSQL_HOST"] = 'localhost'
vj.config["MYSQL_USER"] = 'root'
vj.config["MYSQL_PASSWORD"] = 'Vijay@006'
vj.config["MYSQL_DB"] = 'e_com'
mysql = MySQL(vj)
bcrypt=Bcrypt(vj)

def is_logged_in():
    return "Name" in session

class user():
    def __init__(self,id,Name,Password):
        self.id=id
        self.Name=Name
        self.Password=Password

class SignupForm(FlaskForm):
    Name=StringField("Name",validators=[InputRequired(),Length(min=4,max=20)])
    Password=PasswordField("Password",validators=[InputRequired(),Length(min=8,max=20)])
    submit=SubmitField("Signup")

class Loginform(FlaskForm):
    Name=StringField("Name",validators=[InputRequired(),Length(min=4,max=20)])
    Password=PasswordField("Password",validators=[InputRequired(),Length(min=8,max=20)])
    submit=SubmitField("Login")

class Addproduct(FlaskForm):
    Name=StringField("Name",validators=[InputRequired(),Length(min=2,max=20)])
    ProductName=StringField("ProductName",validators=[InputRequired(),Length(min=2,max=20)])
    Price=StringField("Price",validators=[InputRequired(),Length(min=1,max=20)])
    Quantity=StringField("Quantity",validators=[InputRequired(),Length(min=2,max=20)])

    submit=SubmitField("Submit")

def is_password_strong(Password):
    if len(Password)<8:
        return False
    if not re.search(r"[a-z]",Password) or not re.search(r"[A-Z]",Password) or not re.search(r"\d",Password):
        return False
    if not re.search(r"[!@#$%^&*()-+{}|\"<>?/]",Password):
        return False
    return

@vj.route("/")

def home():    
    return render_template('index.html')
@vj.route("/login",methods=["GET","POST"])
# def signup():
def login():
    formlog = Loginform()
    if formlog.validate_on_submit():
        Name = formlog.Name.data
        Password = formlog.Password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE Name=%s", (Name,))
        data = cur.fetchone()
        cur.close()
        if data and bcrypt.check_password_hash(data[2], Password):
            session["Name"] = Name
            flash("Login successfully", 'success')
            return redirect(url_for('table'))
        else:
            flash("Invalid Password or Username", 'error')
    return render_template('login.html', form=formlog)

@vj.route("/signup",methods=["GET","POST"])
def signup():
    formsign = SignupForm()

    if request.method=="POST":
        print(request.method,"Done Post")
        # if formsign.validate_on_submit():
        print("Stage Two")
        Name=formsign.Name.data
        Password=formsign.Password.data
        if not is_password_strong(Password):
            flash("Password not strong")
        hashed_password=bcrypt.generate_password_hash(Password).decode('utf-8')
        cur=mysql.connection.cursor()
        print(Name,Password)
        cur.execute("select *from signup where Name=%s",(Name,))
        data=cur.fetchone()
        if data:
            cur.close()
            flash("Username already taken,Please choose another Name")
            return render_template("signup.html",form=formsign)
        cur.execute("insert into signup(Name,Password) values(%s,%s)",(Name,hashed_password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    
    return render_template('signup.html',form=formsign)

@vj.route("/table",methods=["GET","POST"])
def table():
    if is_logged_in():
        Name = session['Name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products WHERE Name=%s", (Name,))
        data=cur.fetchall()
        cur.connection.commit()
        print(data)
        cur.close()
    return render_template("tab.html")
@vj.route('/add',methods=["GET","POST"])
def add():
    form=Addproduct()
    if request.method=="POST":
       Name=form.Name.data
       ProductName = form.ProductName.data
       Quantity = form.Price.data
       Price = form.Quantity.data
       cur = mysql.connection.cursor()
       cur.execute("INSERT INTO products (Name,ProductName,Quantity,Price) VALUES(%s,%s,%s,%s)",(Name,ProductName,Quantity,Price))
       cur.connection.commit()
       cur.close()
       return redirect(url_for('table'))
    return render_template("add.html",form=form)

@vj.route('/')
def logout():
    session.pop("Name",None)
    redirect(url_for('home'))

if __name__=="__main__":
    vj.run(debug=True)

