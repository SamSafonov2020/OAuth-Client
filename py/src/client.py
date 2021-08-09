"""
 * API клиент для сайта Rabota.RU
 *
 * @license https://spdx.org/licenses/0BSD.html BSD Zero Clause License
"""

import json
from datetime import datetime
import requests
from rabota_exception import RabotaException
from hashlib import sha256

#namespace RabotaApi;

#HTTP методы
HTTP_GET = 'GET'
HTTP_POST = 'POST'

#Хост для апи
HOST = 'https://api.rabota.ru'
SANDBOX_HOST = 'https://api.rabota.wtf'

#Поле авторизации
TOKEN_NAME = 'X-Token'

#Основные эндпоинты
POINT_AUTHORIZATION = '/oauth/authorize.html'       # Эндпоинт авторизации
POINT_GET_TOKEN = '/oauth/token.json'               # Эндпоинт получение токена по коду
POINT_REFRESH_TOKEN = '/oauth/refresh-token.json'   # Эндпоинт обновление токена
POINT_LOGOUT = '/oauth/logout.json'                 # Эндпоинт завершение сеанса


#Наименования полей
    
FIELD_TOKEN = 'access_token'                        # Имя ключа токена в ответе
FIELD_EXPIRES = 'expires_in'                        # Имя ключа времени жизни токена в овете
FIELD_SIGNATURE = 'signature'                       # Имя ключа подписи запроса
FIELD_APP_ID = 'app_id'                             # Код приложения
FIELD_REDIRECT = 'redirect_uri'                     # Адрес возрата
FIELD_DISPLAY = 'display'                           # Вид страницы авторизации
FIELD_CODE = 'code'                                 # Код для получения токена
FIELD_TIME = 'time'                                 # Код для получения токена
FIELD_SCOPE = 'scope'                               # Требуемые разрешения

#Параметр токена при запросе
PARAM_TOKEN = 'token'


#Скопы доступа
SCOPE_PROFILE = 'profile'
SCOPE_VACANSIES = 'vacancies'
SCOPE_RESUME = 'resume'


#Вид отображения окна авторизации
DISPLAY_PAGE = 'page'                               # в виде страници
DISPLAY_POPUP = 'popup'                             # в виде PopUp страници


