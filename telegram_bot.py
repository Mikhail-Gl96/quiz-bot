import logging
import os

import redis
from dotenv import load_dotenv
from telegram.ext import CommandHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

import questions
import utilities
from MyLogger import TelegramLogsHandler, create_custom_logger
from texts import TEXTS_BUTTONS
from texts import TEXTS


telegram_logger = create_custom_logger(name=__name__, level=logging.INFO)


def start(update, context):
    chat_id = update.effective_chat.id
    send_start_keyboard(update, context)
    telegram_logger.debug(f'/start command activated by {chat_id}')


def send_start_keyboard(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id,
                             text=TEXTS['start_session'],
                             reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))


def new_question_handler(update, context):
    chat_id = update.effective_chat.id
    random_question = utilities.new_question(chat_id=chat_id, r_db=r_db, quiz_questions=quiz_questions)
    context.bot.send_message(chat_id=chat_id, text=random_question)
    telegram_logger.debug(f'new_question_handler for {chat_id}: question - {random_question} ')
    return 'waiting_for_answer'


def end_quiz_handler(update, context):
    chat_id = update.effective_chat.id
    text = utilities.end_quiz(chat_id, r_db, quiz_questions)
    if text['status']:
        context.bot.send_message(chat_id=chat_id, text=text['data'])
        telegram_logger.debug(f'end_quiz_handler for {chat_id}')
        telegram_logger.debug(f'delete chat_id_key in redis for {chat_id}')
        return new_question_handler(update, context)
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'end_quiz_handler for {chat_id}: {text["data"]}')
        return ConversationHandler.END


def user_score_handler(update, context):
    chat_id = update.effective_chat.id
    text = utilities.get_user_score(chat_id, r_db)
    if text['status']:
        context.bot.send_message(chat_id=chat_id, text=text['data'])
        telegram_logger.debug(f'user_score_handler for {chat_id} failed: no chat_id in redis')
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'user_score_handler for {chat_id} failed: no chat_id in redis')


def question_answer_handler(update, context):
    chat_id = update.effective_chat.id
    user_message = update.message.text
    text = utilities.waiting_for_question_answer(chat_id, user_message, r_db, quiz_questions)
    if text['status']:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'question_answer_handler for {chat_id}: answer is {text["true_answer"]}')
        return 'waiting_for_new_question' if text['true_answer'] else 'waiting_for_answer'
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'question_answer_handler for {chat_id} failed: no chat_id in redis')
        return ConversationHandler.END


def waiting_for_new_question_handler(update, context):
    chat_id = update.effective_chat.id
    user_message = update.message.text
    if user_message == TEXTS_BUTTONS['keyboard']['new_question']:
        return new_question_handler(update, context)
    else:
        text = TEXTS["next_question"]
        context.bot.send_message(chat_id=chat_id,
                                 text=text,
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'waiting_for_new_question_handler for {chat_id} ')
    return ConversationHandler.END


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

    bot = Updater(token=telegram_token, use_context=True)
    telegram_logger.addHandler(TelegramLogsHandler(tg_bot=bot.bot, chat_id=telegram_chat_id))

    dispatcher = bot.dispatcher

    start_handler = CommandHandler('start', start)
    new_question = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['new_question']), new_question_handler)
    end_quiz = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['end_quiz']), end_quiz_handler)
    user_score = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['my_score']), user_score_handler)
    question_answer = MessageHandler(Filters.text, question_answer_handler)
    waiting_for_new_question = MessageHandler(Filters.text, waiting_for_new_question_handler)

    conversation_handler = ConversationHandler(entry_points=[new_question],
                                               states={
                                                   'waiting_for_answer': [question_answer],
                                                   'waiting_for_new_question': [waiting_for_new_question]
                                               },
                                               fallbacks=[])
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(end_quiz)
    dispatcher.add_handler(user_score)
    dispatcher.add_handler(conversation_handler)

    bot.start_polling()
    bot.idle()

