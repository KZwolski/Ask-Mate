from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from bonus_questions import SAMPLE_QUESTIONS
import data_manager
import os
import util

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static\\images'
app.secret_key = 'dupa'

FILE = "data/question.csv"
answer_path = "data/answer.csv"
FIELDNAMES = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']


@app.route("/")
def index():
    last_five = data_manager.get_last_five_questions()
    return render_template('index.html', last_five=last_five)


@app.route("/list", methods=["GET", "POST"])
def display_list():
    question_details = data_manager.get_questions()
    sort_by = request.args.get("order_by")
    order = request.args.get("order_direction")
    titles = ['ID', 'Submission Time', 'View Number', 'Vote Number', 'Title']
    if sort_by:
        question_details = data_manager.get_questions_sorted(sort_by, order)
    return render_template('list.html', questions=question_details, titles=titles)


@app.route("/search", methods=["GET", "POST"])
def searched_question():
    searched = request.args.get("question")
    search_question = data_manager.search_questions(searched)
    titles = ['ID', 'Title', 'Message']
    return render_template('list.html', questions=search_question, titles=titles, searched=searched)


@app.route("/question/<question_id>")
def display_question(question_id: int):
    question = data_manager.get_a_question(question_id)
    answers = data_manager.get_answers(question_id)
    return render_template("display_question.html", question=question, answers=answers)


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    header = "Add question"
    title = "Title"
    message = "Question"
    action = "/add-question"
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']
        new_id = data_manager.max_id() + 1
        image_path = None
        if request.files['image']:
            filename = secure_filename(request.files['image'].filename)
            request.files['image'].save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = 'images/%s' % filename
        data_manager.save_question(new_id, title, question, image_path)
        return redirect("/list")
    return render_template('add-question.html', header=header, old_title=title, old_question=message, action=action)


@app.route("/question/<question_id>/delete", methods=["GET"])
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect("/list")


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    header = "Edit question"
    title = "Title"
    message = "Question"
    action = f"/question/{question_id}/edit"
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']
        image_path = None
        if request.files['image']:
            filename = secure_filename(request.files['image'].filename)
            request.files['image'].save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = 'images/%s' % filename
        data_manager.edit_question(question_id, title, question, image_path)
        return redirect(f"/question/{question_id}")
    return render_template('add-question.html', header=header, old_title=title, old_question=message, action=action)


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def add_answer(question_id):
    action = f"/question/{question_id}/new-answer"
    if request.method == 'POST':
        message = request.form['message']
        data_manager.save_answer(question_id, message)
        return redirect(f"/question/{question_id}")
    return render_template('add-answer.html', action=action, question_id=question_id)


@app.route("/answer/<answer_id>/delete", methods=["GET"])
def delete_answer(answer_id):
    data_manager.delete_answer(answer_id)

    return redirect("/list")


@app.route("/register")
def register_page():
    if 'user' in session:
        flash('You need to log out first!')  # TO BE CHANGED INTO JS
        return redirect('/')
    else:
        return render_template('register.html')


@app.route("/register", methods=['POST'])
def register_user():
    user_details = dict()
    user_details['username'] = request.form['register-username']
    user_details['email'] = request.form['register-email']
    user_details['password'] = util.hash_password(request.form['register-password'])
    user_details['registration_date'] = util.get_current_time()
    if data_manager.check_if_user_exists(user_details['username'], user_details['email']):
        flash('Username or Email already exists!')  # TO BE CHANGED INTO JS
        return redirect(url_for('register_page'))
    else:
        data_manager.register_user(user_details)
        return redirect(url_for('index'))


@app.route("/bonus-questions")
def main():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS)


@app.route("/users")
def users_list():
    users_details = data_manager.get_users_details()
    return render_template("users.html", users_details=users_details)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    users = data_manager.get_users_details()
    if request.method == 'POST':
        for user in users:
            if request.form['username'] == user['username'] and util.verify_password(request.form['password'],
                                                                                     user['password']):
                session["user"] = request.form['username']
                return redirect("/")
            else:
                error = "Invalid login attempt"
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route('/user')
def account_details():
    return render_template('user.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=5000,
            debug=True)
