import os.path
from unittest import TestCase
from molo.auth import Auth
from molo.loader import Loader
from molo.utils import construct_full_path
from molo.taskbrowser import TaskBrowser
from molo.comptask import CompTask
import gazu


# 서월
class TestLoader(TestCase):
    def setUp(self) -> None:
        self.auth = Auth()
        self.auth.connect_host('http://192.168.3.116/api')
        self.auth.log_in('pipeline@rapa.org', 'netflixacademy')
        tb = TaskBrowser()
        tasks = tb.comp_tasks
        self.ct = CompTask(tasks[0])
        self.loader = Loader()

    def tearDown(self) -> None:
        self.auth.log_out()

    def test_open_nuke_working_file(self):
        self.loader.open_nuke_working_file(self.ct.task_dict)
        # last working file이 있다면 path를 가지고, 없다면 새로 만든다.
        working_file_path = self.loader.working_file_path
        self.assertGreater(len(working_file_path), 0)
        self.assertIsInstance(working_file_path, str)

    def test_new_nuke_working_file(self):
        # 새로운 working file 생성
        working_files = self.loader.new_nuke_working_file(self.ct.task_dict)
        self.assertGreater(len(working_files), 0)
        self.assertIsInstance(working_files, dict)
        self.assertEqual(working_files.get('type'), 'WorkingFile')
        # 새로 만든 working file의 path가 있는지
        working_file_path = self.loader.working_file_path
        self.assertGreater(len(working_file_path), 0)
        self.assertIsInstance(working_file_path, str)

        return_file_path = construct_full_path(working_files)
        root_dir = os.path.dirname(return_file_path)
        # 새로 만든 working file의 경로가 디렉토리인지
        self.assertTrue(os.path.isdir(root_dir))
        file_name = os.path.basename(return_file_path)
        # 새로 만든 working file의 이름이 파일 이름인지
        self.assertFalse(os.path.isfile(file_name))

    def test_set_nuke_command(self):
        # 누크 실행문 생성
        nuke_command = self.loader.set_nuke_command(versrion=14.0, nuke_command=None, nc=True, nukex=True)
        self.assertGreater(len(nuke_command), 0)
        self.assertIsInstance(nuke_command, str)
