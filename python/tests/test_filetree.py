from unittest import TestCase
from molo.auth import Auth
from molo.filetree import FileTree
import gazu


# 희정
class TestFileTree(TestCase):
    def setUp(self) -> None:
        self.auth = Auth()
        self.auth.connect_host('http://192.168.3.116/api')
        self.auth.log_in('pipeline@rapa.org', 'netflixacademy')

    def test_mnt_point(self):
        project = gazu.project.get_project_by_name("Test proj")
        project_tree = project.get('file_tree')
        project_tree_test = project_tree.get('working').get('mountpoint')
        self.mnt_point = project_tree_test

        self.assertEqual(self.mnt_point, project_tree_test)

    def test_init_file_tree(self):
        project = gazu.project.get_project_by_name("Test proj")
        project_tree = project.get('file_tree')
        self.file_tree = project_tree

        self.assertEqual(self.file_tree, project_tree)

    def test_update_file_tree(self):
        project = gazu.project.get_project_by_name("Test proj")
        tree = FileTree(project)
        tree.update_file_tree()
        return_value = project.get('file_tree')

        self.assertGreater(len(return_value), 0)
