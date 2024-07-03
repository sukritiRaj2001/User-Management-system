from flask import Flask, render_template, request, redirect, send_file, url_for
from flask_mysqldb import MySQL
import pdfkit

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'deepak'
app.config['MYSQL_DB'] = 'Python'
app.config['MYSQL_PORT'] = 3306  # Default MySQL port

mysql = MySQL(app)

# Specify the path to the wkhtmltopdf executable
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

def create_users_table():
    with app.app_context():
        # Check if the users table exists
        cur = mysql.connection.cursor()
        cur.execute("SHOW TABLES LIKE 'users'")
        result = cur.fetchone()
        cur.close()

        if not result:
            # Create the users table if it doesn't exist
            cur = mysql.connection.cursor()
            cur.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    dob DATE NOT NULL,
                    gender ENUM('male', 'female', 'other') NOT NULL
                )
            """)
            mysql.connection.commit()
            cur.close()

# Create the users table if it doesn't exist
create_users_table()

@app.route('/')
def index():
    # Fetch all users from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, dob, gender FROM users")
    users = cur.fetchall()
    cur.close()

    return render_template('index.html', users=users)

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Delete the user with the specified id from the database
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        dob = request.form['dob']
        gender = request.form['gender']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, dob, gender) VALUES (%s, %s, %s, %s)", (name, email, dob, gender))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, dob, gender FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()

    if user_data:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            dob = request.form['dob']
            gender = request.form['gender']

            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET name = %s, email = %s, dob = %s, gender = %s WHERE id = %s",
                        (name, email, dob, gender, user_id))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('index'))
        else:
            return render_template('edit.html', user=user_data)
    else:
        return 'User not found', 404
    
@app.route('/generate_pdf')
def generate_pdf():
    # Fetch all users from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, dob, gender FROM users")
    users = cur.fetchall()
    cur.close()

    # Render the HTML template to a string
    rendered_html = render_template('pdf_template.html', users=users)

    # Generate PDF from HTML using pdfkit
    pdf = pdfkit.from_string(rendered_html, False, configuration=config)  # Pass the configuration

    # Save the generated PDF to a file
    pdf_filename = 'users.pdf'
    with open(pdf_filename, 'wb') as f:
        f.write(pdf)

    # Return the generated PDF as a downloadable attachment
    return send_file(pdf_filename, as_attachment=True, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
