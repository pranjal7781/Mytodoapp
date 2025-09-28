from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import re
# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "super_secret_key_change_me"

# --- MySQL Connection ---
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="YOUR USERNAME ",
        password="YOUR PASSWORD HERE", 
        database="DATABASE NAME"
    )
    cursor = conn.cursor(dictionary=True)
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit()

def is_valid_username(username):
    """
    Checks if the username is valid.
    - 4-20 characters long
    - Contains no spaces
    - Contains only alphanumeric characters (a-z, A-Z, 0-9)
    """
    if not (4 <= len(username) <= 20):
        return False, "Username must be between 4 and 20 characters long."
    if ' ' in username:
        return False, "Username cannot contain spaces."
    if not re.match("^[a-zA-Z0-9_]*$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    return True, ""



@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # if user and check_password_hash(user['password'], password):  #for secure password
        if user and (user['password'], password):    
            session['username'] = user['username']
            cursor.execute("INSERT INTO UserLogins (username, status) VALUES (%s, %s)", (username, "success"))
            conn.commit()
            return redirect(url_for('dashboard'))
        else:
            cursor.execute("INSERT INTO UserLogins (username, status) VALUES (%s, %s)", (username, "failed"))
            conn.commit()
            flash("❌ Invalid username or password!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        is_valid, error_message = is_valid_username(username)
        if not is_valid:
            flash(f"❌ {error_message}", "danger")
            return redirect(url_for('register'))

        cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("❌ Username already exists! Please choose another one.", "danger")
            return redirect(url_for('register'))

        # hashed_password = generate_password_hash(password) # for secure password
        hashed_password =(password)


        try:
            cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash("✅ You have successfully registered! Please login.", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"❌ Database error: {err}", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("🔒 Please login to access the dashboard.", "info")
        return redirect(url_for('login'))

    cursor.execute("SELECT id FROM Users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()
    user_id = user['id']

    # Fetch tasks for the logged-in user
    cursor.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    user_tasks = cursor.fetchall()

    return render_template('dashboard.html', username=session['username'], tasks=user_tasks)

# --- NEW: Route to Add a Task ---
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        return redirect(url_for('login'))

    task_content = request.form['task_content']
    
    # Get user_id from the database based on the session username
    cursor.execute("SELECT id FROM Users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()
    user_id = user['id']

    # Insert the new task into the database
    cursor.execute("INSERT INTO tasks (user_id, task_content) VALUES (%s, %s)", (user_id, task_content))
    conn.commit()
    return redirect(url_for('dashboard'))

# --- NEW: Route to Update a Task (Complete/Undo) ---
@app.route('/update_task/<int:task_id>')
def update_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # First, get the current status of the task
    cursor.execute("SELECT is_completed FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task:
        # Flip the status (if it's True, make it False, and vice-versa)
        new_status = not task['is_completed']
        cursor.execute("UPDATE tasks SET is_completed = %s WHERE id = %s", (new_status, task_id))
        conn.commit()
    
    return redirect(url_for('dashboard'))


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    
    
    return redirect(url_for('dashboard'))


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get the logged-in user's ID
    cursor.execute("SELECT id FROM Users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()
    user_id = user['id']

    if request.method == 'POST':
        # This block runs when the user saves the changes
        new_content = request.form['task_content']
        
        # Update the task in the database
        cursor.execute("UPDATE tasks SET task_content = %s WHERE id = %s AND user_id = %s", 
                       (new_content, task_id, user_id))
        conn.commit()
        return redirect(url_for('dashboard'))
    
    else:
        # This block runs when the user first clicks "Edit" (GET request)
        cursor.execute("SELECT * FROM tasks WHERE id = %s AND user_id = %s", (task_id, user_id))
        task_to_edit = cursor.fetchone()

        if task_to_edit:
            # Show the edit page, passing the current task details to it
            return render_template('edit_task.html', task=task_to_edit)
        else:
            # If task doesn't exist or doesn't belong to the user, redirect
            flash("❌ Task not found or you don't have permission to edit it.", "danger")
            return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("👋 You have been successfully logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':

    app.run(debug=True)


