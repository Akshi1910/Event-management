# app.py
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime
from flask import session
from flask import request


app = Flask(__name__)

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="college"
)
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS self_development_events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        description TEXT,
        event_date DATE,
        location VARCHAR(255),
        contact_person VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
db.commit()

cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_id INT,
        student_name VARCHAR(255),
        email VARCHAR(255),
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES self_development_events(id)
    )
""")
db.commit()


@app.route('/view_self_dev_events')
def view_self_dev_events():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM self_development_events")
    events = cursor.fetchall()  # Fetch all events
    cursor.close()
    return render_template('self_dev_events.html', events=events)
@app.route('/self_dev_add_event', methods=['GET', 'POST'])
def add_self_dev_event():
    if request.method == 'POST':
        title = request.form.get("title")
        description = request.form.get("description")
        event_date = request.form.get("event_date")
        location = request.form.get("location")
        contact_person = request.form.get("contact_person")
        form_link = request.form.get("form_link")  # Get the form link from the form
        
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO self_development_events (title, description, event_date, location, contact_person, form_link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, event_date, location, contact_person, form_link))
        db.commit()

        return redirect(url_for('view_self_dev_events'))
    
    return render_template('add_self_dev_event.html')

@app.route('/register', methods=['GET', 'POST'])
def register_event():
    event_id = request.args.get('event_id')  # Get event_id from the query string
    if not event_id:
        return "Event ID is missing", 400

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM self_development_events WHERE id = %s", (event_id,))
    event = cursor.fetchone()
    cursor.close()

    if not event:
        return "Event not found", 404

    if request.method == 'POST':
        student_name = request.form['student_name']
        email = request.form['email']

        # Insert registration data into the registrations table
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO registrations (event_id, student_name, email)
            VALUES (%s, %s, %s)
        """, (event_id, student_name, email))
        db.commit()
        cursor.close()

        return "Registration successful!"

    return render_template('register_event.html', event=event)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    cursor = db.cursor()
    
    # Delete the event from the database
    cursor.execute("""
        DELETE FROM self_development_events WHERE id = %s
    """, (event_id,))
    db.commit()
    
    return redirect(url_for('view_self_dev_events'))

# Route to view all events
@app.route('/self_dev_events')
def view_self_dev():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM self_development_events ORDER BY event_date")
    events = cursor.fetchall()
    return render_template('view_self_dev_events.html', events=events)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Add more routes as needed for other pages
@app.route('/services')
def services():
    return render_template('food.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

