
import os


def get_questions():
    file_dir = 'questions'
    files = os.listdir(file_dir)
    random_file = os.path.join(file_dir, files[0])
    quiz_questions = {}

    with open(random_file, 'r', encoding='KOI8-R') as file:
        question_now = False
        answer_now = False
        for string in file:
            string = string.replace('\n', '')
            if string == '':
                if answer_now and answer_now:
                    question_now = False
                    answer_now = False
            if string.startswith('Вопрос '):
                answer_now = False
                question_now = string.replace(':', '')
                quiz_questions.update({
                    question_now: {'question': None,
                                   'answer': None}
                })
                continue
            elif string.startswith('Ответ:'):
                answer_now = True
                continue
            if answer_now:
                quiz_questions[question_now].update({
                    'answer': quiz_questions[question_now].get('answer') + ' ' + string
                    if quiz_questions[question_now].get('answer') else string
                })
            elif question_now:
                quiz_questions[question_now].update({
                    'question': quiz_questions[question_now].get('question') + ' ' + string
                    if quiz_questions[question_now].get('question') else string
                })
    return quiz_questions.copy()

