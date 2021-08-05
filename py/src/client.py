"""
 * API клиент для сайта Rabota.RU
 *
 * @license https://spdx.org/licenses/0BSD.html BSD Zero Clause License
"""

import json
from datetime import datetime

#namespace RabotaApi;

#Api клиент
class Client:

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


    def __init__(self, app_id: str, secret: str, token: str = None, expires: int = None):
        #Индификатор приложения
        self._app_id: str = app_id

        #Секретный код приложения
        self._secret: str = secret

        #Token доступа
        self._token: str = token

        #Время устаревания токена
        self._expires: int = expires

        self._api_uri: str = Client.HOST


    #Преключиться на песочницу
    def set_sandbox(self, host = Client.SANDBOX_HOST):
        self._api_uri = host
    
    #Преключиться на продакшен
    def switch_prod(self):
        self._api_uri = Client.HOST

     #Получение ссылки на автаризацию
     #param string $redirect Адрес редиректа после авторизации
     #param string $display  Внешний вид диалога
     #param array  $scope
     #return string
    def get_authentication_url(self, redirect, display = Client.DISPLAY_PAGE, scope = ['profile', 'vacancies', 'resume']):
        #_scope = scope implode(",", scope)
        parameters = {
            Client.FIELD_APP_ID: self._app_id,
            Client.FIELD_REDIRECT: redirect,
            Client.FIELD_DISPLAY: display,
            Client.FIELD_SCOPE: scope
        }
        return self._api_uri + Client.POINT_AUTHORIZATION + '?' + http_build_query(parameters, None, '&')

    #Получение токена доступа
    #param string $code Код авторизации
    #return array
    def request_token(self, code):
        response = self.fetch(
            Client.POINT_GET_TOKEN,
            {
                Client.FIELD_CODE: code,
                'app_id': self._app_id,
            },
            Client.HTTP_POST,
            True
        )
        result = response.get_json_decode()

        if result is None:
            raise Exception("Не удалось получить токен" + response)

        if Client.FIELD_TOKEN in result:
            self.set_token(result[Client.FIELD_TOKEN])
            self.expires = datetime.now() + result[Client.FIELD_EXPIRES]
        
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
        method = Client.HTTP_GET,
        subscribe = False
    ):
        # если токен устарел, обновляем его
        if self.get_token() and self.is_expires():
            self.refresh_token()
        

        # подписываем запрос
        if subscribe:
            parameters[Client.FIELD_TIME] = datetime.now()
            parameters[Client.FIELD_SIGNATURE] = self.get_signature(parameters)
        

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
        url,
        parameters = [],
        method = Client.HTTP_GET,
        token = None
    ):
        url = self._api_Uri + url

        #параметры из url передаются в список параметров
        if (strpos(url, '?') !== false):
            list($url, $url_params) = explode('?', $url, 2)
            parse_str($url_params, $url_params)
            parameters = url_params + parameters

        curl_options = {
            CURLOPT_RETURNTRANSFER: True,
            CURLOPT_SSL_VERIFYPEER: 1,
            CURLOPT_CUSTOMREQUEST: method,
            CURLOPT_FOLLOWLOCATION: True,
            CURLOPT_URL: url,
        }

        if token:
            $curl_options[CURLOPT_HTTPHEADER] = [static::TOKEN_NAME . ":" . $token];
        

        switch ($method) {
            case self::HTTP_GET:
                $url .= '?' . http_build_query($parameters);
                $curl_options[CURLOPT_URL] = $url;
                break;
            case self::HTTP_POST:
                $curl_options[CURLOPT_POST] = true;
                $curl_options[CURLOPT_POSTFIELDS] = http_build_query($parameters);
                break;
            default:
                throw new Exception('no_support_method', 'Неподдерживаемый метод запроса', null);
        }

        $ch = curl_init();
        curl_setopt_array($ch, $curl_options);

        $dialogue = new Response(curl_exec($ch), $ch, $url, $parameters);

        curl_close($ch);
        $json_decode = $dialogue->getJsonDecode();

        if ($dialogue->getHttpCode() != 200) {
            $code = $dialogue->getHttpCode();
            $desc = 'Неизвестная ошибка';
            if (isset($json_decode['error'], $json_decode['description'])) {
                $code = $json_decode['error'];
                $desc = $json_decode['description'];
                #токен устарел
                if ($code == 'invalid_token') {
                    $this->refreshToken();
                    $parameters[self::FIELD_TOKEN] = $this->getToken();
                    return $this->executeRequest($url, $parameters, $method);
                }
                #токен не найден
                if ($code == 'undefined_token') {
                    $this->token = null;
                    $this->expires = null;
                }
            } elseif (isset($json_decode['code'], $json_decode['error'])) {
                $code = $json_decode['code'];
                $desc = $json_decode['error'];
            }
            throw new Exception($code, $desc, $dialogue);
        }
        return $dialogue;
    }

    #Выход
    def logout(self):
        self.fetch(
            Client.POINT_LOGOUT,
            {
                Client.FIELD_TOKEN: self.token
            },
            Client.HTTP_GET
        );
        self.token = None
        self.expires = None
    

    #Обновление токена доступа
    #return array
    def refresh_token(self):
        resource_url = Client.POINT_REFRESH_TOKEN
        parameters = {
            Client.FIELD_TIME: time(),
            Client.PARAM_TOKEN: self.token,
            Client.FIELD_APP_ID: self.app_id
        }
        parameters[Client.FIELD_SIGNATURE] = self.get_signature(parameters)
        request = self.__execute_request(
            resource_url,
            parameters,
            Client.HTTP_POST
        )
        result = request.get_json_decode()

        if Client.FIELD_TOKEN in result:
            self.set_token(result[self.FIELD_TOKEN])
            self.expires = datetime.now() + result[Client.FIELD_EXPIRES]
        
        return result

    
    #Строит подпись
    #param array  $vars
    #return string
    def __get_signature(self, vars = []):
        for k, v in vars:
            vars[k] = str(v)
        
        return hash('sha256', json.encode(vars) . self.secret, False)

