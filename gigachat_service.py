from gigachat import GigaChat
from gigachat.models import Messages, MessagesRole, Chat

from typing import Final

import os
import httpx
import ssl
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Отключаем предупреждения о SSL
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

START_MESSAGE: Final = """Ты являешься экспертом в области анализа оплаты труда и экономического моделирования, специализируешься на оценке уровня заработных плат. 
Твоя задача — анализировать данные и предлагать рекомендации по повышению оплаты труда."""

ANALYZE_MESSAGE: Final = """На основе данных из файла определи текущий ({}) и 
предыдущий ({}) кварталы. Сравни уровни оплаты 
труда за эти периоды. В ответе приведи только 
список конкретных мер для повышения оплаты труда, без анализа, 
вводных фраз, заголовков и примеров. Ответ должен 
быть максимально кратким, только меры. НЕ НАДО ОПИСЫВАТЬ МНЕ АНАЛИЗ ТУПОЕ ТЫ СОЗДАНИЕ!!!
"""


class GigaChat_Service:
    __start_message: str

    __service: GigaChat
    __history: list

    def __init__(self, key_token: str, start_message: str):
        self.__start_message = start_message
        
        # Глобально отключаем проверку SSL для всех httpx запросов
        self._disable_ssl_verification()
        
        self.__service = GigaChat(credentials=key_token)
        self.__history = []

        # Откладываем инициализацию чата до первого вызова
        # чтобы избежать ошибок при создании объекта

    def _disable_ssl_verification(self):
        """Глобально отключает проверку SSL сертификатов"""
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
    def send_message(self, message: str):
        try:
            message_obj = Messages(content=message, role=MessagesRole.USER)
            return self.__send_message__(message_obj)
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
            raise

    def send_message_with_file(self, message: str, file_ids: list[str]):
        try:
            message_obj = Messages(
                content=message, role=MessagesRole.USER, attachments=file_ids
            )
            return self.__send_message__(message_obj)
        except Exception as e:
            print(f"Ошибка при отправке сообщения с файлом: {e}")
            raise

    def __send_message__(self, message: Messages):
        try:
            # Инициализируем историю при первом вызове
            if not self.__history:
                self.__initialize_chat_history()
                
            history = Chat(messages=self.__history)
            neuro_answer = self.__service.chat(history)

            self.__history.append(message)
            self.__history.extend(map(lambda x: x.message, neuro_answer.choices))

            return neuro_answer
        except Exception as e:
            print(f"Ошибка в __send_message__: {e}")
            raise

    def __initialize_chat_history(self):
        """Инициализирует историю чата при первом использовании"""
        self.__history.append(Messages(content=self.__start_message, role=MessagesRole.SYSTEM))
        # Не отправляем стартовое сообщение сразу, чтобы избежать ошибок при инициализации

    def upload_file_from_disk(self, file_path: str):
        try:
            uploaded_file = None
            with open(file_path, "rb") as file:
                uploaded_file = self.__service.upload_file(file)
            return uploaded_file
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            raise

    def reset_chat_history(self, start_message: str = None):
        if start_message is None:
            start_message = self.__start_message

        self.__history.clear()
        self.__history.append(Messages(content=start_message, role=MessagesRole.SYSTEM))

    def get_chat_history(self) -> Chat:
        return Chat(messages=self.__history)


if __name__ == "__main__":
    pass