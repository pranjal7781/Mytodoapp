# Flask To-Do List Web Application

A secure, multi-user to-do list application built with Python and the Flask web framework. This project provides a full-featured task management system with user authentication and a clean, responsive user interface.

## 🌟 Features

* **Secure User Authentication:** Users can register for a new account and log in. Passwords are securely hashed and never stored as plain text.
* **Full CRUD Functionality:** Complete Create, Read, Update, and Delete operations for managing tasks.
* **User-Specific Tasks:** Each user can only view and manage their own tasks, ensuring data privacy.
* **Task Management:** Users can add new tasks, edit existing task descriptions, mark tasks as complete, and delete tasks.
* **Responsive Design:** A clean and modern UI that works on both desktop and mobile browsers.


## 🛠️ Technologies Used

* **Backend:** Python, Flask
* **Database:** MsSQL server
* **Templating:** Jinja2
* **Frontend:** HTML, CSS

## ⚙️ Setup and Installation

To run this project locally, follow these steps:

### 1. Prerequisites

Make sure you have the following installed on your system:
* Python (3.8 or higher)
* Git
* MsSQL

### 2. Create `requirements.txt`

**(Action Required):** Before pushing to GitHub, you need to create a `requirements.txt` file that lists all the Python packages your project needs. Run this command in your project's terminal:

```bash
pip freeze > requirements.txt
```

Your `requirements.txt` file should look something like this:
```
Flask
mysql-connector-python
Werkzeug
# Add any other libraries you used, like Flask-Mail or pyodbc
```

### 3. Clone and Set Up the Project

```bash
# 1. Clone the repository
git clone <your-github-repo-url>
cd <your-project-directory>

# 2. Create and activate a virtual environment
# On Windows:
python -m venv venv
venv\Scripts\activate
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# 3. Install the required packages
pip install -r requirements.txt
```

### 4. Database Setup

1.  Log in to your MsSQL server.
2.  Create a new database for the project.
    ```sql
    CREATE DATABASE flask_app;
    USE flask_app;
    ```
3.  Create the necessary tables by running the following SQL commands:
    ```sql
    -- Create the 'users' table
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create the 'tasks' table
    CREATE TABLE tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        task_content VARCHAR(255) NOT NULL,
        is_completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ```

### 5. Configure the Application

Open the `app.py` file and update the MySQL connection details with your own credentials:

```python
# Inside app.py

# ...
conn = mysql.connector.connect(
    host="localhost",
    user="your_mysql_user",      # UPDATE THIS
    password="your_mysql_password",  # UPDATE THIS
    database="flask_app"
)
# ...
```

## ▶️ How to Run

With your virtual environment activated and the database configured, run the following command in your project's root directory:

```bash
flask run
```
Or
```bash
python app.py
```

Open your web browser and navigate to `http://127.0.0.1:5000`.
