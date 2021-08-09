#API клиент для сайта Rabota.RU
#license https://spdx.org/licenses/0BSD.html BSD Zero Clause License

import requests

#Исключение API клиента
class RabotaException(Exception):

    #Ошибка
    #var string
    __error: str

    #Описание ошибки
    __description: str

    #Диалог
    __response: requests.Response 

    def __init__(self, error, description, response = None):
        self.error       = error
        self.response    = response
        self.description = description

        #super().
        #parent::__construct($error, $response ? $response->getHttpCode() : 500);

    #Возвращает ошибку
    def get_error(self) -> str:
        return self.error

    #Возвращает описание ошибки
    def get_description(self) -> str:
        return self.description

    #Возвращает диалог
    def get_response(self) -> str:
        return self.response
