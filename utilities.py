import random

import telegram
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from texts import TEXTS_BUTTONS as TEXTS_BUTTONS
from texts import TEXTS as TEXTS


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
        keyboard.add_line()  # Переход на вторую строку
        keyboard.add_button(button_my_score, color=VkKeyboardColor.SECONDARY)
        reply_markup = keyboard.get_keyboard()
    return reply_markup


def new_question(chat_id, r_db, quiz_questions):
    all_questions = list(quiz_questions.keys())
    random_question_number = random.choice(all_questions)
    random_question = quiz_questions[random_question_number]['question']
    r_db.set(chat_id, random_question_number)

    true_answer = quiz_questions[random_question_number]['answer']
    print(true_answer)

    return random_question


def end_quiz(chat_id, r_db, quiz_questions):
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        current_question = quiz_questions[current_question_id]['question']
        current_question_true_answer = quiz_questions[current_question_id]['answer']
        text = f'Текущий вопрос: {current_question}\n\nОтвет: {current_question_true_answer}'
        r_db.delete(chat_id)
        return {'status': True, 'data': text}
    else:
        text = f'Вы еще не начали викторину'
        return {'status': False, 'data': text}


def get_my_score(chat_id, r_db):
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        text = f'Вы в викторине, рейтинг сделаем позже'
        return {'status': True, 'data': text}
    else:
        text = f'Вы еще не начали викторину'
        return {'status': False, 'data': text}


def get_user_last_question(chat_id, r_db, quiz_questions):
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        question_id_number = current_question_id.lower().replace("вопрос ", "")
        current_question = quiz_questions[current_question_id]['question']
        text = f'Ваш последний вопрос без ответа: {question_id_number}. Вопрос был такой: {current_question}'
        return {'status': True, 'data': text, 'question_id': question_id_number, 'current_question': current_question}
    else:
        return {'status': False, 'data': None}


def waiting_for_question_answer(chat_id, user_message, r_db, quiz_questions):
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        true_answer = quiz_questions[current_question_id]['answer'].lower()
        user_text = user_message.lower()
        case_is_true = true_answer == user_text or true_answer.find(user_text) != -1
        if case_is_true:
            answer_to_user = f"{TEXTS['true_answer']} {TEXTS['next_question']}"
        else:
            answer_to_user = f"{TEXTS['false_answer']} {TEXTS['try_again']}"
        return {'status': True, 'true_answer': case_is_true, 'data': answer_to_user, 'answer': true_answer}
    else:
        text = f'Вы еще не начали викторину'
        return {'status': False, 'data': text}


def waiting_for_new_question():
    text = f'{TEXTS["next_question"]}'
    return text