#Api клиент
class Client:



    def __init__(self, app_id: str, secret: str, token: str = None, expires: int = None):
        #Индификатор приложения
        self._app_id: str = app_id
        #Секретный код приложения
        self._secret: str = secret
        #Token доступа
        self._token: str = token
        #Время устаревания токена
        self._expires: int = expires
        self._api_uri: str = HOST


    #Преключиться на песочницу
    def set_sandbox(self, host = SANDBOX_HOST):
        self._api_uri = host
    
    #Преключиться на продакшен
    def switch_prod(self):
        self._api_uri = HOST

     #Получение ссылки на автаризацию
     #param string $redirect Адрес редиректа после авторизации
     #param string $display  Внешний вид диалога
     #param array  $scope
     #return string
    def get_authentication_url(self, redirect, display = DISPLAY_PAGE, scope = ['profile', 'vacancies', 'resume']):
        #_scope = scope implode(",", scope)
        parameters = {
            FIELD_APP_ID: self._app_id,
            FIELD_REDIRECT: redirect,
            FIELD_DISPLAY: display,
            FIELD_SCOPE: scope
        }
        return self._api_uri + POINT_AUTHORIZATION + '?' + http_build_query(parameters, None, '&')

    #Получение токена доступа
    #param string $code Код авторизации
    #return array
    def request_token(self, code):
        response = self.fetch(
            POINT_GET_TOKEN,
            {
                FIELD_CODE: code,
                'app_id': self._app_id,
            },
            HTTP_POST,
            True
        )
        result = response.get_json_decode()

        if result is None:
            raise RabotaException("Не удалось получить токен", resp)

        if FIELD_TOKEN in result:
            self.set_token(result[FIELD_TOKEN])
            self.expires = datetime.now() + result[FIELD_EXPIRES]
        
        return result

    #Проверить устарел ли токен доступа
    #return boolean
    def is_expires(self):
        from datetime import datetime
        return self._expires < datetime.now()

    #Получение текущего токена доступа
    #return strin
    def get_token(self):
        return self._token

    #Время устаревания токена
    #return string
    def get_expires(self):
        return self.expires
    
    #Установить токен доступа
    #param string $token Токен доступа
    def set_token(self, token):
        self.token = token

    #Выполнить запрос
    #param string       $resource_url Адрес API метода
    #param array        $parameters   Параметры запроса
    #param string|null  $method       HTTP метод запроса
    #param boolean|null $subscribe    Подписать запорс
    #return \RabotaApi\Response

    def fetch(
        self,
        resource_url,
        parameters = {},
        method = HTTP_GET,
        subscribe = False
    ):
        # если токен устарел, обновляем его
        if self.get_token() and self.is_expires():
            self.refresh_token()
        

        # подписываем запрос
        if subscribe:
            parameters[FIELD_TIME] = datetime.now()
            parameters[FIELD_SIGNATURE] = self.get_signature(parameters)
        
        return self.execute_request(
            resource_url,
            parameters,
            method,
            self.token
        )
   

    #Выполнить запрос
    #param string      $url        Адрес API метода
    #param mixed       $parameters Параметры запроса
    #param string|null $method     HTTP метод запроса
    #param null        $token
    #return \RabotaApi\Response

    def __execute_request(
        self,
        url: str,
        parameters = [],
        method = HTTP_GET,
        token = None
    ):
        resp = None

        url = self._api_uri + url

        #параметры из url передаются в список параметров
        if url.find("?") > 0:
            url_params = url.split("?")
            #list($url, $url_params) = explode('?', $url, 2)
            #parse_str($url_params, $url_params)
            parameters = url_params + parameters

        #curl_options = {
        #    CURLOPT_RETURNTRANSFER: True,
        #    CURLOPT_SSL_VERIFYPEER: 1,
        #    CURLOPT_CUSTOMREQUEST: method,
        #    CURLOPT_FOLLOWLOCATION: True,
        #    CURLOPT_URL: url,
        #}

        _headers = {}
        if token:
            _headers[TOKEN_NAME] = token
        
        _data = {}
        if method == HTTP_GET:
            for k, v in parameters:
                _data[k] = v

            resp = requests.get(url, data=_data, verify=False)
        elif method == HTTP_POST:
            for k, v in parameters:
                _data[k] = v

            resp = requests.post(url, data=_data, headers=_headers, verify=False)
        else:
            raise RabotaException('no_support_method', 'Неподдерживаемый метод запроса', resp)

        if resp and resp.status_code != 200:
            json_str = resp.text
            json_obj = json.loads(json_str)

            code = resp.status_code
            desc = 'Неизвестная ошибка'
            if 'error' in json_obj and 'description' in json_obj:
                code = json_obj['error']
                desc = json_obj['description']
                #токен устарел
                if code == 'invalid_token':
                    self.refresh_token()
                    parameters[FIELD_TOKEN] = self.get_token()
                    return self.__execute_request(url, parameters, method)

                #токен не найден
                if code == 'undefined_token':
                    self.token = None
                    self.expires = None
                
            elif 'code' in json_obj and 'error' in json_obj:
                code = json_obj['code']
                desc = json_obj['error']
            
            raise RabotaException(code, desc, resp)
        
        return resp

    #Выход
    def logout(self):
        self.fetch(
            POINT_LOGOUT,
            {
                FIELD_TOKEN: self.token
            },
            HTTP_GET
        )
        self._token = None
        self._expires = None
    

    #Обновление токена доступа
    #return array
    def refresh_token(self):
        resource_url = POINT_REFRESH_TOKEN
        parameters = {
            FIELD_TIME: datetime.now(),
            PARAM_TOKEN: self._token,
            FIELD_APP_ID: self._app_id
        }
        parameters[FIELD_SIGNATURE] = self.__get_signature(parameters)
        request = self.__execute_request(
            resource_url,
            parameters,
            HTTP_POST
        )
        result = request.get_json_decode()

        if FIELD_TOKEN in result:
            self.set_token(result[FIELD_TOKEN])
            self._expires = datetime.now() + result[FIELD_EXPIRES]
        
        return result

    #Строит подпись
    #param array  $vars
    #return string
    def __get_signature(self, vars = []):
        for k, v in vars:
            vars[k] = str(v)
        
        hash = sha256(json.dumps(vars).encode('utf-8') + self._secret.encode('utf-8')).hexdigest()
        return hash

