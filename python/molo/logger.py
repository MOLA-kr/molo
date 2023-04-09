import logging
import os
from .exceptions import *


class Logger:
    """
    User(comp artist)가 타 부서의 output file을 load할 때
    생성되는 Nuke working file에 대한 기록
    """
    def __init__(self):
        self.molog = None
        self.dir_path = os.path.expanduser('~/.config/Molo')
        if not os.path.exists(self.dir_path):
            try:
                os.makedirs(self.dir_path)
            except OSError:
                raise AuthFileIOError("Error: Failed to create the directory.")

        self.set_logger()

    def set_logger(self):
        """
        log파일에 기록할 format과 handler 설정

        Returns:
            (.log) file: {user정보, 시간, path, output file path log} data
        """
        self.molog = logging.getLogger('molo')

        if len(self.molog.handlers) == 0:
            # 중복 logging 방지
            '''어떤 유저가 / 언제 / 어떤 아웃풋파일(path)로부터 / 어디에 working file을 생성했는지'''
            formatting = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
            self.molog.setLevel(logging.DEBUG)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatting)
            stream_handler.setLevel(logging.INFO)
            self.molog.addHandler(stream_handler)

            file_handler = logging.FileHandler(os.path.join(self.dir_path, 'molo_test.log'))
            file_handler.setFormatter(formatting)
            file_handler.setLevel(logging.DEBUG)
            self.molog.addHandler(file_handler)

    def connect_log(self, host_url):
        if host_url:
            self.molog.debug(f"successful connection to {host_url}")

    def enter_log(self, user_name):
        if user_name:
            self.molog.debug(f"{user_name}: log-in succeed")

    def create_working_file_log(self, user_name, working_file):
        """
        working file(.nk)이 정확한 위치에 생성 됐는지 확인하는 오류 검출부
        """
        if os.path.exists(working_file):
            self.molog.debug(f"\"{user_name}\" create Nuke file in \"{working_file}\"")
        else:
            self.molog.warning(f"\"{user_name}\" failed to create Nuke file")

    def load_output_file_log(self, user_name, output_file_path):
        """
        각 task의 output file load 시, path 정보 기록
        """
        self.path_list = output_file_path
        return self.molog.debug(f"\"{user_name}\" load output file from \"{output_file_path}\"")
