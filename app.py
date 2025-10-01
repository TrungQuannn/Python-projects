from flask import Flask, redirect, render_template, request
import sqlite3

app = Flask(__name__, template_folder='.')


DB_FILE = 'todo.sql'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todo_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Doing',
            editing BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


init_db()

@app.route('/')
def index():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, description, status, editing FROM todo_list')
    todo_list = [
        {"id": row[0], "description": row[1], "status": row[2], "editing": bool(row[3])}
        for row in cursor.fetchall()
    ]
    conn.close()
    return render_template('index.html', todo_list=todo_list)

@app.route('/create', methods=['POST'])
def create_todo():
    description = request.form['description']
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO todo_list (description) VALUES (?)', (description,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/update/<int:id>', methods=['POST'])
def update_todo(id):
    new_description = request.form['description']
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE todo_list 
        SET description = ?, editing = 0 
        WHERE id = ?
    ''', (new_description, id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/toggle/<int:id>', methods=['POST'])
def toggle_status(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM todo_list WHERE id = ?', (id,))
    current_status = cursor.fetchone()[0]
    new_status = 'Done' if current_status == 'Doing' else 'Doing'
    cursor.execute('UPDATE todo_list SET status = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/toggle_editing/<int:id>', methods=['POST'])
def toggle_editing(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT editing FROM todo_list WHERE id = ?', (id,))
    current_editing = cursor.fetchone()[0]
    new_editing = not current_editing
    cursor.execute('UPDATE todo_list SET editing = ? WHERE id = ?', (new_editing, id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_todo(id):    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todo_list WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
