

import bcrypt
from flask_pymongo import PyMongo
from flask_login import login_required
from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import pandas as pd
from flask_mail import Mail, Message
from email_validator import validate_email, EmailNotValidError
from email.mime.multipart import MIMEMultipart
from functools import wraps
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import pickle
import base64
import re
# for email

from pymongo import MongoClient
from email.mime.text import MIMEText

# for email validation


# for pkl file to predict

app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config['MONGO_DBNAME'] = "auth"
app.config['MONGO_URI'] = "mongodb://localhost:27017/auth"
mongo = PyMongo(app)
print("connected")

model = pickle.load(open(
    "C:/Users/HP/Downloads/rainfall_prediction_SVM-master/rainfall_prediction_SVM-master/models/ranf.pkl", "rb"))
print("model loaded")


def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        user = mongo.db.user
        existing_user = user.find_one({'username': request.form['username']})
        existing_email = user.find_one({'email': request.form['email']})
        if existing_email:
            email_error = "email have been already used."
            return f"<script>alert('{email_error}');window.location='/register'</script>"

        if existing_user:
            name_error = "username is already taken."
            return f"<script>alert('{name_error}');window.location='/register'</script>"

        if request.form['password'] != request.form['confirm_password']:
            pass_error = "password do not matched"
            return f"<script>alert('{pass_error}');window.location='/register'</script>"

        if len(request.form["password"]) < 8:
            pass_error = "password must be of 8 character"
            return f"<script>alert('{pass_error}');window.location='/register'</script>"

        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"

        if not re.fullmatch(password_pattern, request.form["password"]):
            pass_error = "uppercase letters: A-Z, lowercase letters: a-z, numbers: 0-9, any of the special characters: @#$%^&+="
            return f"<script>alert('{pass_error}');window.location='/register'</script>"

        hashpass = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        user.insert_one(
            {'username': request.form['username'], 'password': hashpass, 'email': request.form['email']})
        session['username'] = request.form['username']
        session['email'] = request.form['email']

        return render_template('home.html')

    return render_template('register.html')


@ app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_name = session.get('username')
        user_email = session.get('email')
        print(user_email)

        # check if email and password are not empty
        if not email or not password:
            error_message = "Email and password are required."
            return f"<script>alert('{error_message}');window.location='/login'</script>"

        user = mongo.db.user

        login_user = user.find_one({'email': email})

        if login_user:
            user_email = login_user['email']
            session['user_email'] = user_email

            if bcrypt.checkpw(password.encode('utf-8'), login_user['password']):
                session['email'] = email
                session['username'] = login_user['username']
                return redirect('/home')
            else:
                error_message = "Invalid email or password."
        else:
            error_message = "User not registered"

        # display the error message using JavaScript alert function
        return f"<script>alert('{error_message}');window.location='/login'</script>"

    return render_template('login.html')


@ app.route('/')
def index():
    return render_template('home.html')


@ app.route('/rainy')
@ login_required
def rainy():
    return render_template('rainyday.html')


@ app.route('/sunny')
@ login_required
def sunny():
    return render_template('sunnyday.html')


@ app.route('/developer')
def developer():

    return render_template('developer.html')


@ app.route('/about')
def about():
    return render_template('about.html')


@ app.route('/home')
def home():
    return render_template('home.html')


@ app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('index'))


@ app.route("/predict", methods=['GET', 'POST'])
@ login_required
def predict():
    user_email = session.get('email')

    if request.method == "POST":
        print(user_email)

        # DATE
        date = request.form['date']
        day = float(pd.to_datetime(date, format="%Y-%m-%d").day)
        month = float(pd.to_datetime(date, format="%Y-%m-%d").month)
        # MinTemp
        minTemp = float(request.form['mintemp'])

        # MaxTemp
        maxTemp = float(request.form['maxtemp'])

        # Rainfall
        rainfall = float(request.form['rainfall'])

        # Evaporation
        evaporation = float(request.form['evaporation'])

        # Sunshine
        sunshine = float(request.form['sunshine'])

        # Wind Gust Speed
        windGustSpeed = float(request.form['windgustspeed'])

        # Wind Speed 9am
        windSpeed9am = float(request.form['windspeed9am'])

        # Wind Speed 3pm
        windSpeed3pm = float(request.form['windspeed3pm'])

        # Humidity 9am
        humidity9am = float(request.form['humidity9am'])

        # Humidity 3pm
        humidity3pm = float(request.form['humidity3pm'])

        # Pressure 9am
        pressure9am = float(request.form['pressure9am'])

        # Pressure 3pm
        pressure3pm = float(request.form['pressure3pm'])

        # Temperature 9am
        temp9am = float(request.form['temp9am'])

        # Temperature 3pm
        temp3pm = float(request.form['temp3pm'])

        # Cloud 9am
        cloud9am = float(request.form['cloud9am'])

        # Cloud 3pm
        cloud3pm = float(request.form['cloud3pm'])

        # Cloud 3pm
        location = float(request.form['location'])

        # Wind Dir 9am
        winddDir9am = float(request.form['winddir9am'])

        # Wind Dir 3pm
        winddDir3pm = float(request.form['winddir3pm'])

        # Wind Gust Dir
        windGustDir = float(request.form['windgustdir'])

        # Rain Today
        rainToday = float(request.form['raintoday'])

        input_lst = [location, minTemp, maxTemp, rainfall, evaporation, sunshine, windGustDir,
                     windGustSpeed, winddDir9am, winddDir3pm, windSpeed9am, windSpeed3pm,
                     humidity9am, humidity3pm, pressure9am, pressure3pm, cloud9am, cloud3pm, temp9am, temp3pm, rainToday, month, day]

        # Convert the input list to a numpy array
        input_arr = np.array(input_lst)


