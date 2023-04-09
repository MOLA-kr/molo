import sys
import os

from datetime import datetime
from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui

import molo
from molo.PySide.molo_mvc import TaskBrowserModel, TaskTableModel, OutlineDelegate, get_pixmap
from molo.PySide.molo_user_frame import UserFrame
import molo.nuke_function as molo_nuke


class MoloWidget(QtWidgets.QWidget):
    """
    main application widget
    """

    def __init__(self) -> None:
        super().__init__()
        QtGui.QPixmapCache.setCacheLimit(500 * 1024)
        screen_resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.screen_width = screen_resolution.width()
        self.screen_height = screen_resolution.height()

        self.auth = molo.Auth()
        # self.event_test = gazu_event_test.ReloadEvents()

        self.login_ui = None
        self.host_ui = None
        self.ui = None
        self.user_frame = None

        self.browser = None
        self.browser_model = None
        self.browser_view = None
        self.table_model = None
        self.table_view = None
        self.selection_model = None
        self.horizontal_header = None
        self.loader = None

        self.comptasks = None
        self.todo_comptasks = None
        self.done_comptasks = None
        self.selected_comptask = None
        self.selected_outputfile_list = []
        self.current_nuke_id = None
        self.nuke_nodes = None
        self.load_mode = False

        if self.auth.valid_host and self.auth.valid_user:
            self.main_widget()
        elif not self.auth.valid_host:
            self.host_widget()
        else:
            self.login_widget()

    def init_ui(self, ui_path):
        """
        입력된 경로의 .ui 파일을 load한 후 화면에 표시

        Args:
            ui_path(str): 화면에 표시할 ui 파일의 경로

        Returns: load된 ui 객체
        """
        script_path = os.path.realpath(__file__)
        ui_path = os.path.join(os.path.dirname(script_path), ui_path)
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        ui = loader.load(ui_file)
        ui_file.close()

        w = int((self.screen_width - ui.width()) / 2)
        h = int((self.screen_height - ui.height()) / 2)
        ui.move(w, h)
        ui.show()
        return ui

    def host_widget(self):
        """
        host ui 설정
        """
        self.host_ui = self.init_ui('molo_host_widget.ui')
        self.host_ui.host_input.returnPressed.connect(self.run_connect_host)
        self.host_ui.connect_btn.clicked.connect(self.run_connect_host)

    def run_connect_host(self):
        """
        host ui의 connect_btn에 연결된 함수
        host_input에 입력된 host 주소를 이용해 host 연결을 시도
        """
        try_host = self.host_ui.host_input.text()
        try:
            self.auth.connect_host(try_host)
        except molo.exceptions.InvalidAuthError:
            pass
        if self.auth.valid_host:
            self.auth.save_setting()
            self.host_ui.close()
            self.login_widget()
        else:
            self.host_ui.error_msg.setText('Invalid address!')
            self.host_ui.error_msg.setStyleSheet("Color : orange")

    def login_widget(self):
        """
        로그인 ui 설정
        """
        self.login_ui = self.init_ui('molo_login_widget.ui')
        self.login_ui.user_pw_input.returnPressed.connect(self.run_log_in)
        self.login_ui.login_btn.clicked.connect(self.run_log_in)

    def run_log_in(self):
        """
        host ui의 login_btn에 연결된 함수
        user_id_input, user_pw_input에 입력된 계정 정보를 이용해 로그인 시도
        """
        try_id = self.login_ui.user_id_input.text()
        try_pw = self.login_ui.user_pw_input.text()
        try:
            self.auth.log_in(try_id, try_pw)
        except molo.exceptions.InvalidAuthError:
            pass
        if self.auth.valid_user:
            if self.login_ui.remember_check.isChecked():
                self.auth.save_setting()
            self.login_ui.close()
            self.main_widget()
        else:
            self.login_ui.error_msg.setText('Incorrect ID or password!')
            self.login_ui.error_msg.setStyleSheet("Color : orange")

    def main_widget(self):
        """
        메인 ui 설정
        """
        self.ui = self.init_ui('molo_main_widget.ui')
        self.ui.setWindowIcon(QtGui.QIcon('./icon/molo_icon.png'))
        self.ui.installEventFilter(self)

        # user 버튼 관련
        self.ui.btn_user.setText(molo.construct_initials(self.auth.user.get("full_name")))
        self.user_frame = UserFrame(self.ui, self.ui.btn_user)
        self.user_frame.user_name.setText(f'User: {self.auth.user.get("full_name")}')

        # TaskBrowser(My Task) 관련
        self.browser = molo.TaskBrowser()
        self.browser_model = TaskBrowserModel()
        self.browser_view = self.ui.browser_list
        self.browser_view.setModel(self.browser_model)
        self.browser_view.setViewMode(QtWidgets.QListView.IconMode)
        self.browser_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.browser_view.setIconSize(QtCore.QSize(150, 100))
        self.browser_view.setUniformItemSizes(True)
        self.browser_view.setGridSize(QtCore.QSize(180, 140))
        self.browser_view.setTextElideMode(QtCore.Qt.ElideNone)
        self.browser_view.setSpacing(6)
        self.browser_view.setMovement(QtWidgets.QListView.Static)

        # Table 관련
        self.table_view = self.ui.task_table
        self.table_model = TaskTableModel()
        self.table_view.setModel(self.table_model)
        self.selection_model = self.table_view.selectionModel()
        self.horizontal_header = self.table_view.horizontalHeader()
        self.table_model.selection_model = self.selection_model
        OutlineDelegate(self.table_view)
        self.adjust_header_size()

        # Loader
        self.loader = molo.Loader()

        # event 연결
        self.ui.btn_user.clicked.connect(self.toggle_user_frame)
        self.user_frame.logout_btn.clicked.connect(self.run_log_out)
        self.ui.btn_refresh_browser.clicked.connect(self.reload_comptasks)
        self.ui.checkBox_done.stateChanged.connect(self.filter_by_checkbox)
        self.ui.shot_tree.itemClicked.connect(self.filter_by_tree_item)
        self.ui.comboBox_sorted.currentIndexChanged.connect(self.sort_by_combobox)
        self.browser_view.selectionModel().selectionChanged.connect(
            lambda: self.update_selected_comptask(self.browser_model.comptasks[self.browser_view.currentIndex().row()]))
        self.ui.btn_task_type.clicked.connect(self.toggle_task_type)
        self.selection_model.selectionChanged.connect(self.update_selected_count)
        self.ui.btn_select_all.clicked.connect(self.select_all)
        self.ui.btn_deselect_all.clicked.connect(self.deselect_all)
        self.ui.btn_refresh_task_table.clicked.connect(self.update_node_status_icon)
        self.ui.btn_run_nuke.clicked.connect(self.run_nuke)

        # 화면에 표시될 정보들을 초기화
        self.reload_comptasks()
        self.identify_nuke_file()
        self.create_icon_guide()

    def adjust_header_size(self):
        """
        header 크기를 내용 길이에 맞춰서 변경
        """
        header = self.table_view.horizontalHeader()
        twidth = header.width()

        width = []
        for column in range(header.count()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents)
            width.append(header.sectionSize(column))

        wfactor = twidth / sum(width)
        for column in range(header.count()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Interactive)
            header.resizeSection(column, width[column] * wfactor)

    def toggle_user_frame(self):
        """
        btn_user 클릭하면 user_frame 활성화 전환
        """
        if self.user_frame.isVisible():
            self.user_frame.hide()
        else:
            self.user_frame.show()

    def toggle_task_type(self):
        # 선택 항목 리스트로 받아오기
        task_type_list = []
        selected = self.selection_model.selectedRows()
        selected_list = list(map(lambda x: x.row(), selected))
        for index in selected_list:
            task_type_name = self.table_model.task_data[index][0]
            task_type_list.append(task_type_name)
        # json파일 저장
        task_type_dict = {"task_type_list": task_type_list}
        t = molo.utils.TaskType(task_type_dict)
        t.save_task_type()

    def run_log_out(self):
        """
        log out 되고 login widget 활성화
        """
        self.auth.log_out()
        self.ui.close()
        self.login_widget()

    def reload_comptasks(self):
        """
        task status를 기준으로 각각 self.todo_comptasks, self.done_comptasks로 저장
        user의 comptask목록을 reload
        """
        self.todo_comptasks = []
        self.done_comptasks = []
        self.browser.refresh_comp_tasks()
        for i in self.browser.todo_comp_tasks:
            self.todo_comptasks.append(molo.CompTask(i))
        for i in self.browser.done_comp_tasks:
            self.done_comptasks.append(molo.CompTask(i))
        self.filter_by_checkbox()

        if not self.selected_comptask:
            return

        for row in range(self.browser_model.rowCount()):
            if self.selected_comptask.shot_id == self.browser_model.comptasks[row].shot_id:
                self.update_selected_comptask(self.browser_model.comptasks[row])

    def filter_by_checkbox(self):
        """
        self.ui.checkBox_done의 체크 유무에 따라
        self.done_comptasks도 self.comptasks에 포함
        """
        self.comptasks = self.todo_comptasks.copy()
        if self.ui.checkBox_done.isChecked():
            self.comptasks += self.done_comptasks

        self.update_shot_tree()

        self.browser_model.comptasks = self.comptasks
        self.update_shot_count()
        self.sort_by_combobox()
        self.browser_view.scrollToTop()

    def update_shot_tree(self):
        """
        user가 가지고 있는 task를 self.ui.shot_tree에 초기화 후 표시
        """
        self.ui.shot_tree.clear()
        user_item = QtWidgets.QTreeWidgetItem(self.ui.shot_tree)
        user_item.setText(0, self.auth.user.get("full_name"))
        info = molo.user_info_tree(self.sort_by_name(self.comptasks))
        for i in info:
            if not isinstance(i, str):
                continue
            proj_item = QtWidgets.QTreeWidgetItem(user_item)
            proj_item.setText(0, i)
            for j in info[i]:
                if not isinstance(j, str):
                    continue
                seq_item = QtWidgets.QTreeWidgetItem(proj_item)
                seq_item.setText(0, j)
                for k in info[i][j]:
                    if not isinstance(k, str):
                        continue
                    shot_item = QtWidgets.QTreeWidgetItem(seq_item)
                    shot_item.setText(0, k)
        self.ui.shot_tree.expandAll()

    def filter_by_tree_item(self, item):
        """
        shot_tree에서 클릭한 item의 부모를 찾아 선택한 item의 project, sequence, shot을 리스트에 저장
        Args:
            item: tree_widget에서 클릭한 item
        """
        result = []
        for i in range(4):
            if item:
                result.insert(0, item.text(0))
                item = item.parent()
                continue
            result.append(None)
        self.filter_by_entity(project=result[1], sequence=result[2], shot=result[3])

    def filter_by_entity(self, project=None, sequence=None, shot=None):
        """
        self.browser_model에 들어있는 task을 필터링하여 self.browser_model에 다시 적용
        Args:
            project: 필터링 할 프로젝트
            sequence: 필터링 할 시퀀스
            shot: 필터링 할 샷
        """
        filtered = []
        selected_comptask = None
        if project == sequence == shot is None:
            # filter 조건이 없는 경우 => 전체 선택
            filtered = self.comptasks
        else:
            # filter 조건이 있는 경우
            # self.comptasks(전체 task에 대한 CompTask 리스트)에 대해
            # for문을 돌면서 조건에 맞는 comptask 객체만 filtered에 추가
            for comptask in self.comptasks:
                if project and comptask.proj_name != project:
                    continue
                if sequence and comptask.seq_name != sequence:
                    continue
                if shot:
                    if comptask.shot_name == shot:
                        # shot까지 조건이 지정된 경우 => 해당 task를 바로 side에 표시
                        selected_comptask = comptask
                    else:
                        continue
                filtered.append(comptask)

        self.browser_model.comptasks = filtered
        self.update_shot_count()
        self.sort_by_combobox()
        if selected_comptask:
            self.update_selected_comptask(selected_comptask)

    def update_shot_count(self):
        """
        self.browser_model에 들어있는 data 개수
        """
        self.ui.label_shot_count.setText(
            f'Assigned Shot {self.browser_model.rowCount():>2d} / {len(self.comptasks):>2d}   ')

    def sort_by_combobox(self):
        """
        comboBox에서 선택한 정렬 기준을 받아와
        self.browser_model에 들어있는 data를 해당하는 기준에 따라 정렬 후 업데이트
        """
        # 1) comboBox에서 선택한 정렬 기준 가져오기
        selected_text = self.ui.comboBox_sorted.currentText()

        sorted_data = []
        if selected_text == "Name":
            sorted_data = self.sort_by_name(self.browser_model.comptasks)
        elif selected_text == "Due date":
            sorted_data = self.sort_by_criterion(self.browser_model.comptasks, 'due_date')
        elif selected_text == "Priority":
            sorted_data = self.sort_by_criterion(self.browser_model.comptasks, 'priority', True)

        # 2) self.browser_model에 들어있는 data를 해당하는 기준에 따라 정렬 후 업데이트
        self.browser_model.comptasks = sorted_data
        self.browser_view.update()

    @staticmethod
    def sort_by_criterion(shot_data, criterion, reverse=False):
        """
        self.browser_model data를 입력 받은 기준으로 정렬하고 리스트를 반환

        Args:
            shot_data: browser_model의 comptasks
            criterion: 정렬 기준
            reverse: 내림차순인지, 올림차순인지

        Returns: sorted_data(list)

        """
        sorted_data = sorted(shot_data,
                             key=lambda ct: (ct.task_dict.get(criterion) is None, ct.task_dict.get(criterion)),
                             reverse=reverse)
        return sorted_data

    @staticmethod
    def sort_by_name(shot_data):
        """
        self.browser_model data를 shot이름으로 정렬

        Args:
            shot_data: browser_model의 comptasks

        Returns: sorted_shot_data(list)

        """
        sorted_shot_data = sorted(shot_data, key=lambda ct: (ct.proj_name, ct.seq_name, ct.shot_name), reverse=False)
        return sorted_shot_data

    def update_selected_comptask(self, comptask):
        """
        입력된 task에 대해 mode(open 혹은 load)를 지정하고 side에 해당 정보 표시
        (썸네일, output file table, comments, info)

        Args:
            comptask: side에 표시하도록 선택한 CompTask 객체
        """
        self.selected_comptask = comptask
        self.update_load_mode()

        self.update_side_thumbnail()
        self.update_shot_data()
        self.update_table()
        self.update_comment_tree()

    def update_load_mode(self):
        """
        선택한 comptask가 현재 열려 있는 누크 파일과 같다면 load_mode True
        btn_run_nuke 버튼 이름 Load Selected Files로 변경
        그 외에는 load_mode False, btn_run_nuke 버튼 이름 Open Nuke Script로 변경
        """
        if self.selected_comptask and self.selected_comptask.task_dict.get('id') == self.current_nuke_id:
            self.load_mode = True
            self.table_model.load_mode = True
            self.ui.label_selected_count.setVisible(True)
            self.ui.btn_task_type.setVisible(True)
            self.ui.btn_select_all.setVisible(True)
            self.ui.btn_deselect_all.setVisible(True)
            self.ui.btn_refresh_task_table.setVisible(True)
            self.ui.btn_run_nuke.setText('Load Selected Files')
        else:
            self.load_mode = False
            self.table_model.load_mode = False
            self.ui.label_selected_count.setVisible(False)
            self.ui.btn_task_type.setVisible(False)
            self.ui.btn_select_all.setVisible(False)
            self.ui.btn_deselect_all.setVisible(False)
            self.ui.btn_refresh_task_table.setVisible(False)
            self.ui.btn_run_nuke.setText('Open Nuke Script')

    def update_side_thumbnail(self):
        """
        선택한 comptask의 pixmap을 label_thumbnail에 적용
        """
        pixmap = get_pixmap(self.selected_comptask)
        if pixmap:
            self.ui.label_thumbnail.adjustSize()
            self.ui.label_thumbnail.setPixmap(pixmap.scaled(300, 150, QtGui.Qt.KeepAspectRatio))

    def update_table(self):
        """
        load_mode일 때, table_data에 버전 상태 리스트에 추가
        table data 이름순으로 정렬, self.selection_model에 선택한 model들을 저장
        """
        self.table_model.task_data = self.insert_node_status()
        # task data sort
        self.horizontal_header.setSortIndicator(0, QtCore.Qt.AscendingOrder)
        self.table_model.sort(0, QtCore.Qt.AscendingOrder)

        if not self.load_mode:
            return

        for row in range(self.table_model.rowCount()):
            task_type_dict = molo.utils.TaskType(task_type_dict=None).load_task_type()
            self.auto_select_type = task_type_dict.get("task_type_list")
            if self.table_model.task_data[row][0] in self.auto_select_type:
                for column in range(self.table_model.columnCount()):
                    index = self.table_model.index(row, column)
                    self.selection_model.select(index, QtCore.QItemSelectionModel.Select)

    def insert_node_status(self):
        """
        현재 작업 중인 working file의 Node와 선택한 output file의 버전 정보를 비교한 리스트 반환.
        (노드 일치 여부 판별: 일치(녹색), 불일치(주황), 없음(빨강))

        Returns:
            list: 기존 output file info에 node 버전 일치 여부 정보를 추가한 list
        """
        output_files_info = self.selected_comptask.latest_output_files_info()
        if self.load_mode:
            for output_file in output_files_info:
                task_type_name = output_file[0]
                output_id = output_file[-2]

                node_id = self.nuke_nodes.get(task_type_name)
                if node_id is None:
                    # task_type에 해당하는 노드가 없는 경우(빨강)
                    output_file.insert(-2, 0)
                elif node_id == output_id:
                    # 해당 노드의 molo_id가 최신 output file의 id와 일치하는 경우(초록)
                    output_file.insert(-2, 2)
                else:
                    # 해당 노드의 molo_id가 최신 output file의 id와 일치하지 않는 경우(노랑)
                    output_file.insert(-2, 1)
        else:
            # load mode가 아닌 경우, icon 표시 X
            for output_file in output_files_info:
                output_file.insert(-2, 3)

        return output_files_info

    def update_comment_tree(self):
        """
        선택한 comptask의 comments들을 ui treeview에 표시
        """
        comments = self.selected_comptask.get_comments()
        comment_tree_view = self.ui.comment_tree
        comment_tree_model = QtGui.QStandardItemModel()
        old_format = '%Y-%m-%dT%H:%M:%S'
        new_format = '%Y/%m/%d %H:%M'

        for parent_item in comments:
            parent_string = \
                f"{parent_item.get('comm_name')} " \
                f"({datetime.strptime(parent_item.get('comm_date'), old_format).strftime(new_format)}) " \
                f"\n : {parent_item.get('comm_text')}"
            parent = QtGui.QStandardItem(parent_string)
            parent.setFlags(parent.flags() & ~QtCore.Qt.ItemIsEditable)
            comment_tree_model.appendRow(parent)

            for child_item in parent_item.get('replies', {}):
                child_string = \
                    f"{child_item.get('rep_name')} " \
                    f"({datetime.strptime(child_item.get('rep_date'), old_format).strftime(new_format)}) " \
                    f"\n : {child_item.get('rep_text')}"
                child = QtGui.QStandardItem(child_string)
                child.setFlags(child.flags() & ~QtCore.Qt.ItemIsEditable)
                parent.appendRow(child)

        comment_tree_view.setModel(comment_tree_model)
        comment_tree_view.expandAll()
        comment_tree_view.show()

    def update_shot_data(self):
        """
        선택한 task의 shot 정보들을 ui에 표시
        """
        comptask = self.selected_comptask
        self.ui.label_proj.setText(comptask.proj_name)
        self.ui.label_seq.setText(comptask.seq_name)
        self.ui.label_shot.setText(comptask.shot_name)
        self.ui.label_frame_in.setText(str(comptask.frame_in))
        self.ui.label_frame_out.setText(str(comptask.frame_out))
        self.ui.label_resolution.setText(comptask.resolution)
        self.ui.label_fps.setText(str(comptask.fps))
        self.ui.label_revision.setText(str(comptask.revision))

    def update_selected_count(self):
        """
        table data 선택 한 개수 표시
        """
        self.ui.label_selected_count.setText(f'Selected Files  '
                                             f'{len(self.selection_model.selectedRows())} / {self.table_model.rowCount()}  ')

    def select_all(self):
        """
        table data 전체 선택
        """
        model = self.table_model
        selection = QtCore.QItemSelection(model.index(0, 0), model.index(model.rowCount() - 1, model.columnCount() - 1))
        self.selection_model.select(selection, QtCore.QItemSelectionModel.Select)

    def deselect_all(self):
        """
        table data 전체 선택 해제
        """
        self.selection_model.clearSelection()

    def update_node_status_icon(self):
        """
        nuke node들의 최신 상태를 받아와 table_view에 적절한 icon을 표시
        변경된 node 정보를 반영해 icon 변경(table의 sort 유지)
        """
        sorting_column = self.horizontal_header.sortIndicatorSection()
        sorting_order = self.horizontal_header.sortIndicatorOrder()
        self.nuke_nodes = molo_nuke.nodes_data()
        self.table_model.task_data = self.insert_node_status()
        self.horizontal_header.setSortIndicator(sorting_column, sorting_order)
        self.table_model.sort(0, QtCore.Qt.AscendingOrder)
        self.table_model.sort(sorting_column, sorting_order)

    def run_nuke(self):
        """
        btn_run_nuke 클릭하면 해당 nuke파일이 열리거나,
        현재 파일로 아웃풋 파일들을 로드한다.
        """
        if self.load_mode:
            # 선택한 output file들에 대한 node들을 create or update
            create_path_dict, update_path_dict = self.get_outputfiles_path()
            molo_nuke.deselect_all_nodes()
            self.loader.create_nodes(create_path_dict)
            self.loader.update_nodes(update_path_dict)
            molo_nuke.focus_selected_node()
            self.update_node_status_icon()
            self.update_selected_count()
        else:
            if not self.selected_comptask:
                return

            # 해당 task의 working file을 생성하거나 open
            working_file = self.loader.open_nuke_working_file(self.selected_comptask)
            self.selected_comptask.last_comptask_revision = working_file
            self.identify_nuke_file()
            self.update_selected_comptask(self.selected_comptask)

            self.load_mode = True
            self.table_model.load_mode = True
            self.ui.label_selected_count.setVisible(True)
            self.ui.btn_select_all.setVisible(True)
            self.ui.btn_deselect_all.setVisible(True)
            self.ui.btn_refresh_task_table.setVisible(True)
            self.ui.btn_run_nuke.setText('Load Selected Files')

            self.update_node_status_icon()
            self.update_table()

            self.ui.showMinimized()
            self.ui.setWindowState(self.ui.windowState() and (not QtCore.Qt.WindowMinimized or QtCore.Qt.WindowActive))

    def get_outputfiles_path(self):
        """
        리스트를 받아서 아웃풋 파일의 path를 반환
        """
        selected = self.selection_model.selectedRows()
        selected_list = list(map(lambda x: x.row(), selected))

        create_path_dict = {}
        update_path_dict = {}
        for index in selected_list:
            # 선택한 요소들의 노드 반영 상태(빨노초)에 따라 작업 방식 변경
            node_status = self.table_model.task_data[index][-3]
            task_type_name = self.table_model.task_data[index][0]
            output_id = self.table_model.task_data[index][-2]
            output_path = self.table_model.task_data[index][-1]
            if node_status == 0:
                create_path_dict[task_type_name] = {output_id: output_path}
            elif node_status == 1:
                update_path_dict[task_type_name] = {output_id: output_path}
        return create_path_dict, update_path_dict

    def identify_nuke_file(self):
        """
        현재 열려 있는 누크 파일의 이름을 identify_nuke label에 적용하고,
        task broswer_view에 표시한다.
        """
        self.nuke_nodes = molo_nuke.nodes_data()
        path = molo_nuke.nuke_file_name()
        if not path:
            self.ui.identify_nuke.setText("Untitled")
        else:
            text = os.path.basename(path)
            self.ui.identify_nuke.setText(text)
            file_path = os.path.dirname(path)

            for row in range(self.browser_model.rowCount()):
                index = self.browser_model.index(row)
                files_path = self.browser_model.data(index, QtCore.Qt.AccessibleTextRole)

                if file_path in files_path:
                    current_nuke_task = self.browser_model.comptasks[row]
                    self.current_nuke_id = current_nuke_task.task_dict.get("id")
                    self.browser_view.setCurrentIndex(index)
                    break

        self.update_load_mode()

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if isinstance(event, QtGui.QResizeEvent):
            self.user_frame.adjust_position()
            return True
        return False

    def create_icon_guide(self):
        """
        QTableWidget 과 QLabel 을 사용하여 ui 에서 사용하는 icon 의 설명을 보여준다.
        """

        text = '**** ICON LEGEND ****'
        self.ui.icon_guide_title.setText(text)
        # self.ui.icon_guide_title.setFont(QtGui.QFont('Carlito', 11))

        item0 = QtWidgets.QTableWidgetItem()
        item1 = QtWidgets.QTableWidgetItem()
        item2 = QtWidgets.QTableWidgetItem()
        item3 = QtWidgets.QTableWidgetItem()
        item4 = QtWidgets.QTableWidgetItem()

        text0 = QtWidgets.QTableWidgetItem()
        text1 = QtWidgets.QTableWidgetItem()
        text2 = QtWidgets.QTableWidgetItem()
        text3 = QtWidgets.QTableWidgetItem()
        text4 = QtWidgets.QTableWidgetItem()
        text0.setFont(QtGui.QFont('Carlito', 9))
        text1.setFont(QtGui.QFont('Carlito', 9))
        text2.setFont(QtGui.QFont('Carlito', 9))
        text3.setFont(QtGui.QFont('Carlito', 9))
        text4.setFont(QtGui.QFont('Carlito', 9))

        item0.setText('◉ ')
        item1.setText('➡️ ')
        item0.setFont(QtGui.QFont('Cantarell', 13))
        item1.setFont(QtGui.QFont('Cantarell', 15))
        item2.setIcon(QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/None.png'))
        item3.setIcon(QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/update.png'))
        item4.setIcon(QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/latest.png'))

        text0.setText('The Compositing Task is Done')
        text1.setText('All Tasks are Done except Comp.')
        text2.setText('There are no matching node')
        text3.setText('Version needs to be updated')
        text4.setText('Current Version is the latest')

        self.ui.icon_guide.setItem(0, 0, item0)
        self.ui.icon_guide.setItem(1, 0, item1)
        self.ui.icon_guide.setItem(2, 0, item2)
        self.ui.icon_guide.setItem(3, 0, item3)
        self.ui.icon_guide.setItem(4, 0, item4)

        self.ui.icon_guide.setItem(0, 1, text0)
        self.ui.icon_guide.setItem(1, 1, text1)
        self.ui.icon_guide.setItem(2, 1, text2)
        self.ui.icon_guide.setItem(3, 1, text3)
        self.ui.icon_guide.setItem(4, 1, text4)

        self.ui.icon_guide.resizeColumnsToContents()


def main():
    global app
    try:
        app.ui.close()
    except:
        pass
    app = MoloWidget()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    myapp = QtWidgets.QApplication()
    main()
    sys.exit((myapp.exec_()))
