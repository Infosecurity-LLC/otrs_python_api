import json
import requests

from otrs_python_api.exceptions import OTRSException, AuthError, HTTPMethodNotSupportedError, OTRSBadResponse, \
    AccessDeniedError, InvalidParameterError, InvalidInitArgument
from otrs_python_api.session import Session
from otrs_python_api.utils.configuration_loading import logger


class Connection:
    # Unit of measurement of constants - seconds
    DEFAULT_SESSION_TIMEOUT = 28800
    DEFAULT_CONNECT_TIMEOUT = 60.0
    DEFAULT_READ_TIMEOUT = 60.0

    def __init__(self, url: str, login: str, password: str, interface: str, session_timeout: int = None,
                 session_id: str = None, session_time_created: str = None, priority: int = None, verify: bool = None,
                 webservice_url: str = None, connect_timeout: float = None, read_timeout: float = None):
        self._login = login
        self._password = password
        self._session_timeout = session_timeout or Connection.DEFAULT_SESSION_TIMEOUT
        self._connect_timeout = connect_timeout or Connection.DEFAULT_CONNECT_TIMEOUT
        self._read_timeout = read_timeout or Connection.DEFAULT_READ_TIMEOUT
        self._verify = verify
        self._priority = priority or 3
        self._webservice_url = webservice_url or f"{url}/otrs/nph-genericinterface.pl/Webservice/{interface}/"
        self.validate_args(url=url, interface=interface)
        self._session = Session(session_id=session_id, time_created=session_time_created,
                                read_timeout=self._read_timeout, expiry=self._session_timeout)

    def validate_args(self, url: str, interface: str):
        if not isinstance(url, str):
            raise InvalidInitArgument(f"Url {url} must be str")
        if not isinstance(interface, str):
            raise InvalidInitArgument(f"Interface {interface} must be str")
        if not isinstance(self._webservice_url, str):
            raise InvalidInitArgument(f"Webservice url {self._webservice_url} must be str")
        if not isinstance(self._login, str):
            raise InvalidInitArgument(f"Login {self._login} must be str")
        if not isinstance(self._password, str):
            raise InvalidInitArgument(f"Password {self._password} must be str")
        if not isinstance(self._session_timeout, int):
            raise InvalidInitArgument(f"Session timeout {self._session_timeout} must be int")
        if not isinstance(self._priority, int):
            raise InvalidInitArgument(f"Priority {self._priority} must be int")
        if not isinstance(self._connect_timeout, float):
            raise InvalidInitArgument(f"Connect timeout {self._connect_timeout} must be float")
        if not isinstance(self._read_timeout, float):
            raise InvalidInitArgument(f"Priority {self._read_timeout} must be float")

    def _create_session(self) -> str:
        response = self._perform_request(http_method='POST', url=f'{self._webservice_url}Session', proxies=None,
                                         UserLogin=self._login, Password=self._password)
        self._check_response_params(response)
        session_id = response.get('SessionID')
        if not session_id:
            raise OTRSException('session not created')
        logger.info('create session {}'.format(session_id))

        prev_recorded_session_id = self._session.get_session()
        if prev_recorded_session_id:
            return prev_recorded_session_id
        self._session.set_session(session_id)
        return session_id

    @staticmethod
    def _check_response_params(response: dict):
        if response.get('Error'):
            err_code = response['Error']['ErrorCode']
            err_msg = response['Error']['ErrorMessage']
            if 'AuthFail' in err_code:
                raise AuthError(err_msg)
            elif 'AccessDenied' in err_code:
                raise AccessDeniedError(err_msg)
            elif 'InvalidParameter' in err_code:
                raise InvalidParameterError(err_msg)
            else:
                raise OTRSException(response)

    def _perform_request(self, http_method: str, url: str, proxies, **kwargs) -> dict:
        logger.debug(f"Url format: {url}, http_method: {http_method}, data: {kwargs}")
        if http_method == 'GET':
            resp = requests.get(url=url, proxies=proxies, verify=self._verify,
                                timeout=(self._connect_timeout, self._read_timeout))
        elif http_method == 'POST':
            resp = requests.post(url=url, data=json.dumps(kwargs),
                                 proxies=proxies, verify=self._verify,
                                 timeout=(self._connect_timeout, self._read_timeout))
        elif http_method == 'PATCH':
            resp = requests.patch(url=url, data=json.dumps(kwargs),
                                  proxies=proxies, verify=self._verify,
                                  timeout=(self._connect_timeout, self._read_timeout))
        else:
            raise HTTPMethodNotSupportedError()

        if resp.status_code != 200:
            raise OTRSBadResponse(resp.text)

        return resp.json()

    def _collecting_request_url(self, semantic_url: str, **kwargs) -> str:
        prepared_url = self._webservice_url + semantic_url
        session_id = self._session.get_session()
        if not session_id:
            session_id = self._create_session()
        url = prepared_url.format(SessionID=session_id, **kwargs)
        return url

    def send_request(self, http_method: str, semantic_url: str, proxies=None, **kwargs) -> dict:
        url = self._collecting_request_url(semantic_url, **kwargs)
        response = self._perform_request(http_method, url, proxies, **kwargs)
        try:
            self._check_response_params(response)
        except AuthError:
            self._session.clear_session()
            url = self._collecting_request_url(semantic_url, **kwargs)
            response = self._perform_request(http_method, url, proxies, **kwargs)
            self._check_response_params(response)

        return response
