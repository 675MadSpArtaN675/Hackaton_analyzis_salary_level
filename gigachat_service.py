from gigachat import GigaChat
from gigachat.models import Messages, MessagesRole, Chat

import os

class GigaChat_Service:
    __start_message: str

    __service: GigaChat
    __history: Chat

    def __init__(self, key_token: str, start_message: str):
        self.__start_message = start_message

        self.__service = GigaChat(credentials=key_token)
        self.reset_chat_history(start_message)

    def send_message(self, message: str):
        message = Messages(content=message, role=MessagesRole.USER)

        return self.__send_message__(message)

    def send_message_with_file(self, message: str, file_ids: list[str]):
        message = Messages(content=message, role=MessagesRole.USER, attachments=file_ids)
        
        return self.__send_message__(message)
        
    def __send_message__(self, message: Messages):
        neuro_answer = self.__service.chat(self.__history)
        
        self.__history.append(message)
        self.__history.messages.extend(map(lambda x: x.message, neuro_answer.choices))
        
        return neuro_answer
    
    def upload_file_from_disk(self, file_path: str):
        uploaded_file = None
        with open(file_path, "rb") as file:
            uploaded_file = self.__service.upload_file(file)
        
        os.remove(file_path)
        return uploaded_file
        
    def reset_chat_history(self, start_message: str = None):
        if start_message is None:
            if self.__start_message is not None:
                start_message = self.__start_message
            else:
                return
        
        self.__history.messages.clear()
        self.__history.messages.append(Messages(content=start_message, role=MessagesRole.SYSTEM))

    def get_chat_history(self) -> Chat:
        return self.__history
    