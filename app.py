'''For this project we used python external library files for web frame work we used flask module and store the data of participants we used mysql.connector modul so that we have to install both the modules. 
Here is the stps for install modules:
You have to install the python software version 3.2 and above that installed in administarator folder by default it takes administrater folder don't make any changes otherwise it shows "pip is not recognised"
Open cmd and type "pip install flask" then hit enter. (make sure that your system connected to network or not because data connection is required for installataion process)
afterwards same process for mysql.connector "pip install mysql.connector"
'''

from flask import Flask, render_template, request, redirect, url_for, session  # Flask for web framework
from datetime import datetime, timezone  # For handling date and time(inbuilt module)
import random  # For generating random numbers
import time  # For timing functions
import smtplib  # For sending emails(inbuilt module in the Python 3.2 version)
import mysql.connector  # For interacting with MySQL database

#Note: All the files are saved in same directry. otherwise it "flask module didn't render or not link the all webpages"

# Initialize the Flask application
app = Flask(__name__)

# Defining of global variables

# List of operators used in math problems
OPERATORS = ["+", "-", "*"]

# Minimum and maximum number of operators in a math problem
MIN_OPERATORS = 3
MAX_OPERATORS = 12

# Total number of problems in the quiz
TOTAL_PROBLEMS = 10

# Function to generate a random math problem
def generate_problem():
    # Generate random left and right operands and choose a random operator
    left = random.randint(MIN_OPERATORS, MAX_OPERATORS)
    right = random.randint(MIN_OPERATORS, MAX_OPERATORS)
    operator = random.choice(OPERATORS)
    # Create the expression and evaluate the answer
    expr = str(left) + " " + operator + " " + str(right)
    answer = eval(expr)
    return expr, answer

# Function to calculate the grade based on the score
def calculate_grade(score):
    if score == TOTAL_PROBLEMS:
        return "Awesome! You got all the answers correct...!"                        #if the user got all the questions correct 
    elif score >= TOTAL_PROBLEMS * 0.8:                                             
        return "Great! You got {} out of {}.".format(score, TOTAL_PROBLEMS)         #if the user got percentage 80<=Marks>90 then prints this statement
    elif score >= TOTAL_PROBLEMS * 0.6:
        return "Good! You got {} out of {}.".format(score, TOTAL_PROBLEMS)          #if the user got percentage 60<=Marks>80 then prints this statement
    else:
        return "Try again...! You got {} out of {}.".format(score, TOTAL_PROBLEMS)  #if the user got percentage less then 60% prints this statement

# Function to send an email
def send_email(receiver_email, subject, body):
    # Sender's email and password
    sender_email = "example@gmail.com"
    sender_password = "ghyt hbky ijho sant"    '''Create the app passward in your 
    Google account by enabling the 2-Step Verification
    afterwards you can see create app passward option 
    then create and enter here.
    This is example I entered here.''' 
    # Construct the email message
    message = f"Subject: {subject}\n\n{body}"
    # Connect to SMTP server and send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)

# Function to connect to the database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="mysql(Enter your MySQL account username)",     #Enter the sql account user name. By default it get it as'root' in windows 
        password="Enter Your SQL account Password",          #Enter the SQL Account Password 
        database="quiz_data"
    )

