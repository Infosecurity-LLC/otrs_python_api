import threading
import time

from otrs_python_api.exceptions import InvalidInitArgument


class Session:
    def __init__(self, read_timeout: float, session_id: str = None, time_created: int = None, expiry: int = None):
        """
        Stores and caches session data
        :param read_timeout: Used to determine session expiration
        :param session_id: Session id
        :param time_created: Session creation time
        :param expiry: Session timeout
        """
        self._read_timeout = read_timeout
        self._session_id = session_id
        self._time_created = time_created
        self._expiry = expiry or 28800
        self._lock = threading.Lock()
        self.validate_args()

    def validate_args(self):
        if not isinstance(self._read_timeout, float):
            raise InvalidInitArgument(f"Read timeout {self._read_timeout} must be float")
        if self._session_id and not isinstance(self._session_id, str):
            raise InvalidInitArgument(f"Session cache file {self._session_id} must be str")
        if self._time_created and not isinstance(self._time_created, int):
            raise InvalidInitArgument(f"Read timeout {self._time_created} must be int")

    def get_expiry_age(self):
        """
        Get the number of seconds until the session expires. If the session is empty return None
        """
        if not self._session_id or not self._time_created:
            return None
        time_diff = int(time.time()) - self._time_created
        expiry_age = self._expiry - time_diff
        return expiry_age

    def get_session(self):
        """
        Get session and check if the session has expired. If the session is empty or the session has expired return None
        """
        self._lock.acquire()
        try:
            if not self._session_id or not self._time_created:
                return None

            expiry_age = self.get_expiry_age()
            if not expiry_age:
                self._session_id, self._time_created = None, None
                return None
            if expiry_age < self._read_timeout:
                self._session_id, self._time_created = None, None
                return None
        finally:
            self._lock.release()
        return self._session_id

    def clear_session(self):
        self._lock.acquire()
        try:
            self._session_id, self._time_created = None, None
        finally:
            self._lock.release()

    def set_session(self, session_id: str):
        self._lock.acquire()
        try:
            time_created = int(time.time())
            self._session_id = session_id
            self._time_created = time_created
        finally:
            self._lock.release()
