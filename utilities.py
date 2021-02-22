import random

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler
from telegram.ext import MessageHandler, Filters
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