# Function to create the database table
def create_table():
    # Connect to the database and create a cursor
    with connect_db() as conn:
        c = conn.cursor()
        # Create the table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255),
                        email VARCHAR(255),
                        marks INT,
                        time_taken FLOAT
                    )''')
        conn.commit()

# Function to insert data into the database
def insert_data(name, email, marks, time_taken):
    # Connect to the database and create a cursor
    with connect_db() as conn:
        c = conn.cursor()
        # Insert data into the table
        c.execute("INSERT INTO quiz_results (name, email, marks, time_taken) VALUES (%s, %s, %s, %s)", (name, email, marks, time_taken))
        conn.commit()

# Function to fetch participants data from the database
def fetch_participants():
    # Connect to the database and create a cursor
    with connect_db() as conn:
        c = conn.cursor()
        # Execute SQL query to fetch data
        c.execute("SELECT name, marks, time_taken FROM quiz_results")
        return c.fetchall()

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for starting the quiz
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Capture the start time in UTC
        session['start_time'] = datetime.now(timezone.utc)
        # Get user's name and email from the form
        name = request.form.get('name')
        email = request.form.get('email')
        # If name and email are provided, set them in the session and redirect to the first problem
        if name and email:
            session['name'] = name
            session['email'] = email
            return redirect(url_for('problem', problem_number=1))
        # If name or email is missing, show an error message
        else:
            error_message = "Please provide both your name and email."
            return render_template('quiz.html', error_message=error_message)
    # Render the quiz template for GET requests
    return render_template('quiz.html')

# Route for displaying the math problems
@app.route('/problem/<int:problem_number>', methods=['GET', 'POST'])
def problem(problem_number):
    # If problem number exceeds the total number of problems, redirect to the results page
    if problem_number > TOTAL_PROBLEMS:
        return redirect(url_for('results'))
    
    # If the request method is POST, check the user's answer and redirect to the next problem
    if request.method == 'POST':
        # Get the user's answer from the form
        user_answer = request.form.get('answer')
        try:
            user_answer = int(user_answer)
        except ValueError:
            user_answer = None
        
        # Get the real answer for the current problem from the session
        real_answer = session.get(f'problem_{problem_number}_answer')
        # Check if the user's answer is correct or incorrect and store the result in the session
        if user_answer == real_answer:
            session[f'problem_{problem_number}_result'] = 'Correct'
        else:
            session[f'problem_{problem_number}_result'] = 'Incorrect'
        
        # Redirect to the next problem
        return redirect(url_for('problem', problem_number=problem_number + 1))
    
    # If the request method is GET, generate a new problem and render the problem template
    expr, answer = generate_problem()
    session[f'problem_{problem_number}_answer'] = answer
    return render_template('problem.html', problem_number=problem_number, expression=expr)

# Route for displaying the quiz results
@app.route('/results')
def results():
    # Capture the end time in UTC
    end_time = datetime.now(timezone.utc)
    start_time = session.get('start_time')
    
    # Calculate the total time taken for the quiz
    if start_time and end_time > start_time:
        total_time = (end_time - start_time).total_seconds()
    else:
        total_time = 0

    # Calculate the score based on the number of correct answers
    score = sum(session.get(f'problem_{i}_result', 'Incorrect') == 'Correct' for i in range(1, TOTAL_PROBLEMS+1))
    # Calculate the grade based on the score
    grade_message = calculate_grade(score)
    # Get the receiver's email from the session
    receiver_email = session.get('email')
    # Construct the email subject and body
    subject = "Quiz Results"
    body = f"Hello {session.get('name')},\n\n You attended the SUIET Students Conducted Quiz. Here is  your quiz result:\nScore: {score}/{TOTAL_PROBLEMS}\nGrade: {grade_message}\nTotal Time taken to complete the quiz: {total_time} seconds\n\n\nRegards,\nSUIET Quiz Team"
    try:
        # Send the email
        send_email(receiver_email, subject, body)
        email_sent = True
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
        email_sent = False
    
    # Insert quiz data into the database
    name = session.get('name')
    email = session.get('email')
    insert_data(name, email, score, total_time)

    # Fetch participants data from the database
    participants_data = fetch_participants()

    print(participants_data)  # Print participants data for debugging

    # Render the results template with necessary data
    return render_template('results.html', score=score, grade_message=grade_message, total_time=total_time, total_problems=TOTAL_PROBLEMS, email_sent=email_sent, participants=participants_data)

# Run the Flask application
if __name__ == '__main__':
    app.secret_key = 'teamSUIET'
    create_table()  # Create the database table
    app.run(debug=True)
