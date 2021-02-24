import logging
import os
import random

import redis
import questions
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

import utilities
from texts import TEXTS_BUTTONS
from MyLogger import create_custom_logger


vk_logger = create_custom_logger(name=__name__, level=logging.INFO)


def echo_answer(event, vk_api):
    random_id = random.randint(1, 1000)
    try:
        answer = event.text
        if answer:
            vk_api.messages.send(
                user_id=event.user_id,
                message=answer,
                random_id=random_id
            )
            vk_logger.debug(f'send to: {event.user_id} msg: {event.text}')
        else:
            vk_logger.debug(f'no intent detected')
    except Exception as e:
        vk_logger.error(f"error: {e}")


def vk_send_msg(event, vk_api, msg):
    random_id = random.randint(1, 1000)
    vk_api.messages.send(
        user_id=event.user_id,
        message=msg,
        random_id=random_id
    )
    vk_logger.debug(f'send to: {event.user_id} msg: {event.text}')


def vk_send_keyboard(event, vk_api, answer):
    random_id = random.randint(1, 1000)
    vk_api.messages.send(
        user_id=event.user_id,
        message=answer,
        random_id=random_id,
        keyboard=utilities.get_start_keyboard(messenger_type='vk')
    )
    vk_logger.debug(f'send to: {event.user_id} msg: {event.text}')


def new_question(event, vk_api):
    user_id = event.user_id
    random_question = utilities.new_question(chat_id=user_id, r_db=r_db, quiz_questions=quiz_questions)
    vk_send_keyboard(event, vk_api, random_question)
    vk_logger.debug(f'new_question for {user_id}: question - {random_question} ')
    return 'waiting_for_answer'


def end_quiz(event, vk_api):
    user_id = event.user_id
    text = utilities.end_quiz(user_id, r_db, quiz_questions)
    # TODO: так как поле затирается и сразу создается новое - если пользователь правильно ответит на вопрос и
    #  нажмет на сдаться - у него появится сообщение как будто он сдался. При доработке бота сделать джейсонку умнее*
    if text['status']:
        vk_send_msg(event, vk_api, text['data'])
        vk_logger.debug(f'end_quiz for {user_id}')
        vk_logger.debug(f'delete chat_id_key in redis for {user_id}')
        return new_question(event, vk_api)
    else:
        vk_send_keyboard(event, vk_api, text['data'])
        vk_logger.debug(f'end_quiz for {user_id} failed: no chat_id in redis')


def get_my_score(event, vk_api):
    user_id = event.user_id
    text = utilities.get_my_score(user_id, r_db)
    if text['status']:
        vk_send_msg(event, vk_api, text['data'])
        vk_logger.debug(f'end_quiz for {user_id} failed: no chat_id in redis')
    else:
        vk_send_keyboard(event, vk_api, text['data'])
        vk_logger.debug(f'get_my_score for {user_id} failed: no chat_id in redis')


def waiting_for_question_answer(event, vk_api):
    user_id = event.user_id
    user_message = event.text
    text = utilities.waiting_for_question_answer(user_id, user_message, r_db, quiz_questions)
    if text['status']:
        vk_send_msg(event, vk_api, text['data'])
        vk_logger.debug(f'waiting_for_question_answer for {user_id}: answer is {text["true_answer"]}')
        return 'waiting_for_new_question' if text['true_answer'] else 'waiting_for_answer'
    else:
        vk_send_msg(event, vk_api, text['data'])
        vk_logger.debug(f'get_my_score for {user_id} failed: no chat_id in redis')


def waiting_for_new_question(event, vk_api):
    user_id = event.user_id
    text = utilities.waiting_for_new_question()
    vk_send_msg(event, vk_api, text['data'])
    vk_logger.debug(f'waiting_for_new_question for {user_id} ')
    return 'end'


def conversation_handler(event, vk_api):
    text_from_user = event.text

    button_new_question = TEXTS_BUTTONS['keyboard']['new_question']
    button_end_quiz = TEXTS_BUTTONS['keyboard']['end_quiz']
    button_my_score = TEXTS_BUTTONS['keyboard']['my_score']

    if text_from_user == button_new_question:
        new_question(event, vk_api)
    elif text_from_user == button_end_quiz:
        end_quiz(event, vk_api)
    elif text_from_user == button_my_score:
        get_my_score(event, vk_api)
    else:
        waiting_for_question_answer(event, vk_api)


if __name__ == '__main__':
    vk_logger.info('Start VK Bot')

    load_dotenv()

    redis_host = os.getenv('REDIS_ENDPOINT')
    redis_port = os.getenv('REDIS_PORT')
    redis_password = os.getenv('REDIS_PASSWORD')
    r_db = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_password, decode_responses=True)\

    quiz_questions = questions.get_questions()

    vkontakte_group_token = os.getenv("VKONTAKTE_GROUP_TOKEN")

    vk_session = vk.VkApi(token=vkontakte_group_token)
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            vk_logger.debug('Новое сообщение:')
            if event.to_me:
                vk_logger.debug(f'Для меня от: {event.user_id}')
                conversation_handler(event, vk_api)
            else:
                vk_logger.debug(f'От меня для: {event.user_id}')
            vk_logger.debug(f'Текст: {event.text}')

