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
def get_answers(cursor: RealDictCursor, searched_id):
    query = f"""
        SELECT u.username, a.submission_time, a.vote_number, a.message, a.id
        FROM answer as a
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
        DELETE FROM question WHERE id = %(id_to_delete)s
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
def get_user_by_id(cursor, id):
    query = """
        SELECT id, username, password, email, admin, registration_date, reputation
        FROM users
        WHERE id = %(id)s
        ORDER BY username"""
    value = {'id': id}
    cursor.execute(query, value)
    return cursor.fetchall()
