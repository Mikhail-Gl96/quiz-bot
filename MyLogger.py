import logging
import datetime as dt


class MyLoggerFormatter(logging.Formatter):
    converter = dt.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        converted_time = self.converter(record.created)
        if datefmt:
            time_with_sec = converted_time.strftime(datefmt)
        else:
            time_no_sec = converted_time.strftime("%Y-%m-%d %H:%M:%S")
            time_with_sec = "%s.%03d" % (time_no_sec, record.msecs)
        return time_with_sec


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def create_my_logger(name, level):
    """Создаем и настраиваем кастомный логгер для каждого модуля"""

    custom_logger = logging.getLogger(name)
    custom_logger.setLevel(level)

    console = logging.StreamHandler()
    custom_logger.addHandler(console)

    formatter = MyLoggerFormatter(fmt="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
                                  datefmt='%Y-%m-%d %H:%M:%S.%f')
    console.setFormatter(formatter)
    return custom_logger

