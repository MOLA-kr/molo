from unittest import TestCase
from molo.auth import Auth
from molo.taskbrowser import TaskBrowser
import gazu



# sort~ : 은진
# 나머지 : 민지
class TestTaskBrowser(TestCase):
    def setUp(self):
        self.auth = Auth()
        self.auth.connect_host("http://192.168.3.116/api")
        self.auth.log_in("pipeline@rapa.org", "netflixacademy")
        self.tb = TaskBrowser()

    def tearDown(self) -> None:
        self.auth.log_out()    
    
    def test_comp_tasks(self):
        self.assertEqual(self.tb.comp_tasks, self.tb._comp_tasks)

    def test_sorted_by_due_date(self):
        value = self.tb.sorted_by_due_date
        self.assertTrue(value[0].get('due_date') < value[1].get('due_date'))

    def test_sorted_by_priority(self):
        value = self.tb.sorted_by_priority
        self.assertTrue(value[0].get('priority') >= value[1].get('priority'))
    
    def test_is_comp_task_for_user(self):
        self.tb._comp_tasks = []
        self.assertFalse(self.tb.is_comp_task_for_user)

        self.tb._comp_tasks = [1, 2, 3]
        self.assertTrue(self.tb.is_comp_task_for_user)

    def test_refresh_comp_tasks(self):
        tasks = gazu.user.all_tasks_to_do()
        comp = gazu.task.get_task_type_by_name('Compositing')['id']
        todo = gazu.task.get_task_status_by_short_name('todo')['id']
        wip = gazu.task.get_task_status_by_short_name('wip')['id']

        self.tb.refresh_comp_tasks()

        filtered_tasks = []
        for i in tasks:
            if i.get('task_type_id') == comp and i.get('task_status_id') in [todo, wip]:
                filtered_tasks.append(i)

        self.assertEqual(len(self.tb.comp_tasks), len(filtered_tasks))
        for i in range(len(self.tb.comp_tasks)):
            self.assertDictEqual(self.tb.comp_tasks[i], filtered_tasks[i])

    def test_sort_by(self):
        value = self.tb.sort_by("due_date")
        self.assertTrue(value[0].get('due_date') < value[1].get('due_date'))

        self.tb.sort_by("priority", True)
        self.assertTrue(value[0].get('priority') >= value[1].get('priority'))

    # def test_check_new_thing(self):
    #     self.fail()

    def test_user_info_tree(self):
        tree = self.tb.user_file_tree()
        self.assertGreater(len(tree), 0)
        self.assertIsInstance(tree, dict)


