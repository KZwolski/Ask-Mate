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
        SELECT *
        FROM question
        WHERE id = {searched_id}"""
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
        SELECT *
        FROM answer
        WHERE question_id = {searched_id}"""
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def save_question(cursor: RealDictCursor, new_id, question_title, message, image):
    query = '''
        INSERT INTO question(id, submission_time, view_number, vote_number, title, message, image)
        VALUES (%(id)s,%(time)s, %(view_n)s, %(vote_n)s, %(title)s, %(message)s, %(image)s)
        '''
    cursor.execute(query, {'id': new_id, 'time': util.get_current_time(), 'view_n': 0, 'vote_n': 0,
                           'title': question_title, 'message': message, 'image': image})


@connection.connection_handler
def max_id(cursor: RealDictCursor):
    cursor.execute("""
                       SELECT id FROM question
                       ORDER BY id DESC 
                       LIMIT 1
       """)
    maximum_id = cursor.fetchone()
    return maximum_id.get('id')


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
def save_answer(cursor: RealDictCursor, question_id, message):
    query = '''
        INSERT INTO answer(submission_time, vote_number, question_id, message, image)
        VALUES (%(time)s,  %(vote_n)s, %(question_id)s, %(message)s, %(image)s)
        '''
    cursor.execute(query, {'time': util.get_current_time(), 'vote_n': 0,
                           'question_id': question_id, 'message': message, 'image': None})


@connection.connection_handler
def delete_answer(cursor: RealDictCursor, id_to_delete):
    query = '''
        DELETE FROM answer WHERE id = %(id_to_delete)s
        '''
    value = {'id_to_delete': id_to_delete}
    cursor.execute(query, value)


@connection.connection_handler  # IN PROGRESS ~~SEBA
def register_user(cursor: RealDictCursor, user_details: dict):
    query = '''
        INSERT INTO users(username, password, email, registration_date, admin, reputation)
        VALUES (%(username)s, %(password)s, %(email)s, %(registration_date)s, false, 0)
        '''
    cursor.execute(query, user_details)


@connection.connection_handler  # IN PROGRESS ~~SEBA
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
        SELECT username, password, email, admin, registration_date, reputation
        FROM users
        ORDER BY username"""
    cursor.execute(query)
    return cursor.fetchall()
