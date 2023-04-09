import sys
import os

from datetime import datetime
from PySide2 import QtWidgets, QtCore, QtUiTools, QtGui

import molo
from molo.PySide.molo_mvc import TaskBrowserModel, TaskTableModel, OutlineDelegate, get_pixmap
import molo.nuke_function as molo_nuke


class MoloWidget(QtWidgets.QWidget):

    def __init__(self) -> None:
        super().__init__()
        QtGui.QPixmapCache.setCacheLimit(500 * 1024)
        screen_resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.screen_width = screen_resolution.width()
        self.screen_height = screen_resolution.height()

        self.auth = molo.Auth()

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

        if not self.auth.valid_user:
            self.login_widget()
        else:
            self.main_widget()

    def login_widget(self):
        """
        로그인 ui 설정
        """
        self.login_ui = self.init_ui_panel('molo_login_widget.ui')
        self.login_ui.show()
        self.login_ui.user_pw_input.returnPressed.connect(self.run_log_in_panel)
        self.login_ui.login_btn.clicked.connect(self.run_log_in_panel)

    def run_log_in_panel(self):
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

    def init_ui_panel(self, ui_path):
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
        return ui

    @staticmethod
    def init_ui(self, ui_path):
        script_path = os.path.realpath(__file__)
        ui_path = os.path.join(os.path.dirname(script_path), ui_path)
        ui_file = QtCore.QFile(ui_path)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        loader.load(ui_file, self)
        ui_file.close()
        self.move(0, 0)

        # find child
        self.main_layout = self.findChild(QtWidgets.QWidget, 'Molo')
        self.browser_view = self.findChild(QtWidgets.QListView, 'browser_list')
        self.btn_user = self.findChild(QtWidgets.QPushButton, 'btn_user')
        self.table_view = self.findChild(QtWidgets.QTableView, 'task_table')
        self.btn_refresh_browser = self.findChild(QtWidgets.QPushButton, 'btn_refresh_browser')
        self.checkBox_done = self.findChild(QtWidgets.QCheckBox, 'checkBox_done')
        self.shot_tree = self.findChild(QtWidgets.QTreeWidget, 'shot_tree')
        self.comboBox_sorted = self.findChild(QtWidgets.QComboBox, 'comboBox_sorted')
        self.btn_select_all = self.findChild(QtWidgets.QPushButton, 'btn_select_all')
        self.btn_deselect_all = self.findChild(QtWidgets.QPushButton, 'btn_deselect_all')
        self.btn_run_nuke = self.findChild(QtWidgets.QPushButton, 'btn_run_nuke')
        self.btn_refresh_task_table = self.findChild(QtWidgets.QPushButton, 'btn_refresh_task_table')
        self.label_shot_count = self.findChild(QtWidgets.QLabel, 'label_shot_count')
        self.label_selected_count = self.findChild(QtWidgets.QLabel, 'label_selected_count')
        self.label_thumbnail = self.findChild(QtWidgets.QLabel, 'label_thumbnail')
        self.comment_tree = self.findChild(QtWidgets.QTreeView, 'comment_tree')
        self.label_proj = self.findChild(QtWidgets.QLabel, 'label_proj')
        self.label_seq = self.findChild(QtWidgets.QLabel, 'label_seq')
        self.label_shot = self.findChild(QtWidgets.QLabel, 'label_shot')
        self.label_frame_in = self.findChild(QtWidgets.QLabel, 'label_frame_in')
        self.label_frame_out = self.findChild(QtWidgets.QLabel, 'label_frame_out')
        self.label_resolution = self.findChild(QtWidgets.QLabel, 'label_resolution')
        self.label_fps = self.findChild(QtWidgets.QLabel, 'label_fps')
        self.label_revision = self.findChild(QtWidgets.QLabel, 'label_revision')
        self.identify_nuke = self.findChild(QtWidgets.QLabel, 'identify_nuke')
        self.icon_guide_title = self.findChild(QtWidgets.QLabel, 'icon_guide_title')
        self.icon_guide = self.findChild(QtWidgets.QTableWidget, 'icon_guide')
        self.btn_task_type = self.findChild(QtWidgets.QPushButton, 'btn_task_type')
        self.label_sorted = self.findChild(QtWidgets.QLabel, 'label_sorted')

    def main_widget(self):
        """
        메인 ui 설정
        """
        self.init_ui(self, './molo_main_widget.ui')
        self.installEventFilter(self)

        self.main_layout.setFixedSize(1230, 888)
        self.browser_view.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.browser_view.setFixedWidth(280)
        self.table_view.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.table_view.setMinimumWidth(300)
        self.btn_run_nuke.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.btn_run_nuke.setMinimumSize(280, 60)
        self.comboBox_sorted.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.comboBox_sorted.setFixedWidth(80)
        self.comboBox_sorted.setFont(QtGui.QFont('Carlito', 10))
        self.checkBox_done.setFont(QtGui.QFont('Carlito', 8))
        self.label_sorted.setFont(QtGui.QFont('Carlito', 8))
        self.label_sorted.setFixedWidth(80)
        self.label_sorted.setLayoutDirection(QtGui.Qt.LeftToRight)
        self.checkBox_done.setFixedWidth(120)
        self.btn_task_type.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.btn_task_type.setMinimumSize(130, 30)
        self.btn_user.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.btn_user.setMinimumSize(130, 27)


        # user 버튼 관련
        self.btn_user.setText(molo.construct_initials(self.auth.user.get("full_name")))

        # TaskBrowser(My Task) 관련
        self.browser = molo.TaskBrowser()
        self.browser_model = TaskBrowserModel()
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
        self.btn_refresh_browser.clicked.connect(self.reload_comptasks)
        self.checkBox_done.stateChanged.connect(self.filter_by_checkbox)
        self.shot_tree.itemClicked.connect(self.filter_by_tree_item)
        self.comboBox_sorted.currentIndexChanged.connect(self.sort_by_combobox)
        self.browser_view.selectionModel().selectionChanged.connect(
            lambda: self.update_selected_comptask(self.browser_model.comptasks[self.browser_view.currentIndex().row()]))
        self.btn_task_type.clicked.connect(self.toggle_task_type)
        self.selection_model.selectionChanged.connect(self.update_selected_count)
        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_deselect_all.clicked.connect(self.deselect_all)
        self.btn_refresh_task_table.clicked.connect(self.update_node_status_icon)
        self.btn_run_nuke.clicked.connect(self.run_nuke)

        self.reload_comptasks()
        self.identify_nuke_file()
        self.create_icon_guide()

    def adjust_header_size(self):
        """
        header size를 내용 길이에 맞추어 변경
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
        if self.checkBox_done.isChecked():
            self.comptasks += self.done_comptasks

        self.update_shot_tree()

        self.browser_model.comptasks = self.comptasks
        self.update_shot_count()
        self.sort_by_combobox()
        self.browser_view.scrollToTop()

    def update_shot_tree(self):
        """
        user가 가지고 있는 task를 self.ui.shot_tree 초기화 후 표시
        """
        self.shot_tree.clear()
        user_item = QtWidgets.QTreeWidgetItem(self.shot_tree)
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
        self.shot_tree.expandAll()

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
        self.label_shot_count.setText(
            f'Assigned Shot {self.browser_model.rowCount():>2d} / {len(self.comptasks):>2d}   ')

    def sort_by_combobox(self):
        """
         comboBox에서 선택한 정렬 기준을 받아와
         self.browser_model에 들어있는 data를 해당하는 기준에 따라 정렬 후 업데이트
         """
        # 1) comboBox에서 선택한 정렬 기준 가져오기
        selected_text = self.comboBox_sorted.currentText()

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
            self.label_selected_count.setVisible(True)
            self.btn_select_all.setVisible(True)
            self.btn_deselect_all.setVisible(True)
            self.btn_task_type.setVisible(True)
            self.btn_refresh_task_table.setVisible(True)
            self.btn_run_nuke.setText('Load Selected Files')
        else:
            self.load_mode = False
            self.table_model.load_mode = False
            self.label_selected_count.setVisible(False)
            self.btn_select_all.setVisible(False)
            self.btn_deselect_all.setVisible(False)
            self.btn_task_type.setVisible(False)
            self.btn_refresh_task_table.setVisible(False)
            self.btn_run_nuke.setText('Open Nuke Script')

    def update_side_thumbnail(self):
        """
        browser_model에 저장된 선택한 comptask의 pixmap을 적용
        """
        pixmap = get_pixmap(self.selected_comptask)
        if pixmap:
            self.label_thumbnail.adjustSize()
            self.label_thumbnail.setPixmap(pixmap.scaled(300, 150, QtGui.Qt.KeepAspectRatio))

    def update_table(self):
        """
        load_mode일 때, table_data에 버전 상태 리스트에 추가
        table data 이름순으로 정렬, self.selection_model에 선택한 model들을 저장
        """
        self.table_model.task_data = self.insert_node_status()
        # task data sort
        self.horizontal_header.setSortIndicator(0, QtCore.Qt.AscendingOrder)
        self.table_model.sort(0, QtCore.Qt.AscendingOrder)
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
                elif node_id in output_id:
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
        comment_tree_view = self.comment_tree
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
        self.label_proj.setText(comptask.proj_name)
        self.label_seq.setText(comptask.seq_name)
        self.label_shot.setText(comptask.shot_name)
        self.label_frame_in.setText(str(comptask.frame_in))
        self.label_frame_out.setText(str(comptask.frame_out))
        self.label_resolution.setText(comptask.resolution)
        self.label_fps.setText(str(comptask.fps))
        self.label_revision.setText(str(comptask.revision))

    def update_selected_count(self):
        """
        table data 선택 한 개수 표시
        """
        self.label_selected_count.setText(f'Selected Files  '
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
            self.loader.create_nodes(create_path_dict)
            self.loader.update_nodes(update_path_dict)
            molo_nuke.focus_selected_node()
            self.update_node_status_icon()
            self.update_selected_count()
        else:
            # 해당 task의 working file을 생성하거나 open
            self.loader.open_nuke_working_file(self.selected_comptask)
            self.identify_nuke_file()
            self.reload_comptasks()

            self.load_mode = True
            self.table_model.load_mode = True
            self.label_selected_count.setVisible(True)
            self.btn_select_all.setVisible(True)
            self.btn_deselect_all.setVisible(True)
            self.btn_refresh_task_table.setVisible(True)
            self.btn_run_nuke.setText('Load Selected Files')

            self.update_node_status_icon()
            self.update_table()

            self.showMinimized()
            self.setWindowState(self.windowState() and (not QtCore.Qt.WindowMinimized or QtCore.Qt.WindowActive))

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
            situation = self.table_model.task_data[index][-3]
            task_type_name = self.table_model.task_data[index][0]
            output_id = self.table_model.task_data[index][-2]
            output_path = self.table_model.task_data[index][-1]
            if situation == 0:
                create_path_dict[task_type_name] = {output_id: output_path}
            elif situation == 1:
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
            self.identify_nuke.setText("Untitled")
        else:
            text = os.path.basename(path)
            self.identify_nuke.setText(text)
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

    def create_icon_guide(self):
        """
        QTableWidget 과 QLabel 을 사용하여 ui 에서 사용하는 icon 의 설명을 보여준다.
        """
        text = '***** ICON LEGEND *****'
        self.icon_guide_title.setText(text)
        # self.icon_guide_title.setFont(QtGui.QFont('Carlito', 11))

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
        text0.setFont(QtGui.QFont('Carlito', 8))
        text1.setFont(QtGui.QFont('Carlito', 8))
        text2.setFont(QtGui.QFont('Carlito', 8))
        text3.setFont(QtGui.QFont('Carlito', 8))
        text4.setFont(QtGui.QFont('Carlito', 8))

        item0.setText('◉ ')
        item1.setText('➡️ ')
        item0.setFont(QtGui.QFont('Cantarell', 13))
        item1.setFont(QtGui.QFont('Cantarell', 15))
        item2.setIcon(QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/None.png'))
        item3.setIcon(QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/update.png'))
        item4.setIcon(QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/latest.png'))

        text0.setText('The Compositing Task is Done')
        text1.setText('All the Tasks are Done except Comp.')
        text2.setText('There are no matching node')
        text3.setText('Version needs to be updated')
        text4.setText('Current Version is the latest')

        self.icon_guide.setItem(0, 0, item0)
        self.icon_guide.setItem(1, 0, item1)
        self.icon_guide.setItem(2, 0, item2)
        self.icon_guide.setItem(3, 0, item3)
        self.icon_guide.setItem(4, 0, item4)

        self.icon_guide.setItem(0, 1, text0)
        self.icon_guide.setItem(1, 1, text1)
        self.icon_guide.setItem(2, 1, text2)
        self.icon_guide.setItem(3, 1, text3)
        self.icon_guide.setItem(4, 1, text4)

        self.icon_guide.resizeColumnsToContents()


def main():
    global app
    try:
        app.close()
    except:
        pass
    app = MoloWidget()
    app.show()

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    myapp = QtWidgets.QApplication()
    main()
    sys.exit((myapp.exec_()))
