from PySide2 import QtWidgets, QtCore, QtGui


class UserFrame(QtWidgets.QFrame):
    """
    btn_user를 클릭하면 표시되는, user info 표시 및 로그아웃 버튼 프레임
    """

    def __init__(self, parent, reference_object):
        super().__init__(parent=parent)
        self.setObjectName('user_frame')
        self.setStyleSheet('QFrame#user_frame {color: #b1b1b1; '
                           'background-color: #323232; '
                           'border-radius: 5px;'
                           'border: 2px solid #eead53;'
                           '}'
                           'QPushButton:hover {border-style: outset;'
                           'border-radius: 5px;'
                           'border: 3px solid #eead53;}')
        self.setAutoFillBackground(True)

        font1 = QtGui.QFont()
        font1.setFamily(u"Carlito")
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)

        self.user_name = QtWidgets.QLabel(self)
        self.user_name.setObjectName('user_name')
        self.user_name.setGeometry(QtCore.QRect(15, 10, 170, 20))
        self.user_name.setFont(font1)

        self.logout_btn = QtWidgets.QPushButton(self)
        self.logout_btn.setObjectName('logout_btn')
        self.logout_btn.setGeometry(QtCore.QRect(92, 60, 100, 30))
        self.logout_btn.setText('Log Out')
        self.logout_btn.setFont(font1)

        self.reference_object = reference_object
        self.adjust_position()

    def show(self) -> None:
        super().show()
        self.adjust_position()

    def adjust_position(self):
        """
        ui의 크기가 변해도 user frame 잘 보이도록 위치 세팅
        """
        x = self.reference_object.geometry().x() + self.reference_object.geometry().width() - self.geometry().width()
        y = self.reference_object.geometry().y() + self.reference_object.geometry().height() + 10
        self.setGeometry(QtCore.QRect(x, y, 200, 100))
