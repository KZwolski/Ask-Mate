import connection
from psycopg2.extras import RealDictCursor
import util


@connection.connection_handler
def get_questions(cursor: RealDictCursor) -> list:
    query = """
        SELECT id, submission_time, view_number, vote_number, title
        FROM question
        ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_questions_sorted(cursor: RealDictCursor, sort_by, order_direction) -> list:
    query = f"""
        SELECT id, submission_time, view_number, vote_number, title
        FROM question
        ORDER BY {sort_by} {order_direction}"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_a_question(cursor: RealDictCursor, searched_id):
    query = f"""
        SELECT q.*, u.username
        FROM question q
        LEFT JOIN users u ON q.user_id = u.id
        WHERE q.id = {searched_id}"""
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def search_questions(cursor, phrase):
    sql = '''SELECT id, title, message from question
            WHERE message LIKE %(phrase)s OR title LIKE %(phrase)s OR message LIKE %(phrase)s 
            '''
    value = {'phrase': '%' + phrase + '%'}
    cursor.execute(sql, value)
    questions = cursor.fetchall()

    return questions


@connection.connection_handler
def get_last_five_questions(cursor: RealDictCursor) -> list:
    query = """
        SELECT submission_time, title, id, view_number, vote_number,message
        FROM question
        ORDER BY submission_time DESC 
        LIMIT 5"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_answers(cursor: RealDictCursor, question_id):
    query = f"""
        SELECT u.username, a.submission_time, a.vote_number, a.message, a.id, a.user_id
        FROM answer as a
        INNER JOIN users as u ON a.user_id = u.id
        WHERE a.question_id = {question_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_an_answer_message(cursor: RealDictCursor, answer_id):
    query = f"""
        SELECT a.message
        FROM answer a
        WHERE a.id = {answer_id}"""
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def edit_answer(cursor: RealDictCursor, answer_id, message):
    query = """
        UPDATE answer
        SET message = %(message)s
        WHERE id = %(answer_id)s
        """
    cursor.execute(query, {'answer_id': answer_id, 'message': message})


@connection.connection_handler
def get_comments(cursor: RealDictCursor, searched_id):
    query = f"""
        SELECT u.username, a.submission_time, a.answer_id, a.message, a.id
        FROM comment as a
        INNER JOIN users as u ON a.user_id = u.id
        WHERE a.question_id = {searched_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def save_question(cursor: RealDictCursor, username, question_title, message, image):
    query = '''
        INSERT INTO question(submission_time, user_id, view_number, vote_number, title, message, image)
        VALUES (
        %(time)s, 
        (SELECT u.id FROM users u WHERE u.username = %(username)s),
        %(view_n)s, 
        %(vote_n)s, 
        %(title)s,
        %(message)s, 
        %(image)s
        )
        '''
    cursor.execute(query, {'time': util.get_current_time(), 'username': username, 'view_n': 0, 'vote_n': 0,
                           'title': question_title, 'message': message, 'image': image})


@connection.connection_handler
def delete_question(cursor: RealDictCursor, id_to_delete):
    query = '''
        UPDATE comment
        SET answer_id = NULL
        WHERE question_id = %(id_to_delete)s;
        UPDATE answer,comment
        SET question_id =  NULL
        WHERE question_id = %(id_to_delete)s;
        DELETE FROM question,answer,comment WHERE id = %(id_to_delete)s;
        '''
    value = {'id_to_delete': id_to_delete}
    cursor.execute(query, value)


@connection.connection_handler
def edit_question(cursor: RealDictCursor, changed_id, question_title, message, image):
    query = '''
        UPDATE question
        SET submission_time = %(time)s, title = %(title)s, message = %(message)s, image= %(image)s
        WHERE id = %(changed_id)s
        '''
    cursor.execute(query, {'time': util.get_current_time(), 'title': question_title,
                           'message': message, 'image': image, 'changed_id': changed_id})


@connection.connection_handler
def edit_views(cursor: RealDictCursor, changed_id):
    query = '''
        UPDATE question
        SET view_number = view_number +1
        WHERE id = %(changed_id)s
        '''
    cursor.execute(query, {'changed_id': changed_id})


@connection.connection_handler
def save_answer(cursor: RealDictCursor, question_id, message, username):
    query = '''
        INSERT INTO answer(submission_time, user_id, vote_number, question_id, message, image)
        VALUES (
        %(time)s,
        (SELECT u.id FROM users u WHERE u.username = %(username)s),
        %(vote_n)s, 
        %(question_id)s, 
        %(message)s, 
        %(image)s
        )
        '''
    cursor.execute(query, {'time': util.get_current_time(), 'vote_n': 0,
                           'question_id': question_id, 'message': message, 'image': None, 'username': username})


@connection.connection_handler
def save_comment(cursor: RealDictCursor, question_id, answer_id, message, username):
    query = '''
        INSERT INTO comment(submission_time, user_id, question_id,answer_id, message)
        VALUES (
        %(time)s,
        (SELECT u.id FROM users u WHERE u.username = %(username)s), 
        %(question_id)s,  
        %(answer_id)s,
        %(message)s
        )
        '''
    cursor.execute(query, {'time': util.get_current_time(),
                           'question_id': question_id, 'message': message, 'answer_id': answer_id,
                           'username': username})


@connection.connection_handler
def delete_answer(cursor: RealDictCursor, id_to_delete):
    query = '''
        DELETE FROM answer WHERE id = %(id_to_delete)s
        '''
    value = {'id_to_delete': id_to_delete}
    cursor.execute(query, value)


@connection.connection_handler
def register_user(cursor: RealDictCursor, user_details: dict):
    query = '''
        INSERT INTO users(username, password, email, registration_date, admin, reputation)
        VALUES (%(username)s, %(password)s, %(email)s, %(registration_date)s, false, 0)
        '''
    cursor.execute(query, user_details)


@connection.connection_handler
def check_if_user_exists(cursor: RealDictCursor, username, email):
    query = '''
        SELECT username, email 
        FROM users 
        WHERE EXISTS (SELECT username, email FROM users WHERE username = %(username)s OR email = %(email)s)
        '''
    cursor.execute(query, {'username': username, 'email': email})
    return cursor.fetchone()


@connection.connection_handler
def get_users_details(cursor):
    query = """
        SELECT id, username, password, email, admin, registration_date, reputation
        FROM users
        ORDER BY username"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def get_user_by_id(cursor, user_id):
    query = """
        SELECT id, username, password, email, admin, registration_date, reputation
        FROM users
        WHERE id = %(id)s
        ORDER BY username"""
    cursor.execute(query, {'id': user_id})
    return cursor.fetchall()


@connection.connection_handler
def user_rights_to_question(cursor, user_id, question_id):
    query = """
        SELECT true FROM question q WHERE q.id = %(question_id)s AND q.user_id = %(user_id)s
        """
    cursor.execute(query, {'user_id': user_id, 'question_id': question_id})
    return cursor.fetchone()


@connection.connection_handler
def user_rights_to_answer(cursor, user_id, answer_id):
    query = """
        SELECT true FROM answer a WHERE a.id = %(answer_id)s AND a.user_id = %(user_id)s
        """
    cursor.execute(query, {'user_id': user_id, 'answer_id': answer_id})
    return cursor.fetchone()


@connection.connection_handler
def mark_answer_as_accepted(cursor, question_id, answer_id):
    query = """
        UPDATE question
        SET accepted_answer_id = %(answer_id)s
        WHERE id = %(question_id)s
        """
    cursor.execute(query, {'question_id': question_id, 'answer_id': answer_id})


@connection.connection_handler
def unmark_accepted_answer(cursor, question_id):
    query = """
        UPDATE question
        SET accepted_answer_id = null
        WHERE id = %(question_id)s
        """
    cursor.execute(query, {'question_id': question_id})


@connection.connection_handler
def users_questions(cursor: RealDictCursor, user_id):
    query = """
        SELECT * FROM question q WHERE q.user_id = %(user_id)s;
        """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@connection.connection_handler
def users_ans(cursor: RealDictCursor, user_id):
    query = """
        SELECT * FROM answer a WHERE a.user_id = %(user_id)s;
        """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@connection.connection_handler
def users_comments(cursor: RealDictCursor, user_id):
    query = """
        SELECT * FROM comment c WHERE c.user_id = %(user_id)s;
        """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchall()


@connection.connection_handler
def thumb_up(cursor: RealDictCursor, table, question_id):
    query = f"""
        UPDATE {table}
        SET vote_number = vote_number +1
        WHERE id = {question_id}
        """
    cursor.execute(query)


@connection.connection_handler
def thumb_down(cursor: RealDictCursor, table, question_id):
    query = f"""
        UPDATE {table}
        SET vote_number = vote_number -1
        WHERE id =  {question_id}
        """
    cursor.execute(query)


@connection.connection_handler
def change_reputation(cursor: RealDictCursor, table, id, value):
    query = """
        UPDATE users
        SET reputation = reputation + %(value)s
        FROM answer
        WHERE users.id = (SELECT answer.user_id FROM answer WHERE answer.id = %(id)s)
        """
    cursor.execute(query, {'table': table, 'id': id, 'value': value})

