from unittest import TestCase
from molo.auth import *
from molo.logger import Logger


# 윤주
class TestLogger(TestCase):
    def setUp(self):
        # self.molog = None
        # self.set_logger()
        self.logger = Logger()
        self.auth = Auth()
        self.auth.connect_host('http://192.168.3.116/api')
        self.auth.log_in('pipeline@rapa.org', 'netflixacademy')

    def tearDown(self):
        self.auth.log_out()

    def test_set_logger(self):
        assert False

    def test_enter_log(self):
        assert False

    def test_create_working_file_log(self):
        # self.logger.set_logger()
        user_name = self.auth.user.get('full_name')
        working_file = "/mnt/pipeline/personal/minjichoi/kitsu/test_proj/shots/sq03/sh01/animation/workfile/023" \
                       "/test_projsq03sh01animation023.nk"
        with self.assertLogs() as captured:
            self.logger.create_working_file_log(user_name=user_name, working_file=working_file)
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), f"\"{user_name}\" create Nuke file in \"{working_file}\"")

    def test_load_output_file_log(self):
        assert False
