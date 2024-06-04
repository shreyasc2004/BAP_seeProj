from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import secrets

users = {}
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

bikes = [
    {'id': 1, 'name': 'Electric Vehicle', 'available': True, 'hourly_rate': 50, 'daily_rate': 200, 'weekly_rate': 1200},
    {'id': 2, 'name': '125 cc Petrol', 'available': True, 'hourly_rate': 40, 'daily_rate': 180, 'weekly_rate': 1000},
    {'id': 3, 'name': '110 cc Petrol', 'available': True, 'hourly_rate': 35, 'daily_rate': 150, 'weekly_rate': 1000},
]

def get_available_bikes():
    return [bike for bike in bikes if bike['available']]

def get_all_bikes():
    return bikes

def rent_bike(bike_id, rental_type):
    for bike in bikes:
        if bike['id'] == int(bike_id) and bike['available']:
            bike['available'] = False
            session['rental_start'] = datetime.datetime.now()
            session['rental_type'] = rental_type
            session['bike_id'] = bike_id
            session['hourly_rate'] = bike['hourly_rate']
            session['daily_rate'] = bike['daily_rate']
            session['weekly_rate'] = bike['weekly_rate']
            print(f"Bike {bike_id} rented on {rental_type} basis")
            return True
    return False

import datetime

def return_bike(bike_id):
    for bike in bikes:
        if bike['id'] == int(bike_id) and not bike['available']:
            bike['available'] = True
            rental_type = session.pop('rental_type', None)
            hourly_rate = session.pop('hourly_rate', None)
            daily_rate = session.pop('daily_rate', None)
            weekly_rate = session.pop('weekly_rate', None)

            if rental_type and hourly_rate and daily_rate and weekly_rate:
                if rental_type == 'hourly':
                    bill = hourly_rate
                elif rental_type == 'daily':
                    bill = daily_rate
                elif rental_type == 'weekly':
                    bill = weekly_rate
                print(f"Bike {bike_id} returned, total bill: {bill}")
                return bill
    return None




@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        Dl_no = request.form.get('DL')

        if username in users:
            return render_template('register.html', error='Username already exists')
        else:
            users[username] = {'password': password, 'name': name, 'address': address, 'phone': phone, 'DL': Dl_no}
            return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username]['password'] == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'logged_in' in session:
        available_bikes = get_available_bikes()
        all_bikes = get_all_bikes()
        if request.method == 'POST':
            choice = request.form.get('choice')
            scooter_id = request.form.get('scooter_id')
            if choice == '5':
                bill = return_bike(scooter_id)
                if bill is not None:
                    message = f"Scooter returned successfully. Total bill: ₹ {bill}"
                else:
                    message = "Scooter was not rented"
                return render_template('index.html', message=message, scooters=all_bikes)
            else:
                return render_template('index.html', scooters=available_bikes)
        return render_template('index.html', scooters=available_bikes)
    else:
        if not users:
            return redirect(url_for('register'))
        else:
            return redirect(url_for('login'))

@app.route('/process_form', methods=['POST'])
def process_form():
    choice = request.form.get('choice')
    scooter_id = request.form.get('scooter_id')
    available_bikes = get_available_bikes()
    all_bikes = get_all_bikes()
    
    if choice == '1':
        stock = len(available_bikes)
        return render_template('index.html', stock=stock, scooters=available_bikes)
    elif choice in ['2', '3', '4']:
        rental_type = 'hourly' if choice == '2' else 'daily' if choice == '3' else 'weekly'
        if rent_bike(scooter_id, rental_type):
            message = "Bike rented successfully"
        else:
            message = "Bike not available"
        return render_template('index.html', message=message, scooters=available_bikes)
    elif choice == '5':
        bill = return_bike(scooter_id)
        if bill is not None:
            message = f"Bike returned successfully. Total bill: ₹ {bill}"
        else:
            message = "Bike was not rented"
        return render_template('index.html', message=message, scooters=all_bikes)
    elif choice == '6':
        session.pop('logged_in', None)
        return redirect(url_for('login'))
    else:
        error = "Invalid choice"
        return render_template('index.html', error=error, scooters=available_bikes)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
