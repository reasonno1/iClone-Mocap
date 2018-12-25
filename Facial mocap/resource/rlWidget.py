import sys, scriptEvent
import PySide2
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtWidgets import QApplication

def debugMsg(_str):
    _text = str(_str)
    info_dialog = PySide2.QtWidgets.QMessageBox()
    info_dialog.setWindowTitle('Debug Window')
    info_dialog.setText(_text)
    info_dialog.exec_()

class rlWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(rlWidget, self).__init__(parent=parent)
        self.relatedWidgetList = []
        self.mapping_ui = None
        
    def mouseDoubleClickEvent(self, event):
        super(rlWidget, self).mouseDoubleClickEvent(event)

    def setRelatedWidget(self, widget):
        self.relatedWidgetList.append(widget)

    def hideEvent(self,event):
        super(rlWidget, self).hideEvent(event)

        self.device.stop()
        scriptEvent.StopTimer()
        
        for i in range(len(self.relatedWidgetList)):
            self.relatedWidgetList[i].hide()

    def init_pos(self):
        screen_resolution = QApplication.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.move(width-650, 10)

    def setDevice(self, device):
        self.device = device

    def closeEvent(self, event):
        can_exit = True
        if can_exit:
            mappingui_on = False
            event.accept()  # let the window close
        else:
            event.ignore()
        for w in self.relatedWidgetList:
            w.close
