# First import the Flask library file. By the CMD. first to you have download the "PYTHON Software" then open the "CMD" and type "pip install flask"(without qoutes) then hit the ENTER 
from flask import Flask, render_template, request, redirect, url_for, session  # Import necessary modules from Flask
import random                        # Import the random module for generating random numbers
import time                          # Import the time module for timing the quiz

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

@app.route('/')                                                  # Define the route for the home page
def home():
    return render_template('home.html')                          # Render the home.html template

@app.route('/quiz', methods=['GET', 'POST'])                     # Define the route for the quiz page with support for POST requests
def quiz():
    if request.method == 'POST':                                 # If the request method is POST (i.e., form submission)
        session['start_time'] = time.time()                      # Record the start time of the quiz
        return redirect(url_for('problem', problem_number=1))    # Redirect to the first problem
    return render_template('quiz.html')                          # Render the quiz.html template for GET requests

@app.route('/problem/<int:problem_number>', methods=['GET', 'POST'])     # Define the route for individual problems
def problem(problem_number):
    if problem_number > TOTAL_PROBLEMS:                                  # If all problems have been solved
        return redirect(url_for('results'))                              # Redirect to the results page
    if request.method == 'POST':                                         # If the request method is POST (i.e., form submission)
        user_answer = request.form.get('answer', type=int)               # Get the user's answer from the form
        real_answer = session.get(f'problem_{problem_number}_answer')    # Get the real answer from the session
        if user_answer == real_answer:                                   # If the user's answer is correct
            session[f'problem_{problem_number}_result'] = 'Correct'      # Record the result as correct in the session
        else:                                                            # If the user's answer is incorrect
            session[f'problem_{problem_number}_result'] = 'Incorrect'    # Record the result as incorrect in the session
        return redirect(url_for('problem', problem_number=problem_number+1))  # Redirect to the next problem
    expr, answer = generate_problem()                                    # Generate a new arithmetic problem
    session[f'problem_{problem_number}_answer'] = answer                 # Store the answer in the session
    return render_template('problem.html', problem_number=problem_number, expression=expr)  # Render the problem.html template

@app.route('/results')                                                   # Define the route for the results page
def results():
    end_time = time.time()                                               # Record the end time of the quiz
    total_time = round(end_time - session.get('start_time', end_time), 2)# Calculate the total time taken for the quiz
    score = sum(session.get(f'problem_{i}_result', 'Incorrect') == 'Correct' for i in range(1, TOTAL_PROBLEMS+1))  # Calculate the score
    grade_message = calculate_grade(score)                               # Calculate the grade message based on the score
    return render_template('results.html', score=score, grade_message=grade_message, total_time=total_time, total_problems=TOTAL_PROBLEMS)  # Render the results.html template

if __name__ == '__main__':                                               # Run the Flask app if the script is executed directly
    app.secret_key = 'Santhu@93800'                                      # Set a secret key for the session
    app.run(debug=True)                                                  # Run the Flask application in debug mode
