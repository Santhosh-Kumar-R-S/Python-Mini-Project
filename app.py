# First import the Flask library file. By the CMD. first to you have download the "PYTHON Software" then open the "CMD" and type "pip install flask"(without quotes) then hit the ENTER 
from flask import Flask, render_template, request, redirect, url_for, session  # Import necessary modules from Flask
import random                        # Import the random module for generating random numbers
import time                          # Import the time module for timing the quiz
import smtplib                       # Import smtplib for sending emails

app = Flask(__name__)                # Create a Flask application instance

# Define constants for the quiz
OPERATORS = ["+", "-", "*"]          # Define the list of operators used in the quiz
MIN_OPERATORS = 3                    # Define the minimum value for the operands
MAX_OPERATORS = 12                   # Define the maximum value for the operands
TOTAL_PROBLEMS = 10                  # Define the total number of problems in the quiz

def generate_problem():                                         # Define a function to generate arithmetic problems
    left = random.randint(MIN_OPERATORS, MAX_OPERATORS)         # Generate a random left operand
    right = random.randint(MIN_OPERATORS, MAX_OPERATORS)        # Generate a random right operand
    operator = random.choice(OPERATORS)                         # Choose a random operator from the list
    expr = str(left) + " " + operator + " " + str(right)        # Create the arithmetic expression
    answer = eval(expr)                                         # Calculate the answer
    return expr, answer                                         # Return the expression and the answer

def calculate_grade(score):                                     # Define a function to calculate the grade based on the score
    if score == TOTAL_PROBLEMS:                                 # If all answers are correct
        return "Awesome! You got all the answers correct...!"
    elif score >= TOTAL_PROBLEMS * 0.8:                         # If score is 80% or higher
        return "Great! You got {} out of {}.".format(score, TOTAL_PROBLEMS)
    elif score >= TOTAL_PROBLEMS * 0.6:                         # If score is between 60% and 80%
        return "Good! You got {} out of {}.".format(score, TOTAL_PROBLEMS)
    else:                                                        # If score is less than 60%
        return "Try again...! You got {} out of {}.".format(score, TOTAL_PROBLEMS)

def send_email(receiver_email, subject, body):
    sender_email = "quizteamsuiet@gmail.com"   # Enter your email address here
    sender_password = "nrca uvcm dkmt gowl"    # Enter your email password here

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)

@app.route('/')                                                  # Define the route for the home page
def home():
    return render_template('home.html')                          # Render the home.html template

@app.route('/quiz', methods=['GET', 'POST'])                     # Define the route for the quiz page with support for POST requests
def quiz():
    if request.method == 'POST':
        session['start_time'] = time.time()
        name = request.form.get('name')
        email = request.form.get('email')
        if name and email:  # Check if both name and email are provided
            session['name'] = name
            session['email'] = email
            return redirect(url_for('problem', problem_number=1))
        else:
            error_message = "Please provide both your name and email."
            return render_template('quiz.html', error_message=error_message)
    return render_template('quiz.html')

@app.route('/problem/<int:problem_number>', methods=['GET', 'POST'])     # Define the route for individual problems
def problem(problem_number):
    if problem_number > TOTAL_PROBLEMS:
        return redirect(url_for('results'))
    
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        try:
            user_answer = int(user_answer)  # Convert the user's answer to an integer
        except ValueError:
            # Handle the case where the user's answer is not a valid integer
            user_answer = None
        
        real_answer = session.get(f'problem_{problem_number}_answer')
        if user_answer == real_answer:
            session[f'problem_{problem_number}_result'] = 'Correct'
        else:
            session[f'problem_{problem_number}_result'] = 'Incorrect'
        
        return redirect(url_for('problem', problem_number=problem_number + 1))
    
    expr, answer = generate_problem()
    session[f'problem_{problem_number}_answer'] = answer
    return render_template('problem.html', problem_number=problem_number, expression=expr)

@app.route('/results')                                                   # Define the route for the results page
def results():
    end_time = time.time()                                               # Record the end time of the quiz
    total_time = round(end_time - session.get('start_time', end_time), 2)# Calculate the total time taken for the quiz
    score = sum(session.get(f'problem_{i}_result', 'Incorrect') == 'Correct' for i in range(1, TOTAL_PROBLEMS+1))  # Calculate the score
    grade_message = calculate_grade(score)                               # Calculate the grade message based on the score

    # Sending results via email
    receiver_email = session.get('email')
    subject = "Quiz Results"
    body = f"Hello {session.get('name')},\n\n You attended the SUIET Students Conducted Quiz. Here are your quiz results:\nScore: {score}/{TOTAL_PROBLEMS}\nGrade: {grade_message}\nTotal Time taken to complete the quiz: {total_time} seconds"

    try:
        send_email(receiver_email, subject, body)  # Attempt to send email
        email_sent = True  # Set email_sent variable to True if email is successfully sent
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
        email_sent = False  # Set email_sent variable to False if there's an error sending the email

    return render_template('results.html', score=score, grade_message=grade_message, total_time=total_time, total_problems=TOTAL_PROBLEMS, email_sent=email_sent)  # Pass email_sent variable to template

if __name__ == '__main__':                                               # Run the Flask app if the script is executed directly
    app.secret_key = 'Santhu@93800'                                      # Set a secret key for the session
    app.run(debug=True)                                                  # Run the Flask application in debug mode
