from app import app          
from app.database import Database      

from flask import render_template, request, url_for, redirect, session
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app.secret_key = "testing"




# this will be the login page, we need to use both GET and POST requests
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    
    # Check if "id number" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'id_number' in request.form and 'password' in request.form:
        # Create variables for easy access
        id_number = request.form['id_number']
        password = request.form['password']
        # Fetch one record and return result
        temporary_user = Database.find_one("users",{'id_number':id_number})
        # Check if a user was found with specified id_number
        if temporary_user:
            # Compare user's password with hashed password from database
            correct_password = check_password_hash(temporary_user['password'],password)
        
            # If password is correct assign temporary user to be user
            if correct_password:
                user = temporary_user
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                #session['_id'] = user['_id']
                session['id_number'] = user['id_number']
                session['Useremail'] = user['email']
                # Redirect to dashboard page
                return redirect(url_for('dashboard'))
            else:
                # Password is wrong
                msg = 'Password is wrong!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'I.D Number does not exist!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# this will be the logout page
@app.route('/login/logout')
def logout():
   # Remove session data, this will log the user out
   session.pop('loggedin', None)
   #session.pop('_id', None)
   session.pop('id_number', None)
   # Redirect to login page
   return redirect(url_for('login'))

# this will be the registration page, we need to use both GET and POST requests
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "id_number", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'id_number' in request.form:
        # Create variables for easy access
        id_number = request.form['id_number']
        password = request.form['password']
        # Change user's password to hashed password
        hash_password = generate_password_hash(password)
        email = request.form['email']
        # Check if account exists 
        user = Database.find_one("users",{'id_number':id_number})
       
        # If account exists show error and validation checks
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'(^\d{2})-(\d{4,7})\s([A-Z-a-z]{1}\s(\d{2}$))', id_number):
            msg = 'Invalid National ID Card! Enter In Specified Format'
        elif not id_number or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users collection
            employee = {"id_number": id_number, "email": email,"password": hash_password}
            # inititalize available leave days to 3
            availableDays = {"id_number": id_number,"days":36}
            Database.insert("users",employee)
            Database.insert("available_days",availableDays)
            msg = 'You have successfully registered! You can Login'
    
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


#  this will be the home page, only accessible for loggedin users
@app.route('/login/dashboard')
def dashboard():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page 
        id_number = session['id_number']
        # Fetch for the available leave days for the loggedin user
        user = Database.find_one("available_days",{'id_number':id_number})
        # Convert available days to integer
        available_days = int(user['days'])
        # set todays's day
        #toDay = datetime.today()
        # Add a flag variable to determine if we have already incremented
        

        # Check if its first day of a month, if it is increment leave days by 3
        #if toDay == '2021-11-02 20:26:39.834847':
            # Add a flag variable to determine if we have already incremented
            # Update available days by adding 3, since the user gets 3 days each month
            #incrementedDays = available_days + 3
            #available_days = incrementedDays
            #query = {"ec_number": ec_number} 
            #new_value = {"$set":{"days":incrementedDays}}
            #Database.update_one("available_days",query,new_value)
            
                

        return render_template('dashboard.html', id_number=id_number,available_days=available_days)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
    

   