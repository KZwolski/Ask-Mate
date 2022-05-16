import connection
from datetime import datetime, timezone
import bcrypt


question_path = "data/question.csv"
answer_path = "data/answer.csv"


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


def sort_answers_by_timestamp():
    data = connection.reader_csv(answer_path)
    sorted_data = sorted(data, key=lambda k: k["submission_time"], reverse=True)
    return sorted_data


def sort_questions_by_timestamp():
    data = connection.reader_csv(question_path)
    sorted_data = sorted(data, key=lambda k: k["submission_time"], reverse=True)
    return sorted_data


def get_current_time():
    current_time = int(datetime.now().replace(tzinfo=timezone.utc).timestamp())
    value = datetime.utcfromtimestamp(current_time)
    date_format = f"{value:%Y-%m-%d %H:%M:%S}"
    return date_format
