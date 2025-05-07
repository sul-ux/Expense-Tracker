from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home - show all expenses
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC',
                            (session['user_id'],)).fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

# Add expense
@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')

    expense = None
    if request.method == 'POST':
        project = request.form['project']
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form['description']
        date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (user_id, project, category, amount, description, date) VALUES (?, ?, ?, ?, ?, ?)',
                     (session['user_id'], project, category, amount, description, date))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('add.html', expense=expense)

# Edit expense
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id = ? AND user_id = ?', (id, session['user_id'])).fetchone()

    if not expense:
        return 'Expense not found or unauthorized', 404

    if request.method == 'POST':
        project = request.form['project']
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form['description']
        date = request.form['date']

        conn.execute('UPDATE expenses SET project=?, category=?, amount=?, description=?, date=? WHERE id=?',
                     (project, category, amount, description, date, id))
        conn.commit()
        conn.close()
        return redirect('/')

    conn.close()
    return render_template('add.html', expense=expense)

# Delete expense
@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/')

# Dashboard with chart
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    summary = conn.execute('SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category',
                           (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', summary=summary)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return 'Username already exists'
        conn.close()
        return redirect('/login')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                            (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            return redirect('/')
        else:
            return 'Invalid credentials'
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
