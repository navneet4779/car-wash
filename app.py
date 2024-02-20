import pymysql
from flask import Flask, render_template, request, flash, session, redirect, url_for
from datetime import datetime
import re
import config

app = Flask(__name__)
app.secret_key = config.secret_key
connection = pymysql.connect(user=config.user, password='', host=config.host, database=config.database)
cursor = connection.cursor(pymysql.cursors.DictCursor)
# print(cursor)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/service')
def service():
    return render_template('service.html')


@app.route('/memberships', methods=['GET', 'POST'])
def membership():
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        postalcod = request.form['postalcod']
        country = request.form['country']
        gender = request.form['gender']
        offer = request.form['offertype']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Wrong email address!")
        elif re.match(r'\D', phone):
            flash('Wrong phone number')
        else:
            cursor.execute(
                "INSERT INTO membership(firstname, lastname, email, phone, address, city, postalcod, country, offer, gender) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (firstname, lastname, email, phone, address, city, postalcod, country, offer, gender))
            connection.commit()
    return render_template("membership.html")


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == "POST" and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        cursor.execute("SELECT * FROM newsletters WHERE email = %s", (email,))
        unique_email = cursor.fetchone()
        if unique_email:
            flash('You are already subscribed to our Newsletters and Offers! Thank you!')
        else:
            cursor.execute("INSERT INTO newsletters VALUES (NULL, %s, %s, %s)", (firstname, lastname, email))
            connection.commit()
            flash("You have been successfully subscribed to our NewsLetters and Offers")
    return render_template('offers.html')


@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    current_day = datetime.now().strftime("%Y-%m-%d")
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        carmake = request.form['carmake']
        cartype = request.form['cartype']
        regnumber = request.form['regnumber']
        branch = request.form['branch']
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Wrong Email")
        elif re.match(r'\D', phone):
            flash('Wrong phone number')
        else:
            cursor.execute("INSERT INTO reservations VALUES (NULL, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                firstname, lastname, email, phone, carmake, cartype, regnumber, branch, service, date, time))
            connection.commit()
            flash("Order placed with Success!")
    return render_template("reservations.html", current_day=current_day)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST" and 'firstname' in request.form and 'lastname' in request.form and 'email' in \
            request.form and 'phone' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Wrong email address!")
        else:
            cursor.execute(
                "INSERT INTO contact(firstname, lastname, email, phone, message) VALUES (%s, %s, %s, %s, %s)",
                (firstname, lastname, email, phone, message))
            connection.commit()
    return render_template("contact.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        account = cursor.fetchone()
        if account:
            session['logged'] = True
            session['id'] = account['id']
            #   print(account[0])
            session['username'] = account['username']
            #  flash("Logged in with success!")
            return render_template('employee.html')
        else:
            flash('Wrong username/password! Please, check your credentials!')
    return render_template('login.html')


@app.route('/employee')
def employee():
    if 'logged' in session:
        return render_template('employee.html')
    else:
        return '<h1>NOT AUTHORIZED!</h1>'


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/employee/members')
def employee_members():
    if 'logged' in session:
        cursor.execute("SELECT id, firstname, lastname,offer FROM membership ORDER BY id ASC")
        member_list = cursor.fetchall()
        return render_template('employee-members.html', member_list=member_list)
    else:
        return '<h1>NOT AUTHORIZED!</h1>'


@app.route('/employee/support_center')
def employee_support_center():
    if 'logged' in session:
        cursor.execute("SELECT id, firstname, lastname FROM contact ORDER BY id DESC")
        ticket_list = cursor.fetchall()
        return render_template('employee-support-center.html', ticket_list=ticket_list)
    else:
        return '<h1>NOT AUTHORIZED!</h1>'


@app.route('/employee/support_center/<int:id>')
def employee_support_center_ticket_details(id):
    if 'logged' in session:
        cursor.execute("SELECT * FROM contact WHERE id = %s", id)
        ticket = cursor.fetchone()
        return render_template('support_ticket.html', ticket=ticket)
    else:
        return '<h1>NOT AUTHORIZED!</h1>'


if __name__ == '__main__':
    app.run(debug=True)

