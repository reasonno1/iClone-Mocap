import PySide2

from qtRangeSlider import *

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtWidgets import *

class VerticalSliderSpinner(QWidget):
    def __init__(self, parentWidget, label, degrees, _x, _y, _max, _min,
                 smooth=False, mute=False, range=False, multiply=False, slider=True):
        # QWidget will be self
        QWidget.__init__(self)
        self.value = 0
        self.multiplyValue = 1
        self.muteValue = self.multiplyValue
        self.parentWidget = parentWidget
        self.max = _max
        self.min = _min
        self.x = _x
        self.y = _y
        
        self.label = label
        self.degrees = degrees
        vboxLayout = PySide2.QtWidgets.QVBoxLayout()
        vboxLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(vboxLayout)
        self.sliderContainer = PySide2.QtWidgets.QWidget()
        hboxLayout = PySide2.QtWidgets.QHBoxLayout()
        self.sliderContainer.setLayout(hboxLayout)
        self.layout().addWidget(self.sliderContainer)
        self.labelUi = PySide2.QtWidgets.QLabel()
        self.slider = PySide2.QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.muteButton = PySide2.QtWidgets.QToolButton()
        self.rangeButton = PySide2.QtWidgets.QToolButton()

        self.sliderContainer.layout().addWidget(self.labelUi)
        self.sliderContainer.layout().addWidget(self.slider)
        
        self.buttonGroup = PySide2.QtWidgets.QWidget()
        hboxLayout = PySide2.QtWidgets.QHBoxLayout()
        self.buttonGroup.setLayout(hboxLayout)
        self.buttonGroup.layout().setContentsMargins(0,0,0,0)
        
        self.spinnerGroup = PySide2.QtWidgets.QWidget()
        hboxLayout = PySide2.QtWidgets.QHBoxLayout()
        self.spinnerGroup.setLayout(hboxLayout)
        self.spinnerGroup.layout().setContentsMargins(0,0,0,0)

        self.layout().addWidget(self.spinnerGroup)
        self.spinner = PySide2.QtWidgets.QSpinBox()
        self.multiplySpinner = PySide2.QtWidgets.QDoubleSpinBox()
        
        self.spinnerLabel = PySide2.QtWidgets.QLabel()
        self.spinnerGroup.layout().addWidget( self.multiplySpinner )
        self.spinnerGroup.layout().addWidget( self.spinnerLabel )
        self.spinnerGroup.layout().addWidget( self.spinner )
        self.spinnerLabel.setText("X")

        self.layout().addWidget( self.buttonGroup )
        self.buttonGroup.layout().addWidget( self.muteButton )
        self.buttonGroup.layout().addWidget( self.rangeButton )
        
        self.muteButton.setText("M")
        self.muteButton.setCheckable(True)
        self.rangeButton.setText("R")
        
        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.spinner.valueChanged.connect(self.spinnerValueChanged)
        self.spinner.setMaximum(self.max)
        self.spinner.setMinimum(self.min)
        self.spinner.setValue(0)
        
        self.multiplySpinner.setMaximum(3)
        self.multiplySpinner.setMinimum(0)
        self.multiplySpinner.setSingleStep(0.1)
        self.multiplySpinner.setValue( self.multiplyValue )
        
        self.slider.setMaximum(self.max)
        self.slider.setMinimum(self.min)
        self.slider.setValue( 0 )

        if range:
            self.rangeButton.show()
        else:
            self.rangeButton.hide()
        
        if mute:
            self.muteButton.show()
        else:
            self.muteButton.hide()
            
        if multiply:
            self.multiplySpinner.show()
            self.spinnerLabel.show()
            self.spinner.setEnabled(False)
            self.slider.setEnabled(False)
        else:
            self.multiplySpinner.hide()
            self.spinnerLabel.hide()
            self.spinner.setEnabled(True)
            self.slider.setEnabled(True)

        if slider:
            self.spinner.setEnabled(True)
            self.slider.setEnabled(True)
        else:
            self.spinner.setEnabled(False)
            self.slider.setEnabled(False)
        
        self.rangeButton.clicked.connect(self.showRangeDlg)
        self.muteButton.clicked.connect(self.muteClick)
        self.isMuteClick = self.muteButton.isChecked()
        self.multiplySpinner.valueChanged.connect(self.multiplySpinnerChanged)
    
    def setMultiplyValue(self,value):
        self.multiplyValue = value
        self.multiplySpinner.setValue(self.multiplyValue)
    
    def multiplySpinnerChanged(self):
        self.multiplyValue = self.multiplySpinner.value()
    
    def muteClick(self):
        self.isMuteClick = self.muteButton.isChecked()
        if (self.isMuteClick):
            self.muteValue = self.multiplyValue
            self.multiplySpinner.setEnabled(False)
            self.setMultiplyValue(0)
        else:
            self.multiplyValue = self.muteValue
            self.multiplySpinner.setEnabled(True)
            self.setMultiplyValue(self.multiplyValue)
    
    def showRangeDlg(self):
        dialog = QRangeSliderDialog(title_text = "Range Slider",
                                    slider_range = [0, 1, 0.1],
                                    values = [self.min/100, self.max/100], parent = self)
        
        #dialog.open()
        dialog.exec_()
        if dialog.exec_():
            #self.slider.setValue( 10 )
            self.min = dialog.getValues()[0]*100
            self.max = dialog.getValues()[1]*100
            self.slider.setMinimum(dialog.getValues()[0]*100)
            self.slider.setMaximum(dialog.getValues()[1]*100)
            self.spinner.setMinimum(dialog.getValues()[0]*100)
            self.spinner.setMaximum(dialog.getValues()[1]*100)
    
    def debugMsg(self, _str):
        _text = str(_str)
        info_dialog = PySide2.QtWidgets.QMessageBox()
        info_dialog.setWindowTitle('Debug Window')
        info_dialog.setText(_text)
        info_dialog.exec_()

    def showSmoothDlg(self):
        None
    
    def setValue(self, value):
        if (self.isMuteClick):
            value = 0
        # self.value = value/(self.max-self.min)
        self.value = value
        self.spinner.setValue(value)
        self.slider.setValue(value)
        self.parentWidget.onValueChanged(self.value)
        
    def spinnerValueChanged(self):
        #print "spinner"
        self.value = self.spinner.value()
        self.slider.setValue(self.spinner.value())
        self.parentWidget.onValueChanged(self.value)
        
    def sliderValueChanged(self):
        #print "slider"
        self.value = self.slider.value()
        self.spinner.setValue(self.slider.value())
        self.parentWidget.onValueChanged(self.value)
    
    def paintEvent(self, event):
        '''
        the method paintEvent() is called automatically
        the QPainter class does the low-level painting
        between its methods begin() and end()
        '''
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen('#999999')
        x = self.x
        y = self.height() - self.y
        qp.translate(x, y)
        qp.rotate(self.degrees)
        qp.drawText(0, 0, self.label)
        qp.end()