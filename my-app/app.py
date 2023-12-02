import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user, logout_user, login_required
from flask_mysqldb import MySQL
import mysql.connector


app = Flask(__name__)
aplication = app
app.secret_key = '97110c78ae51a45af397b6534caef90ebb9b1dcb3380f008f90b23a5d1616bf1bc29098105da20fe'

db = MySQL(app)


@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    return render_template('public/login/base_login.html')

def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/single')
def single():
    return render_template('shop-single.html')

@app.route('/iniciar', methods=['GET', 'POST'])
def login():
    msg = ''
    form = request.form

    if request.method == 'POST' and 'username' in form and 'password' in form:
        username = form['username']
        password = form['password']

        connection = mysql.connector.connect(host='127.0.0.1', user='josh', password='1234', database='shop_store')
        cursor = connection.cursor(dictionary=False)
        cursor.execute("SELECT * FROM users WHERE email_user = %s AND pass_user = %s", (username, password))
        account = cursor.fetchone()
        if account:
            # Usuario autenticado con éxito
            # Aquí podrías usar Flask-Login para hacer login_user(current_user)
            flash('Inicio de sesión exitoso!', 'hecho')
            return redirect(url_for('index'))  # Reemplaza 'index' con la ruta correcta después del inicio de sesión
        else:
            msg = 'Invalid username or password'

        cursor.close()

    return render_template('auth/login.html', msg=msg, form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    form = request.form

    if request.method == 'POST' and 'email' in form and 'pswd' in form and 'fullname' in form:
        username = form['email']
        password = form['pswd']
        fullname = form['fullname']

        connection = mysql.connector.connect(host='127.0.0.1', user='josh', password='1234', database='shop_store')
        cursor = connection.cursor(dictionary=False)
        cursor.execute("SELECT * FROM users WHERE email_user = %s", (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', username):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            cursor.execute("INSERT INTO users (email_user, pass_user, name_surname) VALUES (%s, %s, %s)", (username, password, fullname))
            connection.commit() 
            #msg = 'You have successfully registered!'
            flash('Te has registrado con exito!', 'hecho')  # Mensaje de éxito
            return redirect(url_for('login'))
        cursor.close()

    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg, form=form)

@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"


def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    # No se inicializa CSRFProtect si no lo estás utilizando
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)



