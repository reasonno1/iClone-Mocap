import sys, script
import PySide2
from PySide2 import QtGui, QtCore, QtWidgets



class rl_mapping_widget(PySide2.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(rl_mapping_widget, self).__init__(parent=parent)

    def closeEvent(self, event):
        try:
            script.EndFacePuppetKey(0)
        except:
            pass
        can_exit = True

        if can_exit:
            event.accept()  # let the window close
        else:
            event.ignore()