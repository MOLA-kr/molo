from PySide2 import QtWidgets, QtCore, QtGui
from datetime import datetime


def get_pixmap(comptask):
    key = comptask.thumbnail_image
    pixmap = QtGui.QPixmap()

    if not QtGui.QPixmapCache.find(key, pixmap):
        if key:
            url_image = comptask.get_thumbnail_data()
            pixmap.loadFromData(url_image)
        else:
            default_image = '/home/rapa/git/mola/python/molo/PySide/icon/default_thumbnail_image.png'
            pixmap.load(default_image)
        QtGui.QPixmapCache.insert(key, pixmap)
    return pixmap


class OutlineDelegate(QtWidgets.QItemDelegate):
    """
    해당 delegate는 QTableView 또는 QTreeView 에서 선택된 item 의 테두리를 그리는 역할을 한다.

    Attributes:
        margin (int): 셀 상단과 테두리 사이의 거리
        radius (int): 둥근 모서리의 반
        border_color (QColor): 테두리 색상
        border_width (int): 테두리 너비

    Args:
        parent (QObject): delegate의 parent 객체
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.margin = 2
        self.radius = 10
        self.border_color = QtGui.QColor(238, 173, 83)
        self.border_width = 2

        parent.setItemDelegate(self)

    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        """
        테두리를 포함한 item의 size hint를 반환한다.
        """
        size = super().sizeHint(option, index)
        size = size.grownBy(QtCore.QMargins(0, self.margin, 0, self.margin))
        return size

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        """
        item이 선택되었을 때 item에 테두리를 그린다.
        """
        painter.save()
        painter.setRenderHint(painter.Antialiasing)

        # Painter에 clipping rect 을 설정하여 테두리 밖에 그리는 것을 방지
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        # 테두리를 고려하여 option.rect 을 조정한 뒤, 원래의 paint 메서드 호출
        option.rect.adjust(0, self.margin, 0, -self.margin)
        super().paint(painter, option, index)

        if option.state & QtWidgets.QStyle.State_Selected:
            pen = painter.pen()
            pen.setColor(self.border_color)
            pen.setWidth(self.border_width)
            painter.setPen(pen)

            # 첫번째 혹은 마지막 열에 있는 item 의 테두리는 둥근 모서리 사각형, 나머지는 직사각형
            if index.column() == 0:
                rect = option.rect.adjusted(self.border_width, 0, self.radius + self.border_width, 0)
                painter.drawRoundedRect(rect, self.radius, self.radius)
                painter.setPen(index.data(QtCore.Qt.TextColorRole))
                painter.drawText(option.rect, QtCore.Qt.AlignCenter, ' ' + index.data(QtCore.Qt.AccessibleTextRole))
            elif index.column() == index.model().columnCount(index.parent()) - 1:
                rect = option.rect.adjusted(-self.radius - self.border_width, 0, -self.border_width, 0)
                painter.drawRoundedRect(rect, self.radius, self.radius)
            else:
                rect = option.rect.adjusted(-self.border_width, 0, self.border_width, 0)
                painter.drawRect(rect)
        painter.restore()


class TaskBrowserModel(QtCore.QAbstractListModel):
    """
    TaskBrowserModel with model class
    Compositor에게 할당된 Task를 보여줌
    """
    def __init__(self, *args, comptasks=None, **kwargs):
        super(TaskBrowserModel, self).__init__(*args, **kwargs)
        self.comptasks = comptasks or []
        self.pixmaps = {}

        self.proirity_text = {
            0: 'Normal',
            1: '!High!',
            2: '!!Very High!!',
            3: '!!!Emergency!!!'
        }

    @property
    def comptasks(self):
        return self._comptasks

    @comptasks.setter
    def comptasks(self, value):
        self.beginResetModel()
        self._comptasks = value
        self.endResetModel()

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        """
        task를 status에 따라 표시, tooltip으로 duedate, priority 표시
        """
        if role == QtCore.Qt.DisplayRole:
            text_icon = ''
            if self.comptasks[index.row()].is_done:
                text_icon = '◉ '
            elif self.comptasks[index.row()].is_ready:
                text_icon = '➡️ '
            text = f'{text_icon}{self.comptasks[index.row()].proj_name} / {self.comptasks[index.row()].seq_name}' \
                   f' / {self.comptasks[index.row()].shot_name}'
            return text

        elif role == QtCore.Qt.TextColorRole:
            if self.comptasks[index.row()].is_ready:
                return QtGui.QColor(238, 173, 83)
            elif self.comptasks[index.row()].is_done:
                return QtGui.QColor(150, 105, 0)

        elif role == QtCore.Qt.DecorationRole:
            # pixmap = self.get_pixmap(self.comptasks[index.row()])
            pixmap = get_pixmap(self.comptasks[index.row()])
            icon = QtGui.QIcon(pixmap)
            return icon

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        elif role == QtCore.Qt.AccessibleTextRole:
            return self._comptasks[index.row()].last_comptask_revision.get('path') or ''

        elif role == QtCore.Qt.ToolTipRole:
            task_dict = self.comptasks[index.row()].task_dict
            due_date = datetime.strptime(task_dict.get('due_date') or '9999-12-21T23:59:59',
                                         '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M')
            priority = self.proirity_text[task_dict.get('priority')]
            text = f'due date: {due_date}\npriority: {priority}'
            return text
        return None

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return len(self.comptasks)


class TaskTableModel(QtCore.QAbstractTableModel):
    """
    Table Model : Compositor가 불러올 다른 Task의 output_file과 관련된 Task_data를 보여줌
    """

    def __init__(self, task_data=None):
        super().__init__()
        self.header_title = ["Task Type", "Status", "Ver", "Ext", "Updated At"]
        self._task_data = task_data or []
        self.load_mode = False
        self.selection_model = None

        self.color_dict = {
            "Storyboard": QtGui.QColor(0, 255, 0),
            "Layout": QtGui.QColor("cyan"),
            "Animation": QtGui.QColor("red"),
            "Lighting": QtGui.QColor(255, 255, 0),
            "FX": QtGui.QColor(153, 153, 255),
            "Rendering": QtGui.QColor("magenta"),
            "Plate": QtGui.QColor(255, 102, 0),
            "Matchmove": QtGui.QColor(159, 255, 158),
            "Camera": QtGui.QColor(255, 153, 204),
        }

    @property
    def task_data(self):
        return self._task_data

    @task_data.setter
    def task_data(self, value):
        self.beginResetModel()
        self._task_data = value
        self.endResetModel()

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole):
        """
        task_data, task_author_info, version, icon 표시
        """
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                if self.selection_model.isSelected(index):
                    return ''
            return self._task_data[index.row()][index.column()]

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        elif role == QtCore.Qt.BackgroundColorRole:
            if self._task_data[index.row()][-3] == 2 or self._task_data[index.row()][2] == '-':
                return QtGui.QColor(0, 0, 0, 100)

        elif role == QtCore.Qt.TextColorRole and index.column() == 0:
            task_type = self._task_data[index.row()][index.column()]
            if task_type in self.color_dict:
                return self.color_dict[task_type]

        # task_author_info
        elif role == QtCore.Qt.ToolTipRole:
            author_info = self._task_data[index.row()][-4]
            if author_info == '-':
                return 'No Data'
            text = f'author:  {author_info[0]}\nphone:  {author_info[1]}\nemail:  {author_info[2]}'
            return text

        # Ver. (node_status) icon 지정
        elif role == QtCore.Qt.DecorationRole and index.column() == 2 and self._task_data[index.row()][2] != '-':
            if self._task_data[index.row()][-3] == 0:
                return QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/None.png')
            if self._task_data[index.row()][-3] == 1:
                return QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/update.png')
            if self._task_data[index.row()][-3] == 2:
                return QtGui.QIcon('/home/rapa/git/mola/python/molo/PySide/icon/latest.png')
            return None
        elif role == QtCore.Qt.AccessibleTextRole:
            return self._task_data[index.row()][index.column()]

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()):
        """
        task_data에 따른 row의 length
        """
        return len(self._task_data)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()):
        """
        header_title에 따른 column의 length
        """
        return len(self.header_title)

    def headerData(self, column: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        """
        section is the index of the column/row
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header_title[column]

            return ""

    def flags(self, index: QtCore.QModelIndex):
        flags = super().flags(index)
        if self._task_data[index.row()][2] == '-':
            flags &= ~QtCore.Qt.ItemIsSelectable  # 선택 불가능
        elif self.load_mode and self._task_data[index.row()][-3] != 2:
            flags |= QtCore.Qt.ItemIsSelectable  # 선택 가능
        else:
            flags &= ~QtCore.Qt.ItemIsSelectable  # 선택 불가능
        return flags

    def sort(self, column: int, order: QtCore.Qt.SortOrder = QtCore.Qt.AscendingOrder):
        """
        column에 따라 표 정렬
        """
        self._task_data = sorted(self._task_data, key=lambda x: str(x[column]) or "")
        if order == QtCore.Qt.DescendingOrder:
            self._task_data.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))
