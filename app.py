from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        project = request.form['project']
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form['description']
        date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (project, category, amount, description, date) VALUES (?, ?, ?, ?, ?)',
                     (project, category, amount, description, date))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('add.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    summary = conn.execute('SELECT category, SUM(amount) as total FROM expenses GROUP BY category').fetchall()
    conn.close()
    return render_template('dashboard.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
