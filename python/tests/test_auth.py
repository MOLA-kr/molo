from unittest import TestCase
import os
import json
from molo.auth import Auth
from molo.exceptions import UnconnectedHostError, InvalidAuthError


# 신유
class TestAuth(TestCase):
    def setUp(self) -> None:
        self.valid_url = 'http://192.168.3.116/api'
        self.valid_id = 'pipeline@rapa.org'
        self.valid_pw = 'netflixacademy'
        self.invalid_url = 'http://192.168.3.116'
        self.invalid_id = 'pipeline@rapa.or'
        self.invalid_pw = 'netflixacadem'
        self.auth = Auth()

    def tearDown(self) -> None:
        os.remove(self.auth.user_path)
        os.system(f'rm -rf {self.auth.dir_path}')

    def test_valid_host(self):
        self.assertEqual(self.auth.valid_host, self.auth._valid_host)

    def test_valid_user(self):
        self.assertEqual(self.auth.valid_user, self.auth._valid_user)

    def test_host(self):
        self.assertEqual(self.auth.host, self.auth._host)

    def test_user(self):
        self.assertEqual(self.auth.user, self.auth._user)

    def test_connect_host(self):
        with self.assertRaises(InvalidAuthError):
            self.auth.connect_host(self.invalid_url)
        self.assertNotEqual(self.auth.host, self.invalid_url)
        self.assertTrue(self.auth.host in ['', None])
        self.assertFalse(self.auth.valid_host)

        self.assertTrue(self.auth.connect_host(self.valid_url))
        self.assertEqual(self.auth.host, self.valid_url)
        self.assertTrue(self.auth.valid_host)

    def test_log_in(self):
        # host에 연결하지 않은 경우 login 되지 않아야 함
        with self.assertRaises(UnconnectedHostError):
            self.auth.log_in(self.valid_id, self.valid_pw)
            self.auth.log_in(self.valid_id, self.invalid_pw)
            self.auth.log_in(self.invalid_id, self.valid_pw)
            self.auth.log_in(self.invalid_id, self.invalid_pw)
        self.assertIsNone(self.auth.user)
        self.assertNotEqual(self.auth._user_id, self.valid_id)
        self.assertNotEqual(self.auth._user_pw, self.valid_pw)
        self.assertFalse(self.auth.valid_user)

        # host에 연결된 상태에서 잘못된 id와 pw로는 login 되지 않아야 함
        self.auth.connect_host(self.valid_url)
        with self.assertRaises(InvalidAuthError):
            self.auth.log_in(self.valid_id, self.invalid_pw)
            self.auth.log_in(self.invalid_id, self.valid_pw)
            self.auth.log_in(self.invalid_id, self.invalid_pw)
        self.assertIsNone(self.auth.user)
        self.assertNotEqual(self.auth._user_id, self.valid_id)
        self.assertNotEqual(self.auth._user_pw, self.valid_pw)
        self.assertFalse(self.auth.valid_user)

        # host에 연결된 상태에서 유효한 id와 pw로는 login 되어야 함
        self.assertTrue(self.auth.log_in(self.valid_id, self.valid_pw))
        self.assertIsNotNone(self.auth.user)
        self.assertEqual(self.auth._user_id, self.valid_id)
        self.assertEqual(self.auth._user_pw, self.valid_pw)
        self.assertTrue(self.auth.valid_user)

    def test_log_out(self):
        self.auth.connect_host('http://192.168.3.116/api')
        self.auth.log_in('pipeline@rapa.org', 'netflixacademy')
        self.auth.log_out()
        self.assertIsNone(self.auth.user)

    def test_access_setting(self):
        os.remove(self.auth.user_path)
        os.system(f'rm -rf {self.auth.dir_path}')
        self.auth.access_setting()
        self.assertTrue(os.path.exists(self.auth.dir_path))
        self.assertTrue(os.path.exists(self.auth.user_path))

    def test_load_setting(self):
        # json의 valid_host가 False인 경우
        invalid_dict = {
            'host': self.invalid_url,
            'user_id': self.invalid_id,
            'user_pw': self.invalid_pw,
            'valid_host': False,
            'valid_user': False,
        }
        with open(self.auth.user_path, 'w') as json_file:
            json.dump(invalid_dict, json_file)
        self.auth.load_setting()
        self.assertIsNone(self.auth.user)
        self.assertNotEqual(self.auth.host, self.invalid_url)
        self.assertNotEqual(self.auth._user_id, self.invalid_id)
        self.assertNotEqual(self.auth._user_pw, self.invalid_pw)
        self.assertFalse(self.auth.valid_host)
        self.assertFalse(self.auth.valid_user)
        os.remove(self.auth.user_path)
        os.removedirs(self.auth.dir_path)
        self.auth.access_setting()

        # json의 valid_host가 True이고 valid_user가 False인 경우
        invalid_dict = {
            'host': self.valid_url,
            'user_id': self.invalid_id,
            'user_pw': self.invalid_pw,
            'valid_host': True,
            'valid_user': False,
        }
        with open(self.auth.user_path, 'w') as json_file:
            json.dump(invalid_dict, json_file)
        self.auth.load_setting()
        self.assertIsNone(self.auth.user)
        self.assertEqual(self.auth.host, self.valid_url)
        self.assertNotEqual(self.auth._user_id, self.invalid_id)
        self.assertNotEqual(self.auth._user_pw, self.invalid_pw)
        self.assertTrue(self.auth.valid_host)
        self.assertFalse(self.auth.valid_user)
        os.remove(self.auth.user_path)
        os.removedirs(self.auth.dir_path)
        self.auth.access_setting()

        # json의 valid_host와 valid_user가 모두 True인 경우
        valid_dict = {
            'host': self.valid_url,
            'user_id': self.valid_id,
            'user_pw': self.valid_pw,
            'valid_host': True,
            'valid_user': True,
        }
        with open(self.auth.user_path, 'w') as json_file:
            json.dump(valid_dict, json_file)
        self.auth.load_setting()
        self.assertIsNotNone(self.auth.user)
        self.assertEqual(self.auth.host, self.valid_url)
        self.assertEqual(self.auth._user_id, self.valid_id)
        self.assertEqual(self.auth._user_pw, self.valid_pw)
        self.assertTrue(self.auth.valid_host)
        self.assertTrue(self.auth.valid_user)

    def test_save_setting(self):
        self.auth.save_setting()
        user_dict = {}
        with open(self.auth.user_path, 'r') as json_file:
            user_dict = json.load(json_file)
        self.assertEqual(user_dict.get('host'), self.auth.host)
        self.assertEqual(user_dict.get('user_id'), self.auth._user_id)
        self.assertEqual(user_dict.get('user_pw'), self.auth._user_pw)
        self.assertEqual(user_dict.get('valid_host'), self.auth.valid_host)
        self.assertEqual(user_dict.get('valid_user'), self.auth.valid_user)

    def test_reset_setting(self):
        self.auth.reset_setting()
        self.assertEqual(self.auth.host, '')
        self.assertEqual(self.auth._user_id, '')
        self.assertEqual(self.auth._user_pw, '')
        self.assertFalse(self.auth.valid_host)
        self.assertFalse(self.auth.valid_user)
