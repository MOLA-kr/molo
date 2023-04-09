from unittest import TestCase
from auth import Auth
from taskbrowser import TaskBrowser
from comptask import CompTask

import gazu.files


# 서월 + 은진 + 희정
class TestCompTask(TestCase):
    def setUp(self) -> None:
        self.auth = Auth()
        self.auth.connect_host('http://192.168.3.116/api')
        self.auth.log_in('pipeline@rapa.org', 'netflixacademy')
        tb = TaskBrowser()
        tasks = tb.comp_tasks
        self.ct = CompTask(tasks[0])

    def tearDown(self) -> None:
        self.auth.log_out()

    def test_task_status(self):
        value = self.ct.task_status
        status = ['Ready', 'Todo', 'Done', 'WIP', 'WFA']
        self.assertIn(value, status)

    def test_is_ready(self):
        tasks = self.ct.get_other_tasks_status()
        self.assertTrue(tasks[0].get('task_status_name'))

    def test_is_done(self):
        """
        bool: shot에서 compositing task가 Done인지 여부

        Done 상태이면 True, 아니면 False
        """
        self.assertEqual(self.ct.is_done, self.ct.task_dict.get('task_status_name') == 'Done')
        self.assertEqual(self.ct.is_done, self.ct.task_dict.get('task_status_name') != 'Done')

    def test_task_dict(self):
        self.assertEqual(self.ct.task_dict['entity_type_name'], 'Shot')

    def test_shot_dict(self):
        self.assertEqual(self.ct.shot_dict, self.ct._shot_dict)

    def test_proj_dict(self):
        self.assertEqual(self.ct.proj_dict, self.ct._proj_dict)

    def test_proj_name(self):
        self.assertEqual(self.ct.proj_name, self.ct._proj_name)

    def test_seq_name(self):
        self.assertEqual(self.ct.seq_name, self.ct._seq_name)

    def test_shot_name(self):
        self.assertEqual(self.ct.shot_name, self.ct._shot_name)

    def test_proj_id(self):
        self.assertEqual(self.ct.proj_id, self.ct._proj_id)

    def test_seq_id(self):
        self.assertEqual(self.ct.seq_id, self.ct._seq_id)

    def test_shot_id(self):
        self.assertEqual(self.ct.shot_id, self.ct._shot_id)

    def test_fps(self):
        self.assertEqual(self.ct.fps, self.ct._fps)

    def test_ratio(self):
        self.assertEqual(self.ct.ratio, self.ct._ratio)

    def test_resolution(self):
        self.assertEqual(self.ct.resolution, self.ct._resolution)

    def test_frame_in(self):
        self.assertEqual(self.ct.frame_in, self.ct._frame_in)

    def test_frame_out(self):
        self.assertEqual(self.ct.frame_out, self.ct._frame_out)

    def test_revision(self):
        revision = gazu.files.get_last_working_file_revision("1ea59234-4783-469b-97c4-a8c4133dd0e4")
        self.assertTrue(revision.get('revision'))

    def test_get_other_tasks_status(self):
        task = self.ct.get_other_tasks_status()

        self.assertIsInstance(task[0], dict)
        self.assertGreater(len(task), 0)
        self.assertNotIn('Compositing', task[0])
        self.assertIn('task_type_name', task[0])
        self.assertIn('task_type_id', task[0])
        self.assertIn('task_status_name', task[0])
        self.assertIn('task_status_id', task[0])

    def test_latest_output_files_info(self):
        file = gazu.files.get_last_output_files_for_entity("ba231d20-3a7d-4b91-8a67-b77013f800e7")
        self.assertIsInstance(file, list)
        self.assertGreater(len(file), 0)

    def test_latest_output_files(self):
        last_output_files = self.ct.latest_output_files()
        self.assertGreater(len(last_output_files), 0)
        self.assertIsInstance(last_output_files[0], dict)
        self.assertEqual(last_output_files[0].get('type'), 'OutputFile')

    def test_all_output_files(self):
        output_files = self.ct.all_output_files()
        self.assertGreater(len(output_files), 0)
        self.assertIsInstance(output_files[0], dict)
        self.assertEqual(output_files[0].get('type'), 'OutputFile')

    def test_check_new_thing(self):
        self.fail()

    def test_get_comment(self):
        comment = self.ct.get_comments()

        self.assertIsInstance(comment, dict)
