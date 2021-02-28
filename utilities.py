import json
import random

import telegram
from fuzzywuzzy import fuzz
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from texts import TEXTS_BUTTONS
from texts import TEXTS


def get_start_keyboard(messenger_type):
    reply_markup = None
    button_new_question = TEXTS_BUTTONS['keyboard']['new_question']
    button_end_quiz = TEXTS_BUTTONS['keyboard']['end_quiz']
    button_my_score = TEXTS_BUTTONS['keyboard']['my_score']

    if messenger_type == 'telegram':
        custom_keyboard = [[button_new_question, button_end_quiz],
                           [button_my_score]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    elif messenger_type == 'vk':
        keyboard = VkKeyboard()
        keyboard.add_button(button_new_question, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(button_end_quiz, color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(button_my_score, color=VkKeyboardColor.SECONDARY)
        reply_markup = keyboard.get_keyboard()
    return reply_markup


def new_question(chat_id, r_db, quiz_questions):
    questions = list(quiz_questions.keys())
    random_question_number = random.choice(questions)
    random_question = quiz_questions[random_question_number]['question']
    user_data = json.dumps({
        'current_question_id': random_question_number,
        'is_answer_correct': False
    })
    r_db.set(chat_id, user_data)
    return random_question


def end_quiz(chat_id, r_db, quiz_questions):
    current_question_id = json.loads(r_db.get(chat_id))
    if current_question_id and current_question_id['is_answer_correct'] is False:
        current_question = quiz_questions[current_question_id['current_question_id']]['question']
        current_question_true_answer = quiz_questions[current_question_id['current_question_id']]['answer']
        text = f'Текущий вопрос: {current_question}\n\nОтвет: {current_question_true_answer}'
        r_db.delete(chat_id)
        return {'status': True, 'data': text}
    elif current_question_id['current_question_id'] and current_question_id['is_answer_correct']:
        text = TEXTS['next_question']
        return {'status': False, 'data': text}
    else:
        text = TEXTS['quiz_not_started']
        return {'status': False, 'data': text}


def get_user_score(chat_id, r_db):
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        text = TEXTS['rating_exists']
        return {'status': True, 'data': text}
    else:
        text = TEXTS['quiz_not_started']
        return {'status': False, 'data': text}


def get_user_last_question(chat_id, r_db, quiz_questions):
    current_question_id = json.loads(r_db.get(chat_id))
    if current_question_id:
        question_id_number = current_question_id.lower().replace("вопрос ", "")
        current_question = quiz_questions[current_question_id]['question']
        text = f'Ваш последний вопрос без ответа: {question_id_number}. Вопрос был такой: {current_question}'
        return {'status': True, 'data': text, 'question_id': question_id_number, 'current_question': current_question}
    else:
        return {'status': False, 'data': None}


def waiting_for_question_answer(chat_id, user_message, r_db, quiz_questions):
    current_question_id = json.loads(r_db.get(chat_id))
    if current_question_id['current_question_id']:
        true_answer = quiz_questions[current_question_id['current_question_id']]['answer'].lower()
        user_text = user_message.lower()
        case_is_true = _is_answer_correct(user_text, true_answer)
        if case_is_true:
            answer_to_user = f"{TEXTS['true_answer']} {TEXTS['next_question']}"
            user_data = json.dumps({
                'current_question_id': current_question_id['current_question_id'],
                'is_answer_correct': True
            })
            r_db.set(chat_id, user_data)
        else:
            answer_to_user = f"{TEXTS['false_answer']} {TEXTS['try_again']}"
        return {'status': True, 'true_answer': case_is_true, 'data': answer_to_user, 'answer': true_answer}
    else:
        text = TEXTS['quiz_not_started']
        return {'status': False, 'data': text}


def _is_answer_correct(user_text, true_answer):
    correct_ratio = fuzz.token_sort_ratio(true_answer, user_text)
    return True if correct_ratio >= 75 else False
