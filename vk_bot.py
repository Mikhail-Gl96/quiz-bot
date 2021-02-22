import random
import os
import logging

from dotenv import load_dotenv
import redis
import questions
import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from MyLogger import create_my_logger
import utilities


vk_logger = create_my_logger(name=__name__, level=logging.INFO)


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


def vk_send_keyboard(event, vk_api, answer):
    random_id = random.randint(1, 1000)
    try:
        vk_api.messages.send(
            user_id=event.user_id,
            message=answer,
            random_id=random_id,
            keyboard=utilities.get_start_keyboard(messenger_type='vk')
        )
        vk_logger.debug(f'send to: {event.user_id} msg: {event.text}')
    except Exception as e:
        vk_logger.error(f"error: {e}")


def new_question(event, vk_api):
    user_id = event.user_id
    random_question = utilities.new_question(chat_id=user_id, r_db=r_db, quiz_questions=quiz_questions)
    vk_send_keyboard(event, vk_api, random_question)
    vk_logger.debug(f'new_question for {user_id}: question - {random_question} ')
    return 'waiting_for_answer'


def conversation_handler(event, vk_api):
    text_from_user = event.text
    user_id = event.user_id
    if text_from_user:
        new_question(event, vk_api)


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

