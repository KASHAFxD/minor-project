from flask import Flask, request,render_template, redirect,session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import numpy as np
import pickle

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    number = db.Column(db.Integer)

    def __init__(self,email,password,name,number):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.number = number
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('signup.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        number = request.form['number']

        new_user = User(name=name,email=email,password=password, number=number)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')



    return render_template('signup.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('signup.html',error='Invalid user')

    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('index.html',user=user)
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')


# perediction wala moel start 








# Load your trained model (assuming it's saved in a pickle file)
model = pickle.load(open('heart_disease.pkl', 'rb'))

# Define the preprocessing function
def preprocess_input(data):
    age = float(data['age'])
    restingBP = float(data['restingBP'])
    cholesterol = float(data['cholesterol'])
    fastingBS = 1 if data['fastingBS'] == '>120mg/dL' else 0
    maxHR = float(data['maxHR'])
    oldpeak = float(data['oldpeak'])

    # Gender one-hot encoding
    male = 1 if data['gender'] == 'male' else 0

    # Chest pain one-hot encoding
    cp_ta = 1 if data['chestPain'] == 'typicalAngina' else 0
    cp_nap = 1 if data['chestPain'] == 'nonAnginalPain' else 0
    cp_asym = 1 if data['chestPain'] == 'asymptomatic' else 0

    # Resting ECG one-hot encoding
    ecg_normal = 1 if data['restingECG'] == 'normal' else 0
    ecg_st = 1 if data['restingECG'] == 'st' else 0
    ecg_lvh = 1 if data['restingECG'] == 'lvh' else 0

    # ST slope one-hot encoding
    slope_flat = 1 if data['stslope'] == 'flat' else 0
    slope_up = 1 if data['stslope'] == 'up' else 0

    # Assemble the features into an array
    features = [age, restingBP, cholesterol, fastingBS, maxHR, oldpeak, male, 
                cp_ta, cp_nap, cp_asym, ecg_normal, ecg_st, ecg_lvh, slope_flat, slope_up]
    

    return np.array([features])

@app.route('/test', methods=['GET', 'POST'])
def indexx():
    if request.method == 'POST':
        # Get form data
        form_data = request.form

        # Preprocess the input data
        features = preprocess_input(form_data)

        # Make prediction using the loaded model
        prediction = model.predict(features)
        prediction_proba = model.predict_proba(features)

        # Extract the probability of the predicted class (either class 0 or 1)
        if prediction[0] == 1:
            probability = prediction_proba[0][1] * 100  # Probability of heart disease
            result = 'At risk of heart disease'
        else:
            probability = prediction_proba[0][0] * 100  # Probability of no heart disease
            result = 'Low risk of heart disease'

        return render_template('result.html', result=result, probability=probability, features=features)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
