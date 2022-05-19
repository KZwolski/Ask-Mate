from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from bonus_questions import SAMPLE_QUESTIONS
import data_manager
import os
import util

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = 'dupa'


def get_reputation_value(table, negative=False, accepted=False):
    if accepted:
        return 15 if not negative else -15
    values = {'answer': 10, 'question': 5}
    return values[table] if not negative else values[table] * -1


def error_message():
    body = """  <script>
                        alert("You are not logged in")
                        window.location.href = '/login' 
                        </script>
                    """
    return body


@app.route("/")
def index():
    last_five = data_manager.get_questions(limit=5)
    return render_template('index.html', last_five=last_five)


@app.route("/list")
def display_list():
    question_details = data_manager.get_questions()
    sort_by = request.args.get("order_by")
    order = request.args.get("order_direction")
    if sort_by:
        question_details = data_manager.get_questions(sort_by=sort_by, order=order)
    return render_template('list.html', questions=question_details)


@app.route("/search")
def searched_question():
    searched = request.args.get("question")
    search_question = data_manager.search_questions(searched)
    return render_template('list.html', questions=search_question, searched=searched)


@app.route("/question/<question_id>")
def display_question(question_id: int):
    question = data_manager.get_a_question(question_id)
    answers = data_manager.get_answers(question_id)
    comments = data_manager.get_comments(question_id)
    data_manager.edit_views(question_id)
    edit_rights = False if 'id' not in session else data_manager.user_rights_to_edit(session['id'], question_id,"question")
    return render_template("display_question.html", question=question, answers=answers, comments=comments,
                           edit=edit_rights)


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if 'user' not in session:
        user_logout = True
        return render_template('add-question.html', user_logout=user_logout)
    else:
        if request.method == 'POST':
            title = request.form['title']
            message = request.form['question']
            username = session['user']
            image_path = None
            if request.files['image']:
                filename = secure_filename(request.files['image'].filename)
                request.files['image'].save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_path = 'images/%s' % filename
            data_manager.save_question(username, title, message, image_path)
            return redirect("/list")
        return render_template('add-question.html')


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['question']
        image_path = None
        if request.files['image']:
            filename = secure_filename(request.files['image'].filename)
            request.files['image'].save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = 'images/%s' % filename
        data_manager.edit_question(question_id, title, message, image_path)
        return redirect(f'/question/{question_id}')
    else:
        title = data_manager.get_a_question(question_id)['title']
        message = data_manager.get_a_question(question_id)['message']
        return render_template('edit-question.html', title=title, message=message)


@app.route("/question/<question_id>/delete", methods=["GET"])
def delete_question(question_id):
    if 'user' not in session or not data_manager.user_rights_to_edit(session['id'], question_id, "question"):
        return redirect(url_for('index'))
    data_manager.delete_question(question_id)
    return redirect("/list")


@app.route("/question/<question_id>/new-answer", methods=["GET", "POST"])
def add_answer(question_id):
    if 'user' not in session:
        return error_message()
    if request.method == 'POST':
        message = request.form['message']
        username = session['user']
        data_manager.save_answer(question_id, message, username)
        return redirect(f"/question/{question_id}")
    return render_template('add-answer.html', question_id=question_id)


@app.route("/answer/<question_id>/<answer_id>/edit")
def edit_answer(answer_id):
    answer = data_manager.get_an_answer_message(answer_id)
    return render_template('edit_answer.html', answer=answer)


@app.route("/answer/<question_id>/<answer_id>/edit", methods=['POST'])
def edit_answer_post(question_id, answer_id):
    message = request.form['message']
    data_manager.edit_answer(answer_id, message)
    return redirect(f'/question/{question_id}')


@app.route("/answer/<question_id>/<answer_id>/<action>")
def accept_answer(question_id, answer_id, action):
    if 'user' not in session or not data_manager.user_rights_to_edit(session['id'], question_id,"answer"):
        return redirect(url_for('index'))
    if action == 'accept':
        data_manager.mark_answer_as_accepted(question_id, answer_id)
        negative = False
    else:
        data_manager.unmark_accepted_answer(question_id)
        negative = True
    data_manager.change_reputation('answer', answer_id,
                                   get_reputation_value('answer', negative=negative, accepted=True))
    return redirect(f'/question/{question_id}')


@app.route("/answer/<answer_id>/<question_id>/delete", methods=["GET"])
def delete_answer(answer_id, question_id):
    if 'user' not in session or not data_manager.user_rights_to_edit(session['id'], answer_id,'answer'):
        return redirect(url_for('index'))
    data_manager.delete_answer(answer_id, question_id)
    return redirect(f'/question/{question_id}')


@app.route("/register")
def register_page():
    if 'user' in session:
        flash('You need to log out first!')
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
        error = "Username or Email already exists!"
        print(error)
        return render_template("register.html", error=error)
    else:
        data_manager.register_user(user_details)
        return redirect(url_for('login'))


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
        return render_template('users.html', user_logout=user_logout)


@app.route("/user/<user_id>")
def user_page(user_id):
    user = data_manager.get_user_by_id(user_id)
    questions = data_manager.users_questions(user_id)
    answers = data_manager.users_ans(user_id)
    comments = data_manager.users_comments(user_id)
    return render_template('user_page.html', user=user, questions=questions, answers=answers, comments=comments)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if data_manager.check_if_user_can_log(request.form['username']):
            user_details = data_manager.get_users_password(request.form['username'])
            print(user_details)
            print(user_details.get("password"))
            if util.verify_password(request.form['password'], user_details.get("password")):
                session["user"] = request.form['username']
                session["id"] = user_details.get("id")
                return redirect("/")
            else:
                error = "Invalid password"
        else:
            error = "Invalid login"
    return render_template('login.html', error=error)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("user", None)
    session.pop("id", None)
    return redirect(url_for("index"))


@app.route('/thumbup/<table>/<id_to_update>/<id_to_return>')
def thumb_up(table, id_to_update, id_to_return):
    data_manager.thumb_up(table, id_to_update)
    data_manager.change_reputation(table, id_to_update, get_reputation_value(table))
    return redirect(f'/question/{id_to_return}')


@app.route('/thumbdown/<table>/<id_to_update>/<id_to_return>')
def thumb_down(table, id_to_update, id_to_return):
    data_manager.thumb_down(table, id_to_update)
    data_manager.change_reputation(table, id_to_update, get_reputation_value(table, negative=True))
    return redirect(f'/question/{id_to_return}')


@app.route("/question/<question_id>/<answer_id>/new-comment", methods=["GET", "POST"])
def add_comment(question_id, answer_id):
    if 'user' not in session:
        return error_message()
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
