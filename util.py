import connection
from datetime import datetime, timezone
import time


question_path = "data/question.csv"
answer_path = "data/answer.csv"


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


def generate_new_id(filename):
    with open(filename, 'r') as file:
        last_id = int(file.read())
    with open(filename, 'w') as file:
        file.write(str(last_id + 1))
    return last_id + 1