# Reshape the array to have 1 row and unknown number of columns (-1)
        input_arr = input_arr.reshape(1, -1)

        # Create a credentials object from the access token and refresh token
        creds = Credentials(
            ACCESS_TOKEN,
            token_uri=TOKEN_URI,
            refresh_token=REFRESH_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build('gmail', 'v1', credentials=creds)

        pred = model.predict(input_arr)

        output = pred
        if output == 0:
            try:
                subject = 'Rainfall Notification'
                message = f'Hello there,<b>there</b> will be no rain in  on your desired date.Enjoy with your friends and family. Thankyou'
                msg = MIMEText(message)
                msg['to'] = user_email
                msg['subject'] = subject
                raw_message = base64.urlsafe_b64encode(
                    msg.as_bytes()).decode('utf-8')
                send_message = {'raw': raw_message}
                send_message = (service.users().messages().send(
                    userId="me", body=send_message).execute())
                print(
                    F'The email was sent to {user_email} with email Id: {send_message["id"]}')
            except HttpError as error:
                print(F'An error occurred: {error}')
                send_message = None

            return render_template("sunnyday.html")

        else:
            try:
                subject = 'Rainfall Notification'
                message = f'hello there, <b>there</b> will be rain on your desired date, please take care while going outside. Thankyou'
                msg = MIMEText(message)
                msg['to'] = user_email
                msg['subject'] = subject
                raw_message = base64.urlsafe_b64encode(
                    msg.as_bytes()).decode('utf-8')
                send_message = {'raw': raw_message}
                send_message = (service.users().messages().send(
                    userId="me", body=send_message).execute())
                print(
                    F'The email was sent to {user_email} with email Id: {send_message["id"]}')
            except HttpError as error:
                print(F'An error occurred: {error}')
                send_message = None

            return render_template("rainyday.html")
    return render_template("prediction.html")


# for email message
CLIENT_ID = '279094025508-q5l5k4l57i8lpjq09239bvoj2n0t4j76.apps.googleusercontent.com'
CLIENT_SECRET = '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'
ACCESS_TOKEN = 'ya29.a0AWY7Cknd122xtcmAm9BswRDKqMR1N20uKN-d7kzI3nwBT6_sxpryku4LGot2GxAkhOklCkahToGZfXd5KySDz6Qmarc6VjLwSwKGESy67SL82ClIkaKpp9dNlT_Ab0ZZZJ2MPSBeO3Lt2yNam0_hYmYUEeY9aCgYKAawSARESFQG1tDrpP7gpRvOaAydmmlAagrRDug0163'
REFRESH_TOKEN = '1//    04KTZsKHl30GxCgYIARAAGAQSNwF-L9Ir93qmnAzADRxj0K5RiQG_5f4pUkC2_dhUTUHPWZpaoI3T4E3kVHNf2whE799rgczlE6A'
TOKEN_URI = 'https://oauth2.googleapis.com/token'


@ app.route("/email", methods=['GET', 'POST'])
def email():
    if request.method == "POST":
        try:
            # Create a credentials object from the access token and refresh token
            creds = Credentials(
                ACCESS_TOKEN,
                token_uri=TOKEN_URI,
                refresh_token=REFRESH_TOKEN,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())


# Create a Gmail API service client
            service = build('gmail', 'v1', credentials=creds)

            to = request.form['receiver_email']

            subject = 'Rainfall Notification'
            message = request.form['message']
            msg = MIMEText(message)
            msg['to'] = to
            msg['subject'] = subject
            raw_message = base64.urlsafe_b64encode(
                msg.as_bytes()).decode('utf-8')

            send_message = {'raw': raw_message}
            send_message = (service.users().messages().send(
                userId="me", body=send_message).execute())
            print(
                F'The email was sent to {to} with email Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None

    return render_template('email.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


if __name__ == '__main__':
    app.run(Debug=True)
