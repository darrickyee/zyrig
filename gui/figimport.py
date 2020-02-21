from .widgets import ButtonBasic
from PySide2 import QtWidgets as qw


act_init = qw.QAction(text="Initialize")
act_orient = qw.QAction(text="Orient Joints")
act_build = qw.QAction(text="Build")


def defaultFunc():
    pass


act_init.triggered.connect(defaultFunc)
act_orient.triggered.connect(defaultFunc)
act_build.triggered.connect(defaultFunc)

btn_init = ButtonBasic(act_init, context_menu=False)
btn_orient = ButtonBasic(act_orient, context_menu=False)
btn_build = ButtonBasic(act_build, context_menu=False)


class DialogFigureImport(qw.QDialog):

    def __init__(self, parent=None):
        super(DialogFigureImport, self).__init__(parent=parent)
        self.setWindowTitle("Import Figure")

        self.layout = qw.QVBoxLayout()

        for btn in [btn_init, btn_orient, btn_build]:
            self.layout.addWidget(btn)

        self.setLayout(self.layout)
