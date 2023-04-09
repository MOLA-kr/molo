"""
사용자가 MOLA를 사용하기 위한 정보를 로컬에 저장하고 가져오거나
호스트와 연결하고 로그인 하기 위한 기능들
"""

from .logger import Logger
from .exceptions import *
import gazu
import os
import json


class Auth:
    """
    사용자의 kistu 계정 정보를 관리하기 위한 class

    local 환경에 저장된 계정 정보를 관리하고, gazu client에 login, logout
    객체 생성시 json file을 찾아 host 연결과 로그인을 시도
    """
    def __init__(self) -> None:
        self.logger = Logger()

        self._host = ''
        self._user = None
        self._user_id = ''
        self._user_pw = ''
        self._valid_host = False
        self._valid_user = False

        self.dir_path = os.path.expanduser('~/.config/Molo/')
        self.user_path = os.path.join(self.dir_path, 'user.json')

        if self.access_setting():
            self.load_setting()

    @property
    def valid_host(self):
        """
        Returns:
            bool: host 연결에 성공했다면 True, 아니면 False
        """
        return self._valid_host

    @property
    def valid_user(self):
        """
        Returns:
            bool: 로그인에 성공했다면 True, 아니면 False
        """
        return self._valid_user

    @property
    def host(self):
        """
        Returns:
            str: 연결된 host URL
        """
        return self._host

    @property
    def user(self):
        """
        Returns:
            dict: 로그인한 계정의 user dict
        """
        return self._user

    def connect_host(self, try_host) -> bool:
        """
        try_host를 사용해 host에 접속 시도

        Returns:
            bool: 접속에 성공하면 True, 아니면 False 반환
        """
        gazu.set_host(try_host)
        if not gazu.client.host_is_valid():
            raise InvalidAuthError('Error: Invalid host URL.')
        self._host = gazu.get_host()
        self._valid_host = True
        self.logger.connect_log(self.host)
        return True

    def log_in(self, try_id, try_pw) -> bool:
        """
        try_id, try_pw를 사용해 로그인 시도

        Returns:
            bool: 접속에 성공하면 True, 아니면 False 반환
        """

        if not self._valid_host:
            raise UnconnectedHostError('Error: Host to login is not connected.')

        try:
            log_in = gazu.log_in(try_id, try_pw)
        except gazu.AuthFailedException:
            raise InvalidAuthError('Error: Invalid user ID or password.')

        self._user = log_in['user']
        self._user_id = try_id
        self._user_pw = try_pw
        self._valid_user = True
        self.logger.enter_log(self.user.get("full_name"))
        return True

    def log_out(self):
        """
        log out한 후 json에서 저장되어있던 user 정보 삭제
        """
        gazu.log_out()
        self._user = None

        self._user_id = ''
        self._user_pw = ''
        self._valid_user = False
        self.save_setting()

    def access_setting(self):
        """
        디렉토리와 각 json 파일이 존재하는지 확인하고 없으면 초기화

        Returns:
            bool: self.user_path에 해당하는 json 파일이 존재하거나 생성되면 True, 아니면 False
        """
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise AuthFileIOError("Error: Failed to create the directory.")

        try:
            if not os.path.exists(self.user_path):
                self.reset_setting()
        except OSError:
            raise AuthFileIOError("Error: Failed to create user.json file.")
        return True

    def load_setting(self):
        """
        json file에서 정보를 읽어오기

        json에 기록된 host나 user의 valid 값이 True이면 자동 login
        """
        user_dict = {}
        with open(self.user_path, 'r') as json_file:
            user_dict = json.load(json_file)

        if user_dict.get('valid_host'):
            self.connect_host(user_dict.get('host'))
        if user_dict.get('valid_user'):
            self.log_in(user_dict.get('user_id'), user_dict.get('user_pw'))

    def save_setting(self):
        """
        json file에 정보를 저장
        """
        user_dict = {
            'host': self.host,
            'user_id': self._user_id,
            'user_pw': self._user_pw,
            'valid_host': self.valid_host,
            'valid_user': self.valid_user,
        }
        with open(self.user_path, 'w') as json_file:
            json.dump(user_dict, json_file)

    def reset_setting(self):
        """
        json file에 저장된 정보 삭제
        """
        self._host = ''
        self._user_id = ''
        self._user_pw = ''
        self._valid_host = False
        self._valid_user = False

        self.save_setting()
