from PySide2 import QtWidgets as qw, QtCore as qc


class ButtonBasic(qw.QToolButton):

    def __init__(self, default_action, middle_action=None, parent=None, context_menu=True):
        super(ButtonBasic, self).__init__(parent=parent)

        self.setDefaultAction(default_action)

        self.middle_action = middle_action

        if context_menu:
            self.setContextMenuPolicy(qc.Qt.ActionsContextMenu)

    def mousePressEvent(self, mouse_event):
        if (mouse_event.button() == qc.Qt.MidButton) and self.middle_action:
            self.middle_action.trigger()
            return

        return(super(ButtonBasic, self).mousePressEvent(mouse_event))


class ButtonSelectableAction(ButtonBasic):

    def __init__(self, action_list, middle_action=None, parent=None):
        self.action_list = action_list

        super(ButtonSelectableAction, self).__init__(
            default_action=action_list[0], middle_action=middle_action, parent=parent, context_menu=False)

        self.custom_menu = qw.QMenu(parent=self)
        self.action_group = qw.QActionGroup(self)
        for action in self.action_list:
            action.setCheckable(True)
            self.custom_menu.addAction(action)
            self.action_group.addAction(action)

        self.action_list[0].setChecked(True)

        self.setContextMenuPolicy(qc.Qt.CustomContextMenu)
        self.action_group.triggered[qw.QAction].connect(self.actionTriggered)

    def showContextMenu(self):
        self.custom_menu.exec_()

    def actionTriggered(self, action):
        self.removeAction(self.defaultAction())
        self.setDefaultAction(action)
        action.setChecked(True)
        self.setMenu(None)

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == qc.Qt.RightButton:
            self.custom_menu.exec_(mouse_event.globalPos())
            return

        return(super(ButtonSelectableAction, self).mousePressEvent(mouse_event))
