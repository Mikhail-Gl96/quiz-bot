import os
import logging
import random

import redis
import telegram
from dotenv import load_dotenv
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler
from telegram.ext import MessageHandler, Filters

from MyLogger import TelegramLogsHandler, create_my_logger
import questions
from texts import TEXTS_BUTTONS as TEXTS_BUTTONS
from texts import TEXTS as TEXTS
import utilities


telegram_logger = create_my_logger(name=__name__, level=logging.INFO)


def main():
    bot = Updater(token=telegram_token, use_context=True)
    telegram_logger.addHandler(TelegramLogsHandler(tg_bot=bot.bot, chat_id=telegram_chat_id))

    dispatcher = bot.dispatcher

    start_handler = CommandHandler('start', start)
    new_question_handler = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['new_question']), new_question)
    end_quiz_handler = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['end_quiz']), end_quiz)
    my_score_handler = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['my_score']), get_my_score)
    user_last_question_handler = MessageHandler(Filters.text, get_user_last_question)
    waiting_for_answer_handler = MessageHandler(Filters.text, waiting_for_question_answer)
    waiting_for_new_question_handler = MessageHandler(Filters.text, waiting_for_new_question)

    conversation_handler = ConversationHandler(entry_points=[start_handler, new_question_handler],
                                               states={
                                                   'user_id': [user_last_question_handler],
                                                   'waiting_for_answer': [waiting_for_answer_handler],
                                                   'waiting_for_new_question': [waiting_for_new_question_handler]
                                               },
                                               fallbacks=[])

    dispatcher.add_handler(end_quiz_handler)
    dispatcher.add_handler(my_score_handler)
    dispatcher.add_handler(conversation_handler)

    bot.start_polling()
    bot.idle()


def start(update, context):
    chat_id = update.effective_chat.id
    send_start_keyboard(update, context)
    telegram_logger.debug(f'/start command activated by {chat_id}')
    return 'chat_id'


def send_start_keyboard(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id,
                             text=TEXTS['start_session'],
                             reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))


def new_question(update, context):

    chat_id = update.effective_chat.id
    random_question = utilities.new_question(chat_id=chat_id, r_db=r_db, quiz_questions=quiz_questions)
    # all_questions = list(quiz_questions.keys())
    # random_question_number = random.choice(all_questions)
    # random_question = quiz_questions[random_question_number]['question']
    # r_db.set(chat_id, random_question_number)
    context.bot.send_message(chat_id=chat_id, text=random_question)
    telegram_logger.debug(f'new_question for {chat_id}: question - {random_question} ')
    return 'waiting_for_answer'


def end_quiz(update, context):
    chat_id = update.effective_chat.id
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        current_question = quiz_questions[current_question_id]['question']
        current_question_true_answer = quiz_questions[current_question_id]['answer']
        text = f'Текущий вопрос: {current_question}\n\nОтвет: {current_question_true_answer}'
        context.bot.send_message(chat_id=chat_id, text=text)
        telegram_logger.debug(f'end_quiz for {chat_id}')
        r_db.delete(chat_id)
        telegram_logger.debug(f'delete chat_id_key in redis for {chat_id}')
        return new_question(update, context)
    else:
        text = f'Вы еще не начали викторину'
        context.bot.send_message(chat_id=chat_id,
                                 text=text,
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'end_quiz for {chat_id} failed: no chat_id in redis')


def get_my_score(update, context):
    chat_id = update.effective_chat.id
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        text = f'Вы в викторине, рейтинг сделаем позже'
        context.bot.send_message(chat_id=chat_id, text=text)
        telegram_logger.debug(f'end_quiz for {chat_id} failed: no chat_id in redis')
    else:
        text = f'Вы еще не начали викторину'
        context.bot.send_message(chat_id=chat_id,
                                 text=text,
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'get_my_score for {chat_id} failed: no chat_id in redis')


def get_user_last_question(update, context):
    chat_id = update.effective_chat.id
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        question_id_number = current_question_id.lower().replace("вопрос ", "")
        current_question = quiz_questions[current_question_id]['question']
        text = f'Ваш последний вопрос без ответа: {question_id_number}. Вопрос был такой: {current_question}'
        context.bot.send_message(chat_id=chat_id, text=text)
        telegram_logger.debug(f'reply question for {chat_id}: question[{current_question_id}] - {current_question} ')
        return 'waiting_for_answer'
    else:
        telegram_logger.debug(f'no question_id for {chat_id}')
        return 'start'


def waiting_for_question_answer(update, context):
    print('waiting_for_question_answer')
    chat_id = update.effective_chat.id
    current_question_id = r_db.get(chat_id)
    if current_question_id:
        true_answer = quiz_questions[current_question_id]['answer'].lower()
        user_text = update.message.text.lower()
        case_is_true = true_answer == user_text or true_answer.find(user_text) != -1
        if case_is_true:
            answer_to_user = f"{TEXTS['true_answer']} {TEXTS['next_question']}"
        else:
            answer_to_user = f"{TEXTS['false_answer']} {TEXTS['try_again']}"
        context.bot.send_message(chat_id=chat_id,
                                 text=answer_to_user,
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'waiting_for_question_answer for {chat_id}: answer is correct')
        return 'waiting_for_new_question' if case_is_true else 'waiting_for_answer'
    else:
        text = f'Вы еще не начали викторину'
        context.bot.send_message(chat_id=chat_id,
                                 text=text,
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'get_my_score for {chat_id} failed: no chat_id in redis')


def waiting_for_new_question(update, context):
    chat_id = update.effective_chat.id
    text = f'{TEXTS["next_question"]}'
    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
    telegram_logger.debug(f'waiting_for_new_question for {chat_id} ')
    return ConversationHandler.END

# def send_new_question(update, context):
#     new_question(update, context)

# def answer(update, context):
#     which_button_was_pressed(update, context)
    # if answer:
    #     # context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
    #     send_start_keyboard(update, context)


# def which_button_was_pressed(update, context):
#     buttons = TEXTS_BUTTONS['keyboard'].values()
#     chat_id = update.effective_chat.id
#     if update.message.text in buttons:
#         if update.message.text == TEXTS_BUTTONS['keyboard']['new_question']:
#             all_questions = list(quiz_questions.keys())
#             random_question_number = random.choice(all_questions)
#             random_question = quiz_questions[random_question_number]['question']
#             r_db.set(chat_id, random_question_number)
#             true_answer = quiz_questions[random_question_number]['answer']
#             print(true_answer)
#             context.bot.send_message(chat_id=chat_id, text=random_question)
#     else:
#         print(r_db.get(chat_id))
#         if r_db.get(chat_id) is not 'null':
#             current_question = r_db.get(chat_id)
#             true_answer = quiz_questions[current_question]['answer'].lower()
#             user_text = update.message.text.lower()
#             if true_answer == user_text or true_answer.find(user_text) != -1:
#                 answer_to_user = f"{TEXTS['true_answer']} {TEXTS['next_question']}"
#             else:
#                 answer_to_user = f"{TEXTS['false_answer']} {TEXTS['try_again']}"
#             context.bot.send_message(chat_id=chat_id, text=answer_to_user)
#         else:
#             send_start_keyboard(update, context)


if __name__ == '__main__':
    telegram_logger.info(f'Start telegram bot')

    load_dotenv()

    redis_host = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')
    r_db = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_password, decode_responses=True)

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    quiz_questions = questions.get_questions()

    main()

