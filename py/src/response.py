#API клиент для сайта Rabota.RU
#license https://spdx.org/licenses/0BSD.html BSD Zero Clause License

#Ответ сервера
class Response:

    #URL запроса
    #var string
    __url = ''

    #Параметры запорса
    #var array
    __parameters = []

    #HTTP код ответа
    #var integer
    __http_code = 0

    #Content-Type ответа
    #var string
    __content_type = ''

    #HTTP заголовки запроса
    #var array
    __request = []

    #HTTP заголовки ответа
    #var array
    __response = []

    #Тело ответа
    #var array
    __body = ''

    /**
     * Декодированный JSON тела ответа
     *
     * @var mixed
     */
    private $json_decode = [];

    def __init__(self, response, ch, url, parameters = [], debug = False):
        #разбор параметров запроса
        if ($debug) {
            $this->content_type = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
            // разбор запроса к серверу
            $this->request = curl_getinfo($ch, CURLINFO_HEADER_OUT);
            $this->request = explode("\n", str_replace("\r\n", "\n", trim($this->request)));
            // разбор ответа от сервера
            $this->body = substr($response, curl_getinfo($ch, CURLINFO_HEADER_SIZE));
            $this->response = substr($response, 0, curl_getinfo($ch, CURLINFO_HEADER_SIZE));
            $this->response = explode("\n", str_replace(["\r\n", "\n\n"], "\n", trim($this->response)));
        } else {
            $this->body = $response;
        }
        $this->url = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
        $this->parameters = $parameters;
        $this->http_code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $this->json_decode = json_decode($this->body, true);
    }

    /**
     * Возвращает URL запроса
     *
     * @return string
     */
    public function getUrl()
    {
        return $this->url;
    }

    /**
     * Возвращает параметры запорса
     *
     * @return array
     */
    public function getParameters()
    {
        return $this->parameters;
    }

    /**
     * Возвращает HTTP код ответа
     *
     * @return integer
     */
    public function getHttpCode()
    {
        return $this->http_code;
    }

    /**
     * Возвращает Content-Type ответа
     *
     * @return string
     */
    public function getContentType()
    {
        return $this->content_type;
    }

    /**
     * Возвращает HTTP заголовки запроса
     *
     * @return array
     */
    public function getRequest()
    {
        return $this->request;
    }

    /**
     * Возвращает HTTP заголовки ответа
     *
     * @return array
     */
    public function getResponse()
    {
        return $this->response;
    }

    /**
     * Возвращает тело ответа
     *
     * @return array
     */
    public function getBody()
    {
        return $this->body;
    }

    /**
     * Возвращает декодированный JSON тела ответа
     *
     * @return array
     */
    public function getJsonDecode()
    {
        return $this->json_decode;
    }

    /**
     * Возвращает параметры запроса в виде массива
     *
     * @return array
     */
    public function toArray()
    {
        return [
            'url'          => $this->url,
            'parameters'   => $this->parameters,
            'request'      => $this->request,
            'http_code'    => $this->http_code,
            'content_type' => $this->content_type,
            'response'     => $this->response,
            'body'         => $this->body,
            'json_decode'  => $this->json_decode,
        ];
    }
}