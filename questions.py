
import os


def get_questions():
    file_dir = 'questions'
    files = os.listdir(file_dir)
    random_file = os.path.join(file_dir, files[0])
    quiz_questions = {}

    with open(random_file, 'r', encoding='KOI8-R') as file:
        question_now = False
        answer_now = False
        comment_now = False
        source_now = False
        author_now = False
        buffer_end = False
        for string in file:
            string = string.replace('\n', '')
            if string == '':
                if answer_now and answer_now and comment_now and source_now and author_now and buffer_end:
                    question_now = False
                    answer_now = False
                    comment_now = False
                    source_now = False
                    author_now = False
                else:
                    if answer_now and answer_now and comment_now and source_now and author_now:
                        buffer_end = True

            if string.startswith('Вопрос '):
                answer_now = False
                comment_now = False
                source_now = False
                author_now = False
                question_now = string.replace(':', '')
                quiz_questions.update({
                    question_now: {'question': None,
                                   'answer': None,
                                   'comment': None,
                                   'source': None,
                                   'author': None}
                })
                continue
            elif string.startswith('Ответ:'):
                answer_now = True
                continue
            elif string.startswith('Комментарий:'):
                comment_now = True
                continue
            elif string.startswith('Источник:'):
                source_now = True
                continue
            elif string.startswith('Автор:'):
                author_now = True
                continue

            if author_now:
                quiz_questions[question_now].update({
                    'author': quiz_questions[question_now].get('author') + ' ' + string
                    if quiz_questions[question_now].get('author') else string
                })
            elif source_now:
                quiz_questions[question_now].update({
                    'source': quiz_questions[question_now].get('source') + ' ' + string
                    if quiz_questions[question_now].get('source') else string
                })
            elif comment_now:
                quiz_questions[question_now].update({
                    'comment': quiz_questions[question_now].get('comment') + ' ' + string
                    if quiz_questions[question_now].get('comment') else string
                })
            elif answer_now:
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


# def pretty(d, indent=0):
#    for key, value in d.items():
#       print('\t' * indent + str(key))
#       if isinstance(value, dict):
#          pretty(value, indent+1)
#       else:
#          print('\t' * (indent+1) + str(value))
#
# print(pretty(get_questions(), 4))

