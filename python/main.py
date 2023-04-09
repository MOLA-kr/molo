import gazu.files

from molo import *


class Molo:
    def __init__(self) -> None:
        # self.logging = logging()
        self.auth = Auth()
        self.start()

        self.browser = TaskBrowser()
        self.selected_task = None
        self.print_browser()
        if not isinstance(self.selected_task, CompTask):
            print('아직 task가 선택되지 않았습니다.')
            return
        self.comments = self.selected_task.get_comments()
        self.print_selected_task_info()
        self.print_selected_task_output_files()
        self.print_selected_task_preview_urls()

    def print_selected_task_preview_urls(self):
        comp_tasks = self.browser.sorted_by_due_date
        for task in comp_tasks:
            comp_task = CompTask(task)
            print(comp_task.proj_name, comp_task.seq_name, comp_task.shot_name)
            # print(comp_task.shot.get('name'))
            print(comp_task.get_thumbnail_url())

        # self.print_selected_task_output_files()

    def print_selected_task_output_files(self):
        output_files = self.selected_task.latest_output_files()
        # info = ['id', 'output_type_id', 'path', 'revision', 'task_type_id', 'updated_at']
        print_align(output_files)
        # pprint(output_files)

        for i in output_files:
            # file dict 안의 'path' - 확장자 X
            # print(i.get('path'))
            # file 정보를 이용하여 확장자 연결
            path = construct_full_path(i)
            print(path)

    def print_selected_task_info(self):
        # print(f'proj: ', end='')
        # print_align(self.selected_task.proj)
        print(f'proj_name: {self.selected_task.proj_name}')
        print(f'seq_name: {self.selected_task.seq_name}')
        print(f'shot_name: {self.selected_task.shot_name}')

        print(f'proj_id: {self.selected_task.proj_id}')
        print(f'seq_id: {self.selected_task.seq_id}')
        print(f'shot_id: {self.selected_task.shot_id}')

        print(f'fps: {self.selected_task.fps}')
        print(f'ratio: {self.selected_task.ratio}')
        print(f'resolution: {self.selected_task.resolution}')

        print(f'frame_in: {self.selected_task.frame_in}')
        print(f'frame_out: {self.selected_task.frame_out}')

        print(f'task_status: {self.selected_task.task_status}')

        print(f'task_comment:{self.comments}')
        # pprint(self.selected_task._task)

    def print_browser(self):
        comp_tasks = self.browser.sorted_by_due_date
        info = ['name', 'project_name', 'entity_name', 'sequence_name',
                'task_type_name', 'task_status_name', 'due_date', 'priority']
        print_align(comp_tasks, 'task_type_name')
        selected_index = input('select task index>> ')
        if selected_index.isdigit():
            self.selected_task = CompTask(comp_tasks[int(selected_index)])

    def start(self):
        if self.auth.valid_host and self.auth.valid_user:
            print('자동 로그인에 성공했습니다.')

        while not self.auth.valid_host:
            try_host = input('host>> ')
            if self.auth.connect_host(try_host):
                print('host 연결에 성공했습니다.')
                break
            print('유효하지 않은 host 주소입니다. 다시 입력하세요')

        while not self.auth.valid_user:
            try_id = input('id>> ')
            try_pw = input('pw>> ')
            remember = False
            if input("remember me?[y/N]>> ") != 'y':
                remember = True
            if self.auth.log_in(try_id, try_pw):
                print('로그인에 성공했습니다.')
                if remember:
                    self.auth.save_setting()
                break
            else:
                print('로그인에 실패했습니다. 다시 입력하세요.')

        print(f'host: {self.auth.host}')
        print(f'user_name: {self.auth.user["full_name"]}')
        print(f'user_email: {self.auth.user["email"]}')


def main():
    mola = Molo()


if __name__ == '__main__':
    main()

