import sys
from PySide2 import QtWidgets as qw, QtCore as qc
from widgets import ButtonSelectableAction


def func1():
    print('This is function 1.')


def func2():
    print('Another function is this.')


def func3():
    print('Third function.')





def main():
    myapp = qw.QApplication(sys.argv)

    #############################
    act1 = qw.QAction(text='Action 1!')
    act1.triggered.connect(func1)
    act2 = qw.QAction(text='2nd Action!')
    act2.triggered.connect(func2)
    act3 = qw.QAction(text='Third!')
    act3.triggered.connect(func3)


    mybut = ButtonSelectableAction([act1, act2, act3])

    ##################################
    myd = qw.QDialog()
    lo = qw.QHBoxLayout()
    lo.addWidget(mybut)
    myd.setLayout(lo)

    myd.show()

    sys.exit(myapp.exec_())


main()

print('Done')
