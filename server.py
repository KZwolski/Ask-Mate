from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from bonus_questions import SAMPLE_QUESTIONS
import data_manager
import os
import util

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static\\images'
app.secret_key = 'dupa'


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
    comments = data_manager.get_comments(question_id)
    data_manager.edit_views(question_id)
    edit_rights = False if 'id' not in session else data_manager.user_rights_to_question(session['id'], question_id)
    return render_template("display_question.html", question=question, answers=answers, comments=comments,
                           edit=edit_rights)


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    header = "Add question"
    title = "Title"
    message = "Question"
    action = "/add-question"
    if request.method == 'POST':
        title = request.form['title']
        question = request.form['question']
        username = session['user']
        image_path = None
        if request.files['image']:
            filename = secure_filename(request.files['image'].filename)
            request.files['image'].save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = 'images/%s' % filename
        data_manager.save_question(username, title, question, image_path)
        return redirect("/list")
    return render_template('add-question.html', header=header, old_title=title, old_question=message, action=action)


@app.route("/question/<question_id>/delete", methods=["GET"])
def delete_question(question_id):
    if 'user' not in session or not data_manager.user_rights_to_question(session['id'], question_id):
        return redirect(url_for('index'))
    data_manager.delete_question(question_id)
    return redirect("/list")


# To be fixed, when editing and not adding an img, the original img is removed
# Also, the html form should be pre-filled with old question and title ~~Seba
@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if 'user' not in session or not data_manager.user_rights_to_question(session['id'], question_id):
        return redirect(url_for('index'))
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
    if 'user' not in session:
        return redirect(url_for('index'))
    action = f"/question/{question_id}/new-answer"
    if request.method == 'POST':
        message = request.form['message']
        username = session['user']
        data_manager.save_answer(question_id, message, username)
        return redirect(f"/question/{question_id}")
    return render_template('add-answer.html', action=action, question_id=question_id)


@app.route("/answer/<question_id>/<answer_id>/accept")
def accept_answer(question_id, answer_id):
    if 'user' not in session or not data_manager.user_rights_to_question(session['id'], question_id):
        return redirect(url_for('index'))
    data_manager.mark_answer_as_accepted(question_id, answer_id)
    data_manager.change_reputation('answer', answer_id, 5)
    return redirect(f'/question/{question_id}')


@app.route("/answer/<question_id>/<answer_id>/remove-accepted-answer")
def remove_accepted_answer(question_id, answer_id):
    if 'user' not in session or not data_manager.user_rights_to_question(session['id'], question_id):
        return redirect(url_for('index'))
    data_manager.unmark_accepted_answer(question_id)
    data_manager.change_reputation('answer', answer_id, -5)
    return redirect(f'/question/{question_id}')


@app.route("/answer/<answer_id>/delete", methods=["GET"])
def delete_answer(answer_id):
    if 'user' not in session or not data_manager.user_rights_to_answer(session['id'], answer_id):
        return redirect(url_for('index'))
    data_manager.delete_answer(answer_id)
    return redirect("/list")  # <---------------------- Should redirect to a question


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
        flash('Username or Email already exists!')  # <---------- TO BE CHANGED INTO JS
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
    if 'user' in session:
        return render_template("users.html", users_details=users_details)
    else:
        user_logout = True
        return render_template('login.html', user_logout=user_logout)



@app.route("/user/<user_id>")
def user_page(user_id):
    user = data_manager.get_user_by_id(user_id)
    questions = data_manager.users_questions(user_id)
    answers = data_manager.users_ans(user_id)
    comments = data_manager.users_comments(user_id)
    print(questions)
    print(user_id)
    return render_template('user_page.html', user=user, questions=questions, answers=answers, comments=comments)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    users = data_manager.get_users_details()
    if request.method == 'POST':
        for user in users:
            if request.form['username'] == user['username'] and util.verify_password(request.form['password'],
                                                                                     user['password']):
                session["user"] = request.form['username']
                session["id"] = user["id"]
                return redirect("/")
            else:
                error = "Invalid login attempt"
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("user", None)
    session.pop("id", None)
    return redirect(url_for("index"))


@app.route('/thumbup/<table>/<id_to_update>/<id_to_return>')
def thumbup(table, id_to_update, id_to_return):
    data_manager.thumb_up(table, id_to_update)
    return redirect(f'/question/{id_to_return}')


@app.route('/thumbdown/<table>/<id_to_update>/<id_to_return>')
def thumb_down(table, id_to_update, id_to_return):
    data_manager.thumb_down(table, id_to_update)
    return redirect(f'/question/{id_to_return}')


@app.route("/question/<question_id>/<answer_id>/new-comment", methods=["GET", "POST"])
def add_comment(question_id, answer_id):
    if 'user' not in session:
        return redirect(url_for('index'))
    action = f"/question/{question_id}/{answer_id}/new-comment"
    if request.method == 'POST':
        message = request.form['message']
        username = session['user']
        data_manager.save_comment(question_id, answer_id, message, username)
        return redirect(f"/question/{question_id}")
    return render_template('add-answer.html', action=action, question_id=question_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=5000,
            debug=True)
