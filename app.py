from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'quizsecret'


def get_db_connection():
    conn = sqlite3.connect(r'C:\\online_quiz_system\\quiz.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO users(username, password) VALUES (?, ?)',
                (username, password)
            )
            conn.commit()
            return redirect('/login')
        except:
            return 'User already exists!'
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return 'Invalid username or password'

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    return render_template('dashboard.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO questions(question, option1, option2, option3, option4, answer)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (question, option1, option2, option3, option4, answer))

        conn.commit()
        conn.close()

        return 'Question Added Successfully'

    return render_template('add_question.html')


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM questions')
    questions = cursor.fetchall()

    conn.close()

    if request.method == 'POST':
        score = 0

        for q in questions:
            selected = request.form.get(str(q['id']))

            if selected == q['answer']:
                score += 1

        return render_template('result.html', score=score, total=len(questions))

    return render_template('quiz.html', questions=questions)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run()
