from gigachat import GigaChat
from gigachat.models import Messages, MessagesRole, Chat


class GigaChat_Service:
    __service: GigaChat
    __history: Chat

    def __init__(self, key_token: str, start_message: str):
        self.__service = GigaChat(credentials=key_token)
        self.reset_chat_history(start_message)

    def send_message(self, message: str):
        message = Messages(content=message, role=MessagesRole.USER)

        self.__send_message__(message)

    def send_message_with_file(self, message: str, file_ids: list[str]):
        message = Messages(content=message, role=MessagesRole.USER, attachments=file_ids)
        
        self.__send_message__(message)
        
    def __send_message__(self, message: Messages):
        neuro_answer = self.__service.chat(self.__history)
        
        self.__history.append(message)
        self.__history.messages.extend(map(lambda x: x.message, neuro_answer.choices))
    
    def upload_file_from_disk(self, file_path: str):
        with open(file_path, "rb") as file:
            return self.__service.upload_file(file)
        
    def reset_chat_history(self, start_message: str):
        self.__history.messages.clear()
        self.__history.messages.append(Messages(content=start_message, role=MessagesRole.SYSTEM))

    def get_chat_history(self) -> Chat:
        return self.__history
    