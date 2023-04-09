"""
특정 task(shot)에 대한 정보를 불러오기 위한 모듈
"""
import os
import gazu
from .utils import construct_full_path

from datetime import datetime


class CompTask:

    def __init__(self, task_dict) -> None:
        """
        입력된 task에 해당하는 shot으로부터 각종 정보를 추출

        Args:
            task_dict(dict{dict}):  객체로 만들고자 하는 shot task의 dict
            반드시 asset이 아닌, shot을 entity로 하는 task여야 함
        """
        if task_dict.get('entity_type_name') != 'Shot':
            raise Exception('shot을 위한 task가 아님')

        self._task_dict = task_dict

        self._task_status = gazu.task.get_task_status(self._task_dict.get('task_status_id')).get('name')
        self._shot_dict = gazu.shot.get_shot(self._task_dict.get('entity_id'))
        self._proj_dict = gazu.project.get_project(self.shot_dict.get('project_id'))

        self._proj_name = self.proj_dict.get('name')
        self._seq_name = self.shot_dict.get('sequence_name')
        self._shot_name = self.shot_dict.get('name')

        self._proj_id = self.proj_dict.get('id')
        self._seq_id = self.shot_dict.get('sequence_id')
        self._shot_id = self.shot_dict.get('id')

        self._fps = self.proj_dict.get('fps')
        self._ratio = self.proj_dict.get('ratio')
        self._resolution = self.proj_dict.get('resolution')

        self._frame_in = self.shot_dict.get('frame_in') or 0
        self._frame_out = self.shot_dict.get('frame_out') or 0

        self._revision = None

        self.file_tree = self.proj_dict.get('file_tree')
        self._filetree_pattern = None

        self._comments = gazu.task.all_comments_for_task(self._task_dict)

        self.thumbnail_image = self.get_thumbnail_url()
        self.last_comptask_revision = gazu.files.get_last_working_file_revision(self.task_dict) or {}


    @property
    def task_status(self):
        """
        Returns:
            dict: 선택한 task의 status 정보??????
        """
        return self._task_status

    @property
    def is_ready(self) -> bool:
        """
        Returns:
            bool: 해당 comp task의 shot에서 comp 이외의 다른 task들이 Done인지 여부

        다른 task들이 모두 Done 상태이면 True, 아니면 False
        """
        tasks = self.get_other_tasks_status()
        for i in tasks:
            if i.get('task_status_name') != 'Done':
                return False
        return True

    @property
    def is_done(self) -> bool:
        """
        Returns:
            bool: shot에서 compositing task가 Done인지 여부

        Done 상태이면 True, 아니면 False
        """
        if self.task_dict.get('task_status_name') == 'Done':
            return True
        return False

    @property
    def task_dict(self):
        return self._task_dict

    @property
    def shot_dict(self):
        return self._shot_dict

    @property
    def proj_dict(self):
        return self._proj_dict

    @property
    def proj_name(self):
        return self._proj_name

    @property
    def seq_name(self):
        return self._seq_name

    @property
    def shot_name(self):
        return self._shot_name

    @property
    def proj_id(self):
        return self._proj_id

    @property
    def seq_id(self):
        return self._seq_id

    @property
    def shot_id(self):
        return self._shot_id

    @property
    def fps(self):
        return self._fps

    @property
    def ratio(self):
        return self._ratio

    @property
    def resolution(self):
        return self._resolution

    @property
    def frame_in(self):
        return self._frame_in

    @property
    def frame_out(self):
        return self._frame_out

    @property
    def revision(self):
        """
        Nuke file revision
        """
        self._revision = self.last_comptask_revision.get("revision")
        if not self._revision:
            self._revision = "New!"
        return self._revision

    @property
    def comments(self):
        """
        Returns:
            dict: all comments for that comp task
        """
        return self._comments

    def get_other_tasks_status(self) -> list:
        """
        해당 comp task의 shot에서 comp 이외의 다른 task들의 task type과 task status를 반환

        Returns:
            list: task type과 status의 이름과 id를 포함하는 dict 리스트
        """
        res = []
        tasks = gazu.task.all_tasks_for_shot(self.shot_dict)
        for i in tasks:
            if i.get('task_type_name') == 'Compositing':
                continue
            temp = {'task_type_name': i.get('task_type_name'), 'task_type_id': i.get('task_type_id'),
                    'task_status_name': i.get('task_status_name'), 'task_status_id': i.get('task_status_id')}
            res.append(temp)
        return res

    def published_output_files(self, output_type=None, task_type=None):
        """
        all_output_files 결과에서 publish 태그 필터링

        json 파일에 output file의 id 저장
        output file id : project > seq > shot > dep
        """
        # 기능 추가 예정
        pass

    def latest_output_files_info(self, output_type=None, task_type=None) -> list:
        """
        해당 comp task의 shot을 위한 최신 output file들의 리스트를 반환(필요한 정보만 포함)

        Args:
            output_type(dict, optional): 리스트에 포함시키고자 하는 output file의 type
                EXR, FBX, ABC 등의 output_type dict
            task_type(dict, optional): 리스트에 포함시키고자 하는 output file의 task type
                Modeling, Rendering, FX, Plate, Matchmove 등의 task_type dict

        Returns:
            result (list): 해당 shot에 속한, 표시해야 할 정보로만 구성된 list
        """
        tasks = gazu.task.all_tasks_for_shot(self.shot_dict)
        files = gazu.files.get_last_output_files_for_entity(self.shot_dict, output_type=output_type,
                                                            task_type=task_type)
        result = []
        for task in tasks:
            temp_list = []

            # Compositing 외 task type
            task_type_name = task.get('task_type_name')
            if task_type_name == "Compositing":
                continue
            temp_list.append(task_type_name)

            # task status
            status_dict = gazu.task.get_task_status(task.get('task_status_id'))
            temp_list.append(status_dict.get('short_name', '').upper())

            # task의 output file이 있는지 찾기
            task_file = None
            for file in files:
                if file.get('task_type_id') == task.get('task_type_id'):
                    task_file = file
                    files.remove(file)
                    break

            if task_file:
                # output_file_revision
                temp_list.append(task_file.get('revision'))
                # output_file_extension
                output_type_id = task_file.get('output_type_id')
                temp_list.append(gazu.files.get_output_type(output_type_id).get('short_name', '').upper())
                # updated at
                temp_list.append(datetime.strptime(task_file.get('updated_at'), '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M'))
                # author_info
                authors_id = task.get('assignees', {})
                if not authors_id == []:
                    for author_id in authors_id:
                        author_name = gazu.person.get_person(author_id).get('full_name', {})
                        author_phone = gazu.person.get_person(author_id).get('phone', {})
                        author_email = gazu.person.get_person(author_id).get('email', {})
                        author_info = [author_name, author_phone, author_email]
                        temp_list.append(author_info)
                else:
                    author_name = ''
                    author_phone = ''
                    author_email = ''
                    author_info = [author_name, author_phone, author_email]
                    temp_list.append(author_info)
                # node 비교를 위한 output_file_id
                temp_list.append(task_file.get('id'))
                # output_file_path
                temp_list.append(construct_full_path(task_file))
            else:
                # output_file_revision
                temp_list.append('-')
                # output_file_extension
                temp_list.append('-')
                # updated at
                temp_list.append('-')
                # author_info
                temp_list.append('-')
                # node 비교를 위한 output_file_id
                temp_list.append('-')
                # output_file_path
                temp_list.append('-')

            result.append(temp_list)
        return result

    def latest_output_files(self, output_type=None, task_type=None) -> list:
        """
        해당 comp task의 shot을 위한 최신 output file들의 리스트를 반환

        Args:
            output_type(dict, optional): 리스트에 포함시키고자 하는 output file의 type
                EXR, FBX, ABC 등의 output_type dict
            task_type(dict, optional): 리스트에 포함시키고자 하는 output file의 task type
                Modeling, Rendering, FX, Plate, Matchmove 등의 task_type dict

        Returns:
            list(dict): 해당 shot에 속한 최신 플레이트 목록
        """
        return gazu.files.get_last_output_files_for_entity(self.shot_dict, output_type=output_type, task_type=task_type)

    def all_output_files(self, output_type=None, task_type=None) -> list:
        """
        해당 comp task의 shot을 위한 모든 output file들 반환

        Args:
            output_type(dict, optional): 리스트에 포함시키고자 하는 output file의 type
                EXR, FBX, ABC 등의 output_type dict
            task_type(dict, optional): 리스트에 포함시키고자 하는 output file의 task type
                Modeling, Rendering, FX, Plate, Matchmove 등의 task_type dict

        Returns:
            list(dict): 해당 shot에 속한 모든 플레이트 목록
        """
        return gazu.files.all_output_files_for_entity(self.shot_dict, output_type=output_type, task_type=task_type)

    def check_new_thing(self):
        """
        해당 comp task와 관련해서 변경 사항이 있는지를 True 또는 False로 반환
        """
        # 기능 추가 예정
        pass

    def get_thumbnail_url(self):
        """
        shot의 main thumbnail 받아 옴

        Returns:
            thumbnail의 url (str)
        """
        plate_task_type = gazu.task.get_task_type_by_name('Plate')
        plate_task = gazu.task.get_task_by_entity(self.shot_dict, plate_task_type)
        preview_file = gazu.files.get_all_preview_files_for_task(plate_task)
        if not preview_file:
            return
        url = gazu.files.get_preview_file_url(preview_file[-1])
        name, ext = os.path.splitext(url)
        if ext == '.mp4':
            url = name + '.png'
        return url

    def get_thumbnail_data(self):
        """
        shot의 main thumbnail 받아옴

        Returns:
            thumbnail url를 이용해 받아온 image data (bytes)
        """
        return gazu.client.get_file_data_from_url(self.thumbnail_image)

    def get_comments(self):
        """
        해당 comp task의 모든 comment정보와 해당 comment의 모든 replies정보를 반환한다.

        Returns:
            list[dict{list[dict]}]: 해당 comp task의 모든 comment(dict)와 comment의 id, 작성자, 작성시간, comment, replies(list)
            그리고 해당 comment의 모든 replies(dict)의 id, 작성자, 작성시간, replies comment

        """
        comments_list = []

        for comm in self._comments:
            comm_dict = {'comm_id': comm.get('id'),
                         'comm_name': comm.get('person').get('first_name') + ' ' + comm.get('person').get('last_name'),
                         'comm_date': comm.get('created_at'),
                         'comm_text': comm.get('text'),
                         'replies': []
                         }
            comments_list.append(comm_dict)

            for rep in comm.get('replies'):
                rep_dict = {'rep_id': rep.get('id'),
                            'rep_name': gazu.person.get_person(rep.get('person_id')).get('full_name'),
                            'rep_date': rep.get('date'),
                            'rep_text': rep.get('text')
                            }
                comments_list[-1]['replies'].append(rep_dict)

        return comments_list