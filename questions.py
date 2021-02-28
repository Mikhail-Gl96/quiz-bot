
import os


def get_questions():
    file_dir = 'questions'
    files = os.listdir(file_dir)
    random_file = os.path.join(file_dir, files[0])
    quiz_questions = {}

    with open(random_file, 'r', encoding='KOI8-R') as file:
        question_now = None
        temp_text = ''
        for string in file:
            temp_text += string
            if temp_text.endswith('\n\n') and question_now and quiz_questions.get(question_now):
                quiz_questions[question_now].update({'answer': temp_text.replace('\n', '')})
                temp_text = ''
                question_now = None
            if string.startswith('Вопрос '):
                question_now = string.replace('\n', '').replace(':', '')
                temp_text = ''
            if string.startswith('Ответ:'):
                quiz_questions.update({
                    question_now: {
                        'question': temp_text.replace(string, '').replace('\n', '')}
                })
                temp_text = ''
    return quiz_questions.copy()

