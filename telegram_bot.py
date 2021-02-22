import logging
import os

import redis
from dotenv import load_dotenv
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

import questions
import utilities
from MyLogger import TelegramLogsHandler, create_my_logger
from texts import TEXTS_BUTTONS as TEXTS_BUTTONS
from texts import TEXTS as TEXTS


telegram_logger = create_my_logger(name=__name__, level=logging.INFO)


def main():
    bot = Updater(token=telegram_token, use_context=True)
    telegram_logger.addHandler(TelegramLogsHandler(tg_bot=bot.bot, chat_id=telegram_chat_id))

    dispatcher = bot.dispatcher

    start_handler = CommandHandler('start', start)
    new_question_handler = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['new_question']), new_question)
    end_quiz_handler = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['end_quiz']), end_quiz)
    my_score_handler = MessageHandler(Filters.regex(TEXTS_BUTTONS['keyboard']['my_score']), get_my_score)
    waiting_for_answer_handler = MessageHandler(Filters.text, waiting_for_question_answer)
    waiting_for_new_question_handler = MessageHandler(Filters.text, waiting_for_new_question)

    conversation_handler = ConversationHandler(entry_points=[new_question_handler],
                                               states={
                                                   'waiting_for_answer': [waiting_for_answer_handler],
                                                   'waiting_for_new_question': [waiting_for_new_question_handler]
                                               },
                                               fallbacks=[])
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(end_quiz_handler)
    dispatcher.add_handler(my_score_handler)
    dispatcher.add_handler(conversation_handler)

    bot.start_polling()
    bot.idle()


def start(update, context):
    chat_id = update.effective_chat.id
    send_start_keyboard(update, context)
    telegram_logger.debug(f'/start command activated by {chat_id}')


def send_start_keyboard(update, context):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id,
                             text=TEXTS['start_session'],
                             reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))


def new_question(update, context):
    chat_id = update.effective_chat.id
    random_question = utilities.new_question(chat_id=chat_id, r_db=r_db, quiz_questions=quiz_questions)
    context.bot.send_message(chat_id=chat_id, text=random_question)
    telegram_logger.debug(f'new_question for {chat_id}: question - {random_question} ')
    return 'waiting_for_answer'


def end_quiz(update, context):
    chat_id = update.effective_chat.id
    text = utilities.end_quiz(chat_id, r_db, quiz_questions)
    # TODO: так как поле затирается и сразу создается новое - если пользователь правильно ответит на вопрос и
    #  нажмет на сдаться - у него появится сообщение как будто он сдался. При доработке бота сделать джейсонку умнее*
    if text['status']:
        context.bot.send_message(chat_id=chat_id, text=text['data'])
        telegram_logger.debug(f'end_quiz for {chat_id}')
        telegram_logger.debug(f'delete chat_id_key in redis for {chat_id}')
        return new_question(update, context)
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'end_quiz for {chat_id} failed: no chat_id in redis')


def get_my_score(update, context):
    chat_id = update.effective_chat.id
    text = utilities.get_my_score(chat_id, r_db)
    if text['status']:
        context.bot.send_message(chat_id=chat_id, text=text['data'])
        telegram_logger.debug(f'end_quiz for {chat_id} failed: no chat_id in redis')
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'get_my_score for {chat_id} failed: no chat_id in redis')


def waiting_for_question_answer(update, context):
    chat_id = update.effective_chat.id
    user_message = update.message.text
    text = utilities.waiting_for_question_answer(chat_id, user_message, r_db, quiz_questions)
    if text['status']:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'waiting_for_question_answer for {chat_id}: answer is {text["true_answer"]}')
        return 'waiting_for_new_question' if text['true_answer'] else 'waiting_for_answer'
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text=text['data'],
                                 reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
        telegram_logger.debug(f'get_my_score for {chat_id} failed: no chat_id in redis')


def waiting_for_new_question(update, context):
    chat_id = update.effective_chat.id
    text = utilities.waiting_for_new_question()
    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_markup=utilities.get_start_keyboard(messenger_type='telegram'))
    telegram_logger.debug(f'waiting_for_new_question for {chat_id} ')
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

    main()

