import script, scriptEvent, socket, sys, os, struct, PySide2, Queue, json

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget
from PySide2 import shiboken2
from PySide2.QtWidgets import QWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.shiboken2 import wrapInstance
from PySide2.QtCore import QThread
import os.path

ExcuteParentPath = os.path.abspath(os.path.join(sys.executable, os.pardir))
ResPath = ExcuteParentPath + "\FM2"
sys.path.insert(0, ResPath) #or sys.path.append('/path/to/application/app/folder')

mainUI = ResPath + "\\resource\FM_mainWindow.ui"
mappingUI = ResPath + "\\resource\FM_mapping.ui"
dataSourceUI = ResPath + "\\resource\FM_dataSource.ui"
dataSmoothUI = ResPath + "\\resource\FM_smooth.ui"
dataRangeUI = ResPath + "\\resource\FM_range.ui"
deviceConnectUI = ResPath + "\\resource\FM_connect.ui"
iCloneStreamingUI = ResPath + "\\resource\FM_iCloneStreaming.ui"

from resource.smooth import *
import resource.rlWidget
import resource.qtRangeSlider
import resource.VerticalSliderSpinner
reload(resource.rlWidget)
reload(resource.VerticalSliderSpinner)
reload(resource.qtRangeSlider)

from resource.VerticalSliderSpinner import VerticalSliderSpinner

globalStrength = 100
smoothFilterBuffer = []

##########################
## GLOBAL VARIABLES 
##########################

rlSliderRegularContainer = []
rlSliderCustomContainer = []
rlSliderEyeLContainer = []
rlSliderEyeRContainer = []
rlSliderHeadContainer = []
rlSliderBoneContainer = []

device = None
testBool = False
previewing = False
recording = False
mappingui_on = False
source_max = 1.0
source_min = 0.0
server_ip = '127.0.0.1'
server_port = 802

#####################################  iClone CSS  #####################################
icCss_style ="""/*整體widget 樣式*/\nQWidget{background-color:#282828;color:#c8c8c8;font-size:12px;font-family:Arial, Helvetica, sans-serif; }\n\n
QToolButton{ min-width:23px; min-height:23px; max-height:23px; border:1px solid #505050; background-color:#282828; color:#c8c8c8}\n
QToolButton:hover { min-width:23px; min-height:23px; max-height:23px; background-color:#505050;border:1px solid #505050; color:#c8c8c8}\n
QToolButton:pressed{ min-width:23px; min-height:23px; max-height:23px; padding: 0px;border:1px solid #505050;background-color:#c8c8c8; color:#000000}\n
QToolButton:checked{min-width:23px; min-height:23px; max-height:23px; padding:0px; border:1px solid #505050;background-color:#c8c8c8; color:#000000}\n
QToolButton:unchecked{min-width:23px; min-height:23px; max-height:23px; padding:0px;border:1px solid #3c3c3c;background-color:#282828; color:#464646}\n
\nQTabWidget::pane { /* The tab widget frame */ border: 1px solid #505050;background-color:#282828;}\n
QTabBar{background-color:#282828; border:1px solid #505050; }\n
QTabBar::tab { font-size:12px; font-weight:bold; text-align:center;border:1px solid #505050; min-width:120px; min-height:25px; background-color:#282828; color:#c8c8c8; border-bottom: 0px; }\n
QTabBar::tab:hover  {background-color:#82be0f;Color:#000000;}\n
QTabBar::tab:selected { background-color:#82be0f;color:#000000;}\n\n\n
/*Combo Box*/\n
QComboBox {/*min-width:200px;*/ min-height:23px;max-height:23px;border:1px solid #505050;background-color:#282828; font-size:12px; color:#c8c8c8;font-family:Arial, Helvetica, sans-serif;padding-left:10px;}\n
QComboBox:!editable, QComboBox::drop-down:editable {background-color:#282828;}\n
QComboBox:!editable:disabled, QComboBox::drop-down:editable:disabled {background-color:#282828;color:#464646;border:1px solid #3c3c3c;}\n
/* QComboBox gets the "on" state when the popup is open */\n
QComboBox:!editable:on, QComboBox::drop-down:editable:on {background-color:#505050;color:#c8c8c8;border:1px solid #505050;}\n
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 20px;border:none;}\n
QComboBox::down-arrow { image:url(:/icons/Elements/ArrowPath_B.svg);background-color:transparent; }\n
QComboBox::down-arrow:disabled{ image:url(:/icons/Elements/ArrowPath_B_dis.svg);background-color:transparent; }\n
QComboBox QAbstractItemView {selection-background-color:#505050; selection-color:#c8c8c8; background-color:#282828; color:#c8c8c8;} \n\n
/*Check Box*/\nQCheckBox{min-height:25px; spacing: 5px; color:#c8c8c8;background-color:transparent; }\nQCheckBox:hover{color:#c8c8c8; }\n
QCheckBox:disabled{color:#464646;}\n\n
QCheckBox::indicator:unchecked{image: url(:/icons/Elements/CheckOff.svg); }\n
QCheckBox::indicator:unchecked:hover{ image: url(:/icons/Elements/CheckOff_hov.svg); }\n
QCheckBox::indicator:unchecked:pressed{ image: url(:/icons/Elements/CheckOff_hov.svg);}\n
QCheckBox::indicator:unchecked:disabled{ image: url(:/icons/Elements/CheckOff_dis.svg);}\n
QCheckBox::indicator:checked{image: url(:/icons/Elements/CheckOn_sel.svg); }\n
QCheckBox::indicator:checked:hover{image: url(:/icons/Elements/CheckOn_hov.svg); }\n
QCheckBox::indicator:checked:pressed{image: url(:/icons/Elements/CheckOn_hov.svg); }\n
QCheckBox::indicator:checked:disabled{image: url(:/icons/Elements/CheckOn_dis.svg);}\n\n
/*Radio Button*/\nQRadioButton{min-height:25px; spacing: 5px; color:#c8c8c8;}\n
QRadioButton:hover{color:#c8c8c8; }\n
QRadioButton:disabled{color:#464646;}\n
QRadioButton::indicator { width: 18px;height: 18px; }\n
QRadioButton::indicator::unchecked { image: url(:/icons/Elements/RadioOff.svg); }\n
QRadioButton::indicator:unchecked:hover { image: url(:/icons/Elements/RadioOff_hov.svg); }\n
QRadioButton::indicator:unchecked:pressed { image: url(:/icons/Elements/RadioOff_hov.svg); }\n
QRadioButton::indicator:unchecked:disabled { image: url(:/icons/Elements/RadioOff_dis.svg); }\n
QRadioButton::indicator::checked { image: url(:/icons/Elements/RadioOn.svg); }\n
QRadioButton::indicator:checked:hover { image: url(:/icons/Elements/RadioOn_hov.svg); }\n
QRadioButton::indicator:checked:pressed { image: url(:/icons/Elements/RadioOn_hov.svg);}\n
QRadioButton::indicator:checked:disabled { image: url(:/icons/Elements/RadioOn_dis.svg);}\n\n
/*Spinbox*/\n
QSpinBox {background-color:#282828; font-size:12px; border:1px solid #505050; padding:1px ; font-family:Helvetica, Arial, sans-serif; min-height:21px;max-height:21px;min-width:52px;color:#c8c8c8;}\nQSpinBox:disabled{color:#464646;border:1px solid #3c3c3c;}\n
QSpinBox::up-button { subcontrol-origin: border; subcontrol-position:top right; /* position at the top right corner */ width: 13px; height:11px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */background-color:#282828; border:1px solid #505050; }\n
QSpinBox::up-button:hover {background-color:#505050;}\n
QSpinBox::up-button:pressed {background-color:#c8c8c8;}\n
QSpinBox::up-button:disabled {background-color:#282828; border:1px solid #3c3c3c;}\n
QSpinBox::up-arrow {qproperty-icon: none; image: url(:/icons/Elements/ArrowSpinner_T.svg); width: 10px; height: 5px;}\n
QSpinBox::up-arrow:hover{ image: url(:/icons/Elements/ArrowSpinner_T.svg); width: 10px; height: 5px;}\n
QSpinBox::up-arrow:pressed{ image: url(:/icons/Elements/ArrowSpinner_T_sel.svg); width: 10px; height: 5px;}\n
QSpinBox::up-arrow:disabled, QSpinBox::up-arrow:off { /* off state when value is max */ image: url(:/icons/Elements/ArrowSpinner_T_dis.svg); }\n\n
QSpinBox::down-button { subcontrol-origin:border; subcontrol-position: bottom right; /* position at bottom right corner */\nwidth: 13px; height:11px; background-color:#282828; border:1px solid #505050; border-width: 1px;border-top-width: 0;}\n
QSpinBox::down-button:hover {background-color:#505050;}\n
QSpinBox::down-button:pressed {background-color:#c8c8c8;}\n
QSpinBox::down-button:disabled {background-color:#282828; border:1px solid #3c3c3c;}\n
QSpinBox::down-arrow {image: url(:/icons/Elements/ArrowSpinner_B.svg); width:10px; height: 5px; }\n
QSpinBox::down-arrow:hover {image: url(:/icons/Elements/ArrowSpinner_B.svg); width:10px; height: 5px; }\n
QSpinBox::down-arrow:pressed {image: url(:/icons/Elements/ArrowSpinner_B_sel.svg); width:10px; height: 5px; }\n
QSpinBox::down-arrow:disabled, QSpinBox::down-arrow:off { /* off state when value in min */ image:url(:/icons/Elements/ArrowSpinner_B_dis.svg); }\n\n
/*DoubleSpinbox*/\nQDoubleSpinBox {background-color:#282828; font-size:12px; border:1px solid #505050; padding:1px ; font-family:Helvetica, Arial, sans-serif; min-height:21px;max-height:21px;min-width:52px;color:#c8c8c8;}\n
QDoubleSpinBox:disabled{color:#464646;border:1px solid #3c3c3c;}\nQDoubleSpinBox::up-button { subcontrol-origin: border; subcontrol-position:top right; /* position at the top right corner */ width: 13px; height:11px; /* 16 + 2*1px border-width = 15px padding + 3px parent border */background-color:#282828; border:1px solid #505050; }\n
QDoubleSpinBox::up-button:hover {background-color:#505050;}\n
QDoubleSpinBox::up-button:pressed {background-color:#c8c8c8;}\n
QDoubleSpinBox::up-button:disabled {background-color:#282828; border:1px solid #3c3c3c;}\nQDoubleSpinBox::up-arrow {qproperty-icon: none; image: url(:/icons/Elements/ArrowSpinner_T.svg);width: 10px; height: 5px;}\n
QDoubleSpinBox::up-arrow:hover{ image: url(:/icons/Elements/ArrowSpinner_T.svg); width: 10px; height: 5px;}\n
QDoubleSpinBox::up-arrow:pressed{ image: url(:/icons/Elements/ArrowSpinner_T_sel.svg); width: 10px; height: 5px;}\n
QDoubleSpinBox::up-arrow:disabled, QSpinBox::up-arrow:off { /* off state when value is max */ image: url(:/icons/Elements/ArrowSpinner_T_dis.svg); }\n\n
QDoubleSpinBox::down-button { subcontrol-origin:border; subcontrol-position: bottom right; /* position at bottom right corner */\nwidth: 13px; height:11px; background-color:#282828; border:1px solid #505050; border-width: 1px;border-top-width: 0;}\n
QDoubleSpinBox::down-button:hover {background-color:#505050;}\nQDoubleSpinBox::down-button:pressed {background-color:#c8c8c8;}\n
QDoubleSpinBox::down-button:disabled {background-color:#282828; border:1px solid #3c3c3c;}\n
QDoubleSpinBox::down-arrow {image: url(:/icons/Elements/ArrowSpinner_B.svg); width:10px; height: 5px; }\n
QDoubleSpinBox::down-arrow:hover {image: url(:/icons/Elements/ArrowSpinner_B.svg); width:10px; height: 5px; }\n
QDoubleSpinBox::down-arrow:pressed {image: url(:/icons/Elements/ArrowSpinner_B_sel.svg); width:10px; height: 5px; }\n
QDoubleSpinBox::down-arrow:disabled, QSpinBox::down-arrow:off { /* off state when value in min */ image:url(:/icons/Elements/ArrowSpinner_B_dis.svg); }\n\n\n/*Slider_不下key*/\nQSlider{border:none;background-color:none; }\n
QSlider::groove:horizontal { background-color:#c8c8c8;  height: 1px;margin:0px 2px;}\n
QSlider::groove:horizontal:disabled{background-color:#464646; height:1px;margin:0px 2px;}\n
QSlider::handle:horizontal { image:url(:/icons/Elements/Bollet.svg); border: 0px solid #9e9e9e;width:20px; height:20px; margin:-10px -4px;  }\n
QSlider::handle:horizontal:hover{ image:url(:/icons/Elements/Bollet_hov.svg); }\n
QSlider::handle:horizontal:pressed{ image:url(:/icons/Elements/Bollet_sel.svg); }\n
QSlider::handle:horizontal:disabled{ image:url(:/icons/Elements/Bollet_dis.svg); }\n\n
/*垂直Scroll Bar */\nQScrollBar:vertical {background-color:#282828;min-width:6px;/*margin-bottom:2px;*/border-bottom:0px solid #505050;padding: 20 0 20 0;margin: -10 0 -10 0;}\n
QScrollBar::handle:vertical {background-color:#505050; border-radius:3px; min-width:1px; max-width:1px;min-height:20px;height:20px;\n	 margin:5px;}\n
QScrollBar::handle:vertical:hover {background-color:#55641b;}\n
QScrollBar::handle:vertical:pressed {background-color:#82be0f;}\nQScrollBar::add-line:vertical {border: none;background: transparent;width: 0;\nsubcontrol-position: right;}\n\n
QScrollBar::sub-line:vertical {border: none;background: transparent;width: 0;\nsubcontrol-position: left;}\n
QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {\nbackground: transparent;}\n
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\nbackground: transparent;}\n\n/*水平Scroll Bar*/\n
QScrollBar:horizontal {background-color:#282828;min-height:6px;margin-right:2px;border-right:0px solid #505050;}\n
QScrollBar::handle:horizontal {background-color:#505050; border-radius:3px;min-height:1px;max-height:1px;min-width:20px;width:20px;\n	 margin:5px;}\n
QScrollBar::handle:horizontal:hover {background-color:#55641b;}\n
QScrollBar::handle:horizontal:pressed {background-color:#82be0f;}\nQScrollBar::add-line:horizontal {border: none;background: transparent;width: 0;\nsubcontrol-position: right;}\n
QScrollBar::sub-line:horizontal {border: none;background: transparent;width: 0;\nsubcontrol-position: left;}\n
QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal {background: transparent;}\n
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {background: transparent;}\n\n
QToolButton#qtPreviewPushButton{font-size:12px;text-align:center; min-height:46px; min-width:90px;color:#c8c8c8;\nbackground-color:#282828;border-radius:8px; border:1px solid #505050;qproperty-iconSize:30px 30px ; padding-top:2px }\n
QToolButton#qtPreviewPushButton:hover{color:#c8c8c8;background-color:#505050; }\n
QToolButton#qtPreviewPushButton:pressed{color:#c8c8c8;background-color:#282828; }\n
QToolButton#qtPreviewPushButton:disabled{color:#464646;border:1px solid #3c3c3c;}\n\n
QToolButton#qtRecordPushButton{font-size:12px;text-align:center; min-height:46px; min-width:90px;color:#c8c8c8;\nbackground-color:#282828;border-radius:8px; border:1px solid #505050;qproperty-iconSize:30px 30px ; padding-top:2px }\n
QToolButton#qtRecordPushButton:hover{color:#c8c8c8;background-color:#505050; }\n
QToolButton#qtRecordPushButton:pressed{color:#c8c8c8;background-color:#282828; }\n
QToolButton#qtRecordPushButton:disabled{color:#464646;border:1px solid #3c3c3c;}\n\n\n/*LineEdit*/\nQLineEdit{border:1px solid #505050;min-height:23px; padding-left:5px;background-color:#282828;}\nQLineEdit:disabled{border:1px solid #3c3c3c; color:#464646;background-color:#282828;}\n\n
/*QLabel*/\n
QLabel{min-height:25px;background-color:transparent;}\nQLabel:disabled{color:#464646;}\n\n
QGroupBox{ border: 0px }\n
QGroupBox::title {\nsubcontrol-origin: margin;\nsubcontrol-position: top left;\nleft:0px\n}\n"""

#####################################   faceware List   #####################################
facewareList = ["mouth_rightMouth_stretch", "mouth_leftMouth_narrow", "mouth_up",
                "mouth_leftMouth_stretch", "mouth_rightMouth_narrow", "mouth_down",
                "mouth_upperLip_left_up", "mouth_upperLip_right_up", "mouth_lowerLip_left_down",
                "mouth_lowerLip_right_down", "mouth_leftMouth_frown", "mouth_rightMouth_frown",
                "mouth_leftMouth_smile", "mouth_rightMouth_smile", "eyes_lookRight", "eyes_lookLeft",
                "eyes_lookDown", "eyes_lookUp", "eyes_leftEye_blink", "eyes_rightEye_blink",
                "eyes_leftEye_wide", "eyes_rightEye_wide", "brows_leftBrow_up", "brows_leftBrow_down",
                "brows_rightBrow_up", "brows_rightBrow_down", "brows_midBrows_up", "brows_midBrows_down",
                "jaw_open", "jaw_left", "jaw_right", "mouth_phoneme_oo", "mouth_right",
                "mouth_left", "mouth_phoneme_mbp", "mouth_phoneme_ch", "mouth_phoneme_fv", "head_Up",
                "head_Down", "head_Left", "head_Right", "head_LeftTilt", "head_RightTilt"]

#####################################   RL Expression List   #####################################

#brow 1~8 / eye 9~15 / nose 16~20 / cheek 21~25 / mouth 26~60
feRegularList = ["01.Brow Raise Inner L", "02.Brow Raise Inner R", "03.Brow Raise Outer L", "04.Brow Raise Outer R",
                 "05.Brow Drop L", "06.Brow Drop R", "07.Brow Raise L", "08.Brow Raise R", "09.Eyes Blink",
                 "10.Eye Blink L", "11.Eye Blink R", "12.Eye Wide L", "13.Eye Wide R", "14.Eye Squint L",
                 "15.Eye Squint R", "16.Nose Scrunch", "17.Nose Flanks Raise", "18.Nose Flank Raise L",
                 "19.Nose Flank Raise R", "20.Nose Nostrils Flare", "21.Cheek Raise L", "22.Cheek Raise R",
                 "23.Cheeks Suck", "24.Cheek Blow L", "25.Cheek Blow R", "26.Mouth Smile", "27.Mouth Smile L",
                 "28.Mouth Smile R", "29.Mouth Frown", "30.Mouth Frown L","31.Mouth Frown R", "32.Mouth Blow",
                 "33.Mouth Pucker", "34.Mouth Pucker Open", "35.Mouth Widen", "36.Mouth Widen Sides",
                 "37.Mouth Dimple L", "38.Mouth Dimple R", "39.Mouth Plosive", "40.Mouth Lips Tight",
                 "41.Mouth Lips Tuck", "42.Mouth Lips Open", "43.Mouth Lips Part", "44.Mouth Bottom Lip Down",
                 "45.Mouth Top Lip Up", "46.Mouth Top Lip Under", "47.Mouth Bottom Lip Under", "48.Mouth Snarl Upper L",
                 "49.Mouth Snarl Upper R", "50.Mouth Snarl Lower L", "51.Mouth Snarl Lower R",
                 "52.Mouth Bottom Lip Bite", "53.Mouth Down", "54.Mouth Up", "55.Mouth L", "56.Mouth R",
                 "57.Mouth Lips Jaw Adjust", "58.Mouth Bottom Lip Trans", "59.Mouth Skewer", "60.Mouth Open"]

feCustomList = ["01.xx", "02.xx", "03.xx", "04.xx", "05.xx", "06.xx", "07.xx", "08.xx", "09.xx", "10.xx",
                "11.xx", "12.xx", "13.xx", "14.xx", "15.xx", "16.xx", "17.xx", "18.xx", "19.xx", "20.xx",
                "21.xx", "22.xx", "23.xx", "24.xx"]

feBone = ["07.JawRotateY", "08.JawRotateZ", "09.JawRotateX", "10.JawMoveX", "11.JawMoveY", "12.JawMoveZ"]

feEyeL = ["EyeL_rightLeft_l", "EyeL_downUp_l"]

feEyeR = ["EyeR_rightLeft_r", "EyeR_downUp_r"]

feHead = ["Head_up_down", "Head_right_left", "Head_tilt"]

iCStreamingData = []

#####################################   Mask Table   #####################################

# [RegularExpression, Bone, Head, EyeballL, EyeballR]
masking_list = [[], True, True, True, True]

#####################################   init Data Structure   #####################################
feRegularData = []
for i in range(60):
    feRegularData.append(0.0)
    
feCustomData = []
for i in range(24):
    feCustomData.append(0.0)

feEyeLData = []
for i in range(2):
    feEyeLData.append(0.0)
    
feEyeRData = []
for i in range(2):
    feEyeRData.append(0.0)

feHeadData = []
for i in range(3):
    feHeadData.append(0.0)
    
feBoneData = []
for i in range(6):
    feBoneData.append(0.0)

data = []
sourceData = []
def initDataStructure():
    global data
    data = []
    for i in range(len(facewareList)):
        tempData = {
            "id": facewareList[i],
            "feRegularData": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "feCustomData": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "feBoneData": [0, 0, 0, 0, 0, 0],
            "feEyeLData": [0, 0],
            "feEyeRData": [0, 0],
            "feHeadData": [0, 0, 0],
        }
        data.append(tempData)
initDataStructure()

##########################
## CLASSES 
##########################

class CacheBuffer():
    def __init__(self):
        self.queue = Queue.Queue(maxsize = 10)
        self.lock = False
        
    def setData( self, dataX ):
        if self.queue.qsize() == 10:
            return
        while self.lock == True:
            pass
        self.lock = True
        print 'setData'
        self.queue.put(dataX)
        print self.queue.qsize()
        self.lock = False
        
    def getData(self):
        if self.queue.qsize() == 0:
            return None
        self.lock = True
        while self.queue.qsize() != 0:
            data = self.queue.get()
        self.lock = False
        return data
        
streamCacheBuf = CacheBuffer()
        
class DataThread(QThread):
    def __init__(self,subData,parent=None):
        QThread.__init__(self,parent)
        self.subData = subData
    
    def __del__(self):
        self.quit()
        self.wait()
    
    def run(self):
        while True:
            self.subData.streamCacheBuffer.setData(self.subData.sock.recv(64*1024))
            #self.subData.loop()
        #self.sleep(0)

class Faceware_live():

    def __init__(self, *args, **kwargs):
        global facewareList
        self.sock = None
        self.thread = None
        self.serverExiting = False
        
    def run(self):
        global streamCacheBuf
        if self.sock != None:
            self.streamData = self.sock.recv(64*1024)
            streamCacheBuf.setData( self.streamData )

    def start(self):
        self.count = 0
        self.bool = True
        if self.sock == None:
            global server_ip
            global server_port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            facewareSock_server_address = (server_ip, server_port)
            self.sock.settimeout(5)

            try:
                self.streamCacheBuffer = CacheBuffer()
                self.sock.connect(facewareSock_server_address)
                self.thread = DataThread(self)
                self.thread.start()
                self.loop()
                if self.serverExiting == False:
                    self.serverExiting = True

            except socket.timeout:
                self.serverExiting = False

    def stop(self):
        # print "stop"
        self.count = 0
        if self.thread != None:
            self.thread.terminate()
            self.thread.wait()
            self.thread = None

        if self.sock != None:
            self.sock.close()
            self.sock = None

        self.serverExiting = False

    def loop(self):
        received = self.streamCacheBuffer.getData()
        if received != None:
            self.extractData(received)
    
    def extractData(self, received):
        global previewing
        global recording
        try:
            reciv=received[0]+received[1]+received[2]+received[3]
        except:
            debugMsg("disconnect")
            debugMsg(reciv)
            self.stop()
            fmMainUi.qtRecordPushButton.setEnabled(True)
            fmMainUi.qtMappingToolButton.setEnabled(True)
            if previewing:
                fmMainUi.qtPreviewPushButton.setText("Start Preview")
                previewing = not previewing

            elif recording:
                fmMainUi.qtRecordPushButton.setText("Start Record")
                recording = not recording

            zeroExpressionData()
            try:
                script.EndFacePuppetKey(script.GetPickedObjectName(),
                                        script.ConvertTimeToFrame(script.GetCurrentTimeScript()))
            except:
                pass
            scriptEvent.StopTimer()
            return

        blockSize = struct.unpack('i', reciv)[0]
        
        if (len(received)) >= blockSize:
            dataType = "i"
            for i in range(len(received)-4, 0, -1):
                dataType = dataType+"c"
            dataStream = struct.unpack(dataType, received)
            data = ""

            for i in range(1, blockSize, 1):
                data = data + dataStream[i]

            data = data + "}"
            self.analystData(data)

    def renameKeys(self,iterable):
        if type(iterable) is dict:
            for key in iterable.keys():
                iterable[key.lower()] = iterable.pop(key)
                if type(iterable[key.lower()]) is dict or type(iterable[key.lower()]) is list:
                    iterable[key.lower()] = renameKeys(iterable[key.lower()])
        elif type(iterable) is list:
            for item in iterable:
                item = renameKeys(item)
        return iterable
    
    def analystData(self,_json):
        print "analystData"
        global globalStrength

        # Accept & Decode Faceware Data
        decodejson = json.loads(_json)
        dataFromFaceware = decodejson["animationValues"]
        self.value = []
        dataFromFaceware = self.renameKeys(dataFromFaceware)

        for name in facewareList:
            data_name = name.lower()
            try:
                self.value.append(dataFromFaceware[data_name])
            except:
                self.value.append(0)

        # init iClone Facial Data
        iCloneRegularData = []
        for i in range(60):
            iCloneRegularData.append(0)
        iCloneCustomData = []
        for i in range(24):
            iCloneCustomData.append(0)
        iCloneEyeRData = []
        for i in range(2):
            iCloneEyeRData.append(0)
        iCloneEyeLData = []
        for i in range(2):
            iCloneEyeLData.append(0)
        iCloneBoneData = []
        for i in range(12):
            iCloneBoneData.append(0)
        iCloneHeadData = []
        for i in range(3):
            iCloneHeadData.append(0)

        ####################    Mapping Data To iClone Expression   ####################
        global data
        global testBool


        # global masking_list
        masking_list = mask_ckbox_to_masking_list()

        # Mapping RegularExpression Data * 60
        for i in range(len(facewareList)):
            out_value = self.value[i]

            for j in range(len(data)):
                if (data[j]["id"] == facewareList[i]):
                    for k in range(len(data[j]["feRegularData"])):
                        iCloneRegularData[k] = iCloneRegularData[k] + (data[j]["feRegularData"][k]*out_value)
        
        # Masking RegularExpression Data
        if len(masking_list[0]) != 0:
            for i in masking_list[0]:
                iCloneRegularData[i] = 0

        # Mapping Custom Data * 24
        for i in range(len(facewareList)):
            out_value = self.value[i]

            for j in range(len(data)):
                if ( data[j]["id"] == facewareList[i] ):
                    for k in range(len(data[j]["feCustomData"])):
                        iCloneCustomData[k] = iCloneCustomData[k] + (data[j]["feCustomData"][k]*out_value)

        # Mapping Jaw Bone Data * 6
        if masking_list[1]:
            for i in range(len(facewareList)):
                out_value = self.value[i]

                for j in range(len(data)):
                    if ( data[j]["id"] == facewareList[i] ):
                        for k in range(len(data[j]["feBoneData"])):
                            iCloneBoneData[k + 6] = iCloneBoneData[k + 6] + (data[j]["feBoneData"][k]*out_value)

        # Mapping Eyeball Left Data * 2
        if masking_list[2]:
            for i in range(len(facewareList)):
                out_value = self.value[i]

                for j in range(len(data)):
                    if ( data[j]["id"] == facewareList[i] ):
                        for k in range(len(data[j]["feEyeLData"])):
                            iCloneEyeLData[k] = iCloneEyeLData[k] + (data[j]["feEyeLData"][k]*out_value)

        # Mapping Eyeball Right Data * 2
        if masking_list[3]:
            for i in range(len(facewareList)):
                out_value = self.value[i]

                for j in range(len(data)):
                    if ( data[j]["id"] == facewareList[i] ):
                        for k in range(len(data[j]["feEyeRData"])):
                            iCloneEyeRData[k] = iCloneEyeRData[k] + (data[j]["feEyeRData"][k]*out_value)

        # Mapping Head Data * 3
        if masking_list[4]:
            for i in range(len(facewareList)):
                out_value = self.value[i]

                for j in range(len(data)):
                    if ( data[j]["id"].lower() == facewareList[i].lower() ):
                        for k in range(len(data[j]["feHeadData"])):
                            if ( data[j]["feHeadData"][k]):
                                iCloneHeadData[k] = iCloneHeadData[k] + ((data[j]["feHeadData"][k])*out_value)

        ####################    Strength Data   ####################
        for i in range(len(iCloneRegularData)):
            if (i >= 0 and i <= 7):
                iCloneRegularData[i] = iCloneRegularData[
                                           i] * fmMainUi.Slider_stBrow.value() / 100

            elif (i >= 8 and i <= 14):
                iCloneRegularData[i] = iCloneRegularData[
                                           i] * fmMainUi.Slider_stEye.value() / 100

            elif (i >= 15 and i <= 19):
                iCloneRegularData[i] = iCloneRegularData[
                                           i] * fmMainUi.Slider_stNose.value() / 100

            elif (i >= 20 and i <= 24):
                iCloneRegularData[i] = iCloneRegularData[
                                           i] * fmMainUi.Slider_stCheek.value() / 100

            elif (i >= 25 and i <= 59):
                iCloneRegularData[i] = iCloneRegularData[
                                           i] * fmMainUi.Slider_stMouth.value() / 100

        for i in range(len(iCloneBoneData)):
            iCloneBoneData[i] = iCloneBoneData[i] * fmMainUi.Slider_stJaw.value() / 100

        for i in range(len(iCloneHeadData)):
            iCloneHeadData[i] = iCloneHeadData[i] * fmMainUi.Slider_stHead.value() / 100

        for i in range(len(iCloneEyeRData)):
            iCloneEyeRData[i] = iCloneEyeRData[i] * fmMainUi.Slider_stEyeball.value() / 100

        for i in range(len(iCloneEyeLData)):
            iCloneEyeLData[i] = iCloneEyeLData[i] * fmMainUi.Slider_stEyeball.value() / 100

        for i in range(len(iCloneCustomData)):
            iCloneCustomData[i] = iCloneCustomData[i] * fmMainUi.Slider_stCustom.value() / 100

        ####################    Smooth Data   ####################
        global smoothFilterBuffer

        # Buffer for Smoothing (BufferSize = 20)
        if (len(smoothFilterBuffer) < 10):
            smoothFilterBuffer.append(
                [iCloneRegularData, iCloneBoneData, iCloneHeadData, iCloneEyeRData, iCloneEyeLData, iCloneCustomData])
        else:
            smoothFilterBuffer.pop(0)
            smoothFilterBuffer.append(
                [iCloneRegularData, iCloneBoneData, iCloneHeadData, iCloneEyeRData, iCloneEyeLData, iCloneCustomData])

        # Smoothing
        if (len(smoothFilterBuffer) == 10):
            for i in range(len(iCloneRegularData)):
                temp = []
                for j in range(len(smoothFilterBuffer)):
                    temp.append(smoothFilterBuffer[j][0][i])

                if(i >= 0 and i <= 7):
                    smoothData = smoothList(temp, fmMainUi.Slider_smBrow.value())
                    iCloneRegularData[i] = smoothData[len(smoothData) - 1]

                elif(i >= 8 and i <= 14):
                    smoothData = smoothList(temp, fmMainUi.Slider_smEye.value())
                    iCloneRegularData[i] = smoothData[len(smoothData) - 1]

                elif(i >= 15 and i <= 19):
                    smoothData = smoothList(temp, fmMainUi.Slider_smNose.value())
                    iCloneRegularData[i] = smoothData[len(smoothData) - 1]

                elif(i >= 20 and i <= 24):
                    smoothData = smoothList(temp, fmMainUi.Slider_smNose.value())
                    iCloneRegularData[i] = smoothData[len(smoothData) - 1]
                elif(i >= 24 and i <= 59):
                    smoothData = smoothList(temp, fmMainUi.Slider_smMouth.value())
                    iCloneRegularData[i] = smoothData[len(smoothData) - 1]

            for i in range(len(iCloneBoneData)):
                temp = []
                for j in range(len(smoothFilterBuffer)):
                    temp.append(smoothFilterBuffer[j][1][i])
                smoothData = smoothList(temp, fmMainUi.Slider_smJaw.value())
                iCloneBoneData[i] = smoothData[len(smoothData) - 1]

            for i in range(len(iCloneHeadData)):
                temp = []
                for j in range(len(smoothFilterBuffer)):
                    temp.append(smoothFilterBuffer[j][2][i])
                smoothData = smoothList(temp, fmMainUi.Slider_smHead.value())
                iCloneHeadData[i] = smoothData[len(smoothData) - 1]

            for i in range(len(iCloneEyeRData)):
                temp = []
                for j in range(len(smoothFilterBuffer)):
                    temp.append(smoothFilterBuffer[j][3][i])
                smoothData = smoothList(temp, fmMainUi.Slider_smEyeball.value())
                iCloneEyeRData[i] = smoothData[len(smoothData) - 1]

            for i in range(len(iCloneEyeLData)):
                temp = []
                for j in range(len(smoothFilterBuffer)):
                    temp.append(smoothFilterBuffer[j][4][i])
                smoothData = smoothList(temp, fmMainUi.Slider_smEyeball.value())
                iCloneEyeLData[i] = smoothData[len(smoothData) - 1]

            for i in range(len(iCloneCustomData)):
                temp = []
                for j in range(len(smoothFilterBuffer)):
                    temp.append(smoothFilterBuffer[j][5][i])
                smoothData = smoothList(temp, fmMainUi.Slider_smCustom.value())
                iCloneCustomData[i] = smoothData[len(smoothData) - 1]

        ####################    Source Data Streaming   ####################

        global sourceData
        for i in range(len(sourceData)):
            data_name = sourceData[i].name.lower()
            try:
                sourceData[i].container.setValue(dataFromFaceware[data_name] * 100)
            except:
                None

        ####################    iClone Data Streaming   ####################
        global iCStreamingData
        temp_iCStreaming = []
        for i in range(60):
            temp_iCStreaming.append(iCloneRegularData[i])

        for i in range(24):
            temp_iCStreaming.append(iCloneCustomData[i])

        for i in range(6):
            temp_iCStreaming.append(iCloneBoneData[i + 6])

        for i in range(2):
            temp_iCStreaming.append(iCloneEyeLData[i])

        for i in range(2):
            temp_iCStreaming.append(iCloneEyeRData[i])

        for i in range(3):
            temp_iCStreaming.append(iCloneHeadData[i])

        for i in range(len(iCStreamingData)):
            iCStreamingData[i].container.setValue(int(temp_iCStreaming[i]*100))

            #### Mute iClone Expression ####
            if iCStreamingData[i].container.isMuteClick:
                if i < 60:
                    iCloneCustomData[i] = 0
                elif i > 59 and i < 84:
                    iCloneCustomData[i - 60] = 0
                elif i > 83 and i < 90:
                    iCloneBoneData[i + 6 - 84] = 0
                elif i > 89 and i < 92:
                    iCloneEyeLData[i - 90] = 0
                elif i > 91 and i < 94:
                    iCloneEyeRData[i - 92] = 0
                else:
                    iCloneHeadData[i - 94] = 0

        ####################    Keying   ####################
        current_key = script.ConvertTimeToFrame(script.GetCurrentTimeScript())
        script.ProcessFacePuppetKey(script.GetPickedObjectName(), current_key,
                                    iCloneHeadData, iCloneEyeLData, iCloneEyeRData, iCloneBoneData,
                                    iCloneRegularData, iCloneCustomData)

class Data_iCloneID:
    def __init__(self, name, id, parentWidget, multiplyValue=1):
        self.name = name
        self.id = id
        self.parentWidget = parentWidget
        self.container = VerticalSliderSpinner(self, self.name, -90, 25, 50, 300, -200, mute=True, slider=False)
        self.parentWidget.layout().addWidget(self.container)
    def onValueChanged(self, value):
        None

class DataSourceID:
    def __init__(self, name, id, parentWidget, multiplyValue=1):
        self.name = name
        self.id = id
        self.multiplyValue = multiplyValue
        self.parentWidget = parentWidget
        self.container = VerticalSliderSpinner(self, self.name, -90, 80, 70, 100, 0, smooth=True, mute=True,
                                               range=True, multiply=True, slider=False)
        self.container.setMultiplyValue(self.multiplyValue)
        self.parentWidget.layout().addWidget(self.container)

    def onSmoothClicked(self):
        None
        '''
        global dataSmoothUI
        dataSmoothUI.show()
        '''
        
    def onRangeClicked(self):
        None
        '''
        global dataRangeUI
        dataRangeUI.show()
        '''
        
    def onValueChanged(self, value):
        None

class FacialID:
    def __init__(self, name, id, parentWidget, type):
        self.name = name
        self.id = id
        self.type = type

        self.parentWidget = parentWidget
        self.container = VerticalSliderSpinner(self, self.name, -90, 25, 50, 200, -200)
        self.parentWidget.layout().addWidget(self.container)
    
    def valueNormalize(self, table):
        for i in range(len(table)):
            table[i] = table[i]/100.0
    
    def onValueChanged(self, value):
        global data
        global previewing
        global recording

        value = int(value)/100.0
        if (value < 0.00001 and value > 0.0000) or (value > -0.00001 and value < 0.0000):
            value = 0

        if (self.type == "feRegularData"):
            data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feRegularData"][self.id] = value

        elif (self.type == "feCustomData"):
            data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feCustomData"][self.id] = value

        elif (self.type == "feBoneData"):
            data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feBoneData"][self.id] = value

        elif (self.type == "feEyeLData"):
            data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feEyeLData"][self.id] = value

        elif (self.type == "feEyeRData"):
            data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feEyeRData"][self.id] = value

        elif (self.type == "feHeadData"):
            data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feHeadData"][self.id] = value

        else:
            None

        feRegularData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feRegularData"]
        feCustomData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feCustomData"]
        feBoneData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feBoneData"]
        feEyeLData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feEyeLData"]
        feEyeRData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feEyeRData"]
        feHeadData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feHeadData"]

        if not previewing and not recording:
            try:
                script.BeginFacePuppetKey(script.GetPickedObjectName(), 0, False)
            except:
                pass
                # debugMsg("BeginFacePuppetKey Error")

            script.ProcessFacePuppetKey(script.GetPickedObjectName(), 0, feHeadData, feEyeLData, feEyeRData,
                                        [0, 0, 0, 0, 0, 0, feBoneData[0], feBoneData[1], feBoneData[2], feBoneData[3],
                                         feBoneData[4], feBoneData[5]], feRegularData, feCustomData)
            try:
                script.EndFacePuppetKey(script.GetPickedObjectName(), 0)
            except:
                pass

class rl_mapping_widget(PySide2.QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(rl_mapping_widget, self).__init__(parent=parent)

    def showEvent(self, event):
        can_open = True
        if not previewing and not recording:
            script.Stop()
        if can_open:
            event.accept()
        else:
            event.ignore()

    def closeEvent(self, event):
        global mappingui_on
        global previewing
        global recording
        if not previewing and not recording:
            try:
                script.BeginFacePuppetKey(script.GetPickedObjectName(),
                                          script.ConvertTimeToFrame(script.GetCurrentTimeScript()), False)
            except:
                pass
                # debugMsg("BeginFacePuppetKey Error")

            zeroExpressionData()
            try:
                script.EndFacePuppetKey(script.GetPickedObjectName(),
                                        script.ConvertTimeToFrame(script.GetCurrentTimeScript()))
            except:
                pass
        can_exit = True

        if can_exit:
            mappingui_on = False
            event.accept()  # let the window close
        else:
            event.ignore()

##########################
## FUNCTION
##########################

def debugMsg(_str):
    _text = str(_str)
    info_dialog = PySide2.QtWidgets.QMessageBox()
    info_dialog.setWindowTitle('Debug Window')
    info_dialog.setText(_text)
    info_dialog.exec_()

def toJson(serialized):
    """Return JSON string from given native Python datatypes."""
    return json.dumps(serialized, encoding="utf-8", indent=4)

def fromJson(jsonString):
    """Return native Python datatypes from JSON string."""
    return json.loads(jsonString, encoding="utf-8")

def zeroAll():
    for i in range(len(rlSliderRegularContainer)):
        rlSliderRegularContainer[i].container.setValue(0)
    for i in range(len(rlSliderCustomContainer)):
        rlSliderCustomContainer[i].container.setValue(0)
    for i in range(len(rlSliderEyeLContainer)):
        rlSliderEyeLContainer[i].container.setValue(0)
    for i in range(len(rlSliderEyeRContainer)):
        rlSliderEyeRContainer[i].container.setValue(0)
    for i in range(len(rlSliderHeadContainer)):
        rlSliderHeadContainer[i].container.setValue(0)
    for i in range(len(rlSliderBoneContainer)):
        rlSliderBoneContainer[i].container.setValue(0)

def setData():
    global data
    for i in range(len(facewareList)):
        if (data[i]["id"] == fmMappingUi.qtExpressionComboBox.currentText()):
            data[i]["feRegularData"] = feRegularData
            data[i]["feCustomData"] = feCustomData
            data[i]["feBoneData"] = feBoneData
            data[i]["feEyeLData"] = feEyeLData
            data[i]["feEyeRData"] = feEyeRData
            data[i]["feHeadData"] = feHeadData
            break

def saveData():
    filePath, _ = PySide2.QtWidgets.QFileDialog.getSaveFileName(
                None,
                "Save Scene to JSON",
                os.path.join(QtCore.QDir.homePath(), "mapping_data.json"),
                "JSON File (*.json)"
            )
    if filePath:
        global data
        global sourceData
        with open(filePath, "w") as f:
            # for source in sourceData:
                # temp = {}
                # temp["id"] = source.name
                # temp["strength"] = source.container.multiplyValue
                # data.append(temp)

            f.write(toJson(data) + "\n")

def loadDefaultData():
    filePath = ResPath + "\\resource\default_mapping_data.json"
    if filePath:
        # fileData = []
        with open(filePath) as f:
            fileData = (fromJson(f.read()))

        global data
        data = fileData
        # changeData()

def loadData():
    filePath, _ = PySide2.QtWidgets.QFileDialog.getOpenFileName(
                None,
                "Open Scene JSON File",
                os.path.join(QtCore.QDir.homePath(), "mapping_data.json"),
                "JSON File (*.json)"
            )
    if filePath:
        # fileData = []
        with open(filePath) as f:
            fileData = (fromJson(f.read()))

        global data
        data = fileData
        changeData()

def changeData():

    global data
    global sourceData

    for i in range(len(facewareList)):
        if data[i]["id"] == fmMappingUi.qtExpressionComboBox.currentText():
            for j in range(60):
                rlSliderRegularContainer[j].container.setValue(data[i]["feRegularData"][j]*100)
            for j in range(24):
                rlSliderCustomContainer[j].container.setValue(data[i]["feCustomData"][j]*100)
            for j in range(6):
                rlSliderBoneContainer[j].container.setValue(data[i]["feBoneData"][j]*100)
            for j in range(2):
                rlSliderEyeLContainer[j].container.setValue(data[i]["feEyeLData"][j]*100)
            for j in range(2):
                rlSliderEyeRContainer[j].container.setValue(data[i]["feEyeRData"][j]*100)
            for j in range(3):
                rlSliderHeadContainer[j].container.setValue(data[i]["feHeadData"][j]*100)
            break
    
    # for i in range(len(sourceData)):
    #     for j in range(len(data)):
    #         if data[j]["id"] == sourceData[i].name:
    #             try:
    #                 sourceData[i].container.setMultiplyValue(data[j]["strength"])
    #             except:
    #                 None
    showSlider()

def zeroExpressionData():
    tempRegularData = []
    for i in range(60):
        tempRegularData.append(0)
    tempCustomData = []
    for i in range(24):
        tempCustomData.append(0)
    script.ProcessFacePuppetKey(script.GetPickedObjectName(), script.ConvertTimeToFrame(script.GetCurrentTimeScript()),
                                [0, 0, 0], [0, 0], [0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                tempRegularData, tempCustomData)

def loop():
    device.loop()

def sliderStrengthChanged():
    global globalStrength
    globalStrength = fmMappingUi.qtGlobalStrengthSlider.value()
    fmMappingUi.qtGlobalStrengthSpinBox.setValue(globalStrength)

def spinboxStrengthChanged():
    global globalStrength
    globalStrength = fmMappingUi.qtGlobalStrengthSpinBox.value()
    fmMappingUi.qtGlobalStrengthSlider.setValue(globalStrength)

##########################
## UI
##########################
############################### MainUI fn ###############################

def openConnectDlg():
    global server_ip
    global server_port
    pos = mainWidget.mapToGlobal(PySide2.QtCore.QPoint(0, 0))
    fmDeviceConnectUi.show()
    fmDeviceConnectUi.move(pos.x()+360, pos.y())
    if fmDeviceConnectUi.radioButton_local.isChecked():
        server_ip = '127.0.0.1'
        server_port = int(fmDeviceConnectUi.lineEdit_localPort.text())
    elif fmDeviceConnectUi.radioButton_net.isChecked():
        server_ip = fmDeviceConnectUi.lineEdit_netIP.text()
        server_port = int(fmDeviceConnectUi.lineEdit_netPort.text())

def openMappingDlg():
    global mappingui_on
    global previewing
    global recording
    mappingui_on = True

    pos = mainWidget.mapToGlobal(PySide2.QtCore.QPoint(0, 0))
    Mapping_widget.show()
    Mapping_widget.move(pos.x()-625, pos.y()-30)

    feRegularData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feRegularData"]
    feCustomData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feCustomData"]
    feBoneData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feBoneData"]
    feEyeLData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feEyeLData"]
    feEyeRData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feEyeRData"]
    feHeadData = data[fmMappingUi.qtExpressionComboBox.currentIndex()]["feHeadData"]

    if not previewing and not recording:
        try:
            script.BeginFacePuppetKey(script.GetPickedObjectName(), 0, False)
        except:
            # debugMsg("BeginFacePuppetKey Error")
            pass
            script.ProcessFacePuppetKey(script.GetPickedObjectName(), 0, feHeadData, feEyeLData, feEyeRData,
                                        [0, 0, 0, 0, 0, 0, feBoneData[0], feBoneData[1], feBoneData[2], feBoneData[3],
                                         feBoneData[4], feBoneData[5]],
                                        feRegularData, feCustomData)
        try:
            script.EndFacePuppetKey(script.GetPickedObjectName(), 0)
        except:
            # debugMsg("EndFacePuppetKey Error")
            pass
        changeData()

def showDataSource():
    global mappingui_on
    if mappingui_on:
        pos = Mapping_widget.mapToGlobal(PySide2.QtCore.QPoint(0, 0))
    else:
        pos = mainWidget.mapToGlobal(PySide2.QtCore.QPoint(0, 0))
    fmDataSourceUi.show()
    fmDataSourceUi.move(pos.x()-540, pos.y())

def openICStreamingDlg():
    pos = mainWidget.mapToGlobal(PySide2.QtCore.QPoint(0, 0))
    iCStreamingUi.show()
    iCStreamingUi.move(pos.x()-598, pos.y()+30)

def mask_select_all():
    fmMainUi.qtBrowL_ckbox.setChecked(True)
    fmMainUi.qtBrowR_ckbox.setChecked(True)
    fmMainUi.qtEyeL_ckbox.setChecked(True)
    fmMainUi.qtEyeR_ckbox.setChecked(True)
    fmMainUi.qtCheekL_ckbox.setChecked(True)
    fmMainUi.qtCheekR_ckbox.setChecked(True)
    fmMainUi.qtNose_ckbox.setChecked(True)
    fmMainUi.qtMouth_ckbox.setChecked(True)
    fmMainUi.qtJaw_ckbox.setChecked(True)
    fmMainUi.qtEyeballL_ckbox.setChecked(True)
    fmMainUi.qtEyeballR_ckbox.setChecked(True)
    fmMainUi.qtHead_ckbox.setChecked(True)

def mask_clear_all():
    fmMainUi.qtBrowL_ckbox.setChecked(False)
    fmMainUi.qtBrowR_ckbox.setChecked(False)
    fmMainUi.qtEyeL_ckbox.setChecked(False)
    fmMainUi.qtEyeR_ckbox.setChecked(False)
    fmMainUi.qtCheekL_ckbox.setChecked(False)
    fmMainUi.qtCheekR_ckbox.setChecked(False)
    fmMainUi.qtNose_ckbox.setChecked(False)
    fmMainUi.qtMouth_ckbox.setChecked(False)
    fmMainUi.qtJaw_ckbox.setChecked(False)
    fmMainUi.qtEyeballL_ckbox.setChecked(False)
    fmMainUi.qtEyeballR_ckbox.setChecked(False)
    fmMainUi.qtHead_ckbox.setChecked(False)

def reset_smooth_all():
    fmMainUi.Slider_smHead.setValue(0)
    fmMainUi.Slider_smBrow.setValue(0)
    fmMainUi.Slider_smEye.setValue(0)
    fmMainUi.Slider_smEyeball.setValue(0)
    fmMainUi.Slider_smNose.setValue(0)
    fmMainUi.Slider_smCheek.setValue(0)
    fmMainUi.Slider_smMouth.setValue(0)
    fmMainUi.Slider_smJaw.setValue(0)
    fmMainUi.Slider_smCustom.setValue(0)

def reset_strength_all():
    fmMainUi.Slider_stHead.setValue(100)
    fmMainUi.Slider_stBrow.setValue(100)
    fmMainUi.Slider_stEye.setValue(100)
    fmMainUi.Slider_stEyeball.setValue(100)
    fmMainUi.Slider_stNose.setValue(100)
    fmMainUi.Slider_stCheek.setValue(100)
    fmMainUi.Slider_stMouth.setValue(100)
    fmMainUi.Slider_stJaw.setValue(100)
    fmMainUi.Slider_stCustom.setValue(100)

def mask_ckbox_to_masking_list():
    global masking_list

    # mask_ckbox_ary
    mask_ckbox_ary = [True, True, True, True, True, True, True, True, True, True, True, True]
    mask_ckbox_ary[0] = fmMainUi.qtBrowL_ckbox.isChecked()
    mask_ckbox_ary[1] = fmMainUi.qtBrowR_ckbox.isChecked()
    mask_ckbox_ary[2] = fmMainUi.qtEyeL_ckbox.isChecked()
    mask_ckbox_ary[3] = fmMainUi.qtEyeR_ckbox.isChecked()
    mask_ckbox_ary[4] = fmMainUi.qtCheekL_ckbox.isChecked()
    mask_ckbox_ary[5] = fmMainUi.qtCheekR_ckbox.isChecked()
    mask_ckbox_ary[6] = fmMainUi.qtNose_ckbox.isChecked()
    mask_ckbox_ary[7] = fmMainUi.qtMouth_ckbox.isChecked()
    mask_ckbox_ary[8] = fmMainUi.qtJaw_ckbox.isChecked()
    mask_ckbox_ary[9] = fmMainUi.qtEyeballL_ckbox.isChecked()
    mask_ckbox_ary[10] = fmMainUi.qtEyeballR_ckbox.isChecked()
    mask_ckbox_ary[11] = fmMainUi.qtHead_ckbox.isChecked()

    # Regular Expression
    browL = [0, 2, 4, 6]
    browR = [1, 3, 5, 7]
    eyeL = [9, 11, 13]
    eyeR = [10, 12, 14]
    eyeBoth = [8]
    CheekL = [20, 23, 26, 36, 54]
    CheekR = [21, 24, 27, 37, 55]
    CheekBoth = [22, 25]
    nose = [15, 16, 17, 18, 19]
    mouth = [28, 29, 30, 31, 32, 33, 34, 35, 38, 39, 40, 41, 42, 43, 44, 45,
             46, 47, 48, 49, 50, 51, 52, 53, 56, 57, 58, 59]
    re_exp = [browL, browR, eyeL, eyeR, CheekL, CheekR, nose, mouth, eyeBoth, CheekBoth]
    temp_exp = []

    for i in range(8):
        if not mask_ckbox_ary[i]:
            temp_exp.extend(re_exp[i])

    if not mask_ckbox_ary[2] and not mask_ckbox_ary[3]:
        temp_exp.extend(re_exp[8])
    if not mask_ckbox_ary[4] and not mask_ckbox_ary[5]:
        temp_exp.extend(re_exp[9])

    # Regular Expression
    temp_exp.sort()
    masking_list[0] = temp_exp

    # Jaw Bone / Eyeball / Head
    for i in range(1, 5):
        masking_list[i] = mask_ckbox_ary[i+7]

    return masking_list

def startPreview():
    global previewing

    if not previewing:
        # Check Picked Character
        if script.GetPickedObjectName() == "":
            return debugMsg("Please Pick A Character!")

        # Check TCP/IP Connect
        try:
            device.start()
        except:
            device.stop()
            return debugMsg("Connect Failed!\nPlease Check Port Or IP!")

        # if mappingui_on:
        #     Mapping_widget.close()

        # fmMainUi.qtMappingToolButton.setEnabled(False)
        fmMainUi.qtRecordPushButton.setEnabled(False)
        fmMainUi.qtPreviewPushButton.setText("Stop Preview")
        previewing = not previewing
        try:
            script.BeginFacePuppetKey(script.GetPickedObjectName(), script.GetCurrentTimeScript(), False)
        except:
            pass
            # debugMsg("BeginFacePuppetKey Error")

        scriptEvent.Append("Timer", "loop()", [1, -1])

    else:
        fmMainUi.qtRecordPushButton.setEnabled(True)
        # fmMainUi.qtMappingToolButton.setEnabled(True)
        fmMainUi.qtPreviewPushButton.setText("Start Preview")
        previewing = not previewing
        device.stop()
        zeroExpressionData()
        try:
            script.EndFacePuppetKey(script.GetPickedObjectName(),
                                    script.ConvertTimeToFrame(script.GetCurrentTimeScript()))
        except:
            pass
        scriptEvent.StopTimer()

def startRecord():
    global recording
    isBlend = fmMainUi.mask_blend_ckbox.isChecked()

    if not recording:
        # Check Picked Character
        if script.GetPickedObjectName() == "":
            return debugMsg("Please Pick A Character!")

        # Check TCP/IP Connect
        try:
            device.start()
        except:
            device.stop()
            return debugMsg("Connect Failed!\nPlease Check Port Or IP!")

        # if mappingui_on:
        #     Mapping_widget.close()

        # fmMainUi.qtMappingToolButton.setEnabled(False)
        fmMainUi.qtPreviewPushButton.setEnabled(False)
        fmMainUi.qtRecordPushButton.setText("Stop Record")
        recording = not recording
        try:
            script.BeginFacePuppetKey(script.GetPickedObjectName(),
                                      script.ConvertTimeToFrame(script.GetCurrentTimeScript()), isBlend)
        except:
            pass
            # debugMsg("BeginFacePuppetKey Error")
        script.Play()
        scriptEvent.Append("Timer", "loop()", [1, -1])

    else:
        fmMainUi.qtPreviewPushButton.setEnabled(True)
        # fmMainUi.qtMappingToolButton.setEnabled(True)
        fmMainUi.qtRecordPushButton.setText("Start Record")
        recording = not recording
        device.stop()
        try:
            script.EndFacePuppetKey(script.GetPickedObjectName(),
                                    script.ConvertTimeToFrame(script.GetCurrentTimeScript()))
        except:
            pass
        script.Stop()
        scriptEvent.StopTimer()

def showSlider():

    if fmMappingUi.qtShowAllSliderCheckBox.checkState():
        for i in range(len(rlSliderRegularContainer)):
            temp = rlSliderRegularContainer[i].container
            if temp.value == 0:
                temp.hide()
            else:
                temp.show()
        for i in range(len(rlSliderCustomContainer)):
            temp = rlSliderCustomContainer[i].container
            if temp.value == 0:
                temp.hide()
            else:
                temp.show()
        for i in range(len(rlSliderBoneContainer)):
            temp = rlSliderBoneContainer[i].container
            if temp.value == 0:
                temp.hide()
            else:
                temp.show()
        for i in range(len(rlSliderEyeLContainer)):
            temp = rlSliderEyeLContainer[i].container
            if temp.value == 0:
                temp.hide()
            else:
                temp.show()
        for i in range(len(rlSliderEyeRContainer)):
            temp = rlSliderEyeRContainer[i].container
            if temp.value == 0:
                temp.hide()
            else:
                temp.show()
        for i in range(len(rlSliderHeadContainer)):
            temp = rlSliderHeadContainer[i].container
            if temp.value == 0:
                temp.hide()
            else:
                temp.show()

    else:
        for i in range(len(rlSliderRegularContainer)):
            temp = rlSliderRegularContainer[i].container
            if not temp.isVisible():
                temp.show()
        for i in range(len(rlSliderCustomContainer)):
            temp = rlSliderCustomContainer[i].container
            if not temp.isVisible():
                temp.show()
        for i in range(len(rlSliderBoneContainer)):
            temp = rlSliderBoneContainer[i].container
            if not temp.isVisible():
                temp.show()
        for i in range(len(rlSliderEyeLContainer)):
            temp = rlSliderEyeLContainer[i].container
            if not temp.isVisible():
                temp.show()
        for i in range(len(rlSliderEyeRContainer)):
            temp = rlSliderEyeRContainer[i].container
            if not temp.isVisible():
                temp.show()
        for i in range(len(rlSliderHeadContainer)):
            temp = rlSliderHeadContainer[i].container
            if not temp.isVisible():
                temp.show()

def mappingSearchFilter():
    text = fmMappingUi.lineEdit_textFilter.text().strip().lower().replace(" ", "")
    showSlider()
    if text == "":
        return
    else:
        for i in range(len(rlSliderRegularContainer)):
            temp_name = rlSliderRegularContainer[i].name.strip().lower().replace(" ", "")
            if rlSliderRegularContainer[i].container.isVisible() and not (text in temp_name):
                rlSliderRegularContainer[i].container.hide()

        for i in range(len(rlSliderCustomContainer)):
            temp_name = rlSliderCustomContainer[i].name.strip().lower().replace(" ", "")
            if rlSliderCustomContainer[i].container.isVisible() and not (text in temp_name):
                rlSliderCustomContainer[i].container.hide()

        for i in range(len(rlSliderBoneContainer)):
            temp_name = rlSliderBoneContainer[i].name.strip().lower().replace(" ", "")
            if rlSliderBoneContainer[i].container.isVisible() and not (text in temp_name):
                rlSliderBoneContainer[i].container.hide()

        for i in range(len(rlSliderEyeLContainer)):
            temp_name = rlSliderEyeLContainer[i].name.strip().lower().replace(" ", "")
            if rlSliderEyeLContainer[i].container.isVisible() and not (text in temp_name):
                rlSliderEyeLContainer[i].container.hide()

        for i in range(len(rlSliderEyeRContainer)):
            temp_name = rlSliderEyeRContainer[i].name.strip().lower().replace(" ", "")
            if rlSliderEyeRContainer[i].container.isVisible() and not (text in temp_name):
                rlSliderEyeRContainer[i].container.hide()

        for i in range(len(rlSliderHeadContainer)):
            temp_name = rlSliderHeadContainer[i].name.strip().lower().replace(" ", "")
            if rlSliderHeadContainer[i].container.isVisible() and not (text in temp_name):
                rlSliderHeadContainer[i].container.hide()

def iCStreamingSearchFilter():
    text = iCStreamingUi.lineEdit_iCStreamFilter.text().strip().lower().replace(" ", "")
    if text == "":
        for i in iCStreamingData:
            i.container.show()
    else:
        for i in iCStreamingData:
            temp_name = i.name.strip().lower().replace(" ", "")
            if not (text in temp_name):
                i.container.hide()
            else:
                i.container.show()

############################### fmDeviceConnectUi fn ###############################

def fmLivce_localPort_changed():
    global server_ip
    global server_port
    if fmDeviceConnectUi.radioButton_local.isChecked():
        server_ip = '127.0.0.1'
        server_port = int(fmDeviceConnectUi.lineEdit_localPort.text())

def fmLivce_networkPort_changed():
    global server_port
    if fmDeviceConnectUi.radioButton_net.isChecked():
        server_port = int(fmDeviceConnectUi.lineEdit_netPort.text())

def fmLivce_networkIP_changed():
    global server_ip
    if fmDeviceConnectUi.radioButton_net.isChecked():
        server_ip = fmDeviceConnectUi.lineEdit_netIP.text()

############################### MainUi ###############################
app = PySide2.QtWidgets.QApplication.instance()
if not app:
    app = PySide2.QtWidgets.QApplication([])

loader = QUiLoader()
file = PySide2.QtCore.QFile(mainUI)
file.open(PySide2.QtCore.QFile.ReadOnly)
fmMainUi = loader.load(file)

mainWidget = resource.rlWidget.rlWidget()
hboxLayout = PySide2.QtWidgets.QVBoxLayout()
hboxLayout.setContentsMargins(0, 0, 0, 0)
mainWidget.setLayout(hboxLayout)
mainWidget.layout().addWidget(fmMainUi)
mainWidget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
mainWidget.init_pos()

############################### MainUi Btn ###############################

fmMainUi.connect_btn.clicked.connect(openConnectDlg)
fmMainUi.qtMappingToolButton.clicked.connect(openMappingDlg)
fmMainUi.qtiCloneStreamingButton.clicked.connect(openICStreamingDlg)
fmMainUi.qtPreviewPushButton.clicked.connect(startPreview)
fmMainUi.qtRecordPushButton.clicked.connect(startRecord)
fmMainUi.qtDataSourceButton.clicked.connect(showDataSource)
fmMainUi.mask_selectAll_btn.clicked.connect(mask_select_all)
fmMainUi.mask_clearAll_btn.clicked.connect(mask_clear_all)
fmMainUi.reset_sm_btn.clicked.connect(reset_smooth_all)
fmMainUi.reset_st_btn.clicked.connect(reset_strength_all)


############################### fmDeviceConnectUi ###############################

loader = QUiLoader()
file = PySide2.QtCore.QFile(deviceConnectUI)
file.open(PySide2.QtCore.QFile.ReadOnly)
fmDeviceConnectUi = loader.load(file)
fmDeviceConnectUi.setStyleSheet(icCss_style)
fmDeviceConnectUi.lineEdit_localPort.textChanged.connect(fmLivce_localPort_changed)
fmDeviceConnectUi.lineEdit_netPort.textChanged.connect(fmLivce_networkPort_changed)
fmDeviceConnectUi.lineEdit_netIP.textChanged.connect(fmLivce_networkIP_changed)
fmDeviceConnectUi.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
############################### fmMappingUi ###############################
loader = QUiLoader()
file = PySide2.QtCore.QFile(mappingUI)
file.open(PySide2.QtCore.QFile.ReadOnly)
fmMappingUi = loader.load(file)

Mapping_widget = rl_mapping_widget()
MappingLayout = PySide2.QtWidgets.QVBoxLayout()
Mapping_widget.setLayout(MappingLayout)
Mapping_widget.layout().addWidget(fmMappingUi)
Mapping_widget.setStyleSheet(icCss_style)
Mapping_widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
############################### fmMappingUi Btn ###############################
fmMappingUi.qtZeroAllPushButton.clicked.connect(zeroAll)
fmMappingUi.qtSavePushButton.clicked.connect(saveData)
fmMappingUi.qtLoadPushButton.clicked.connect(loadData)
fmMappingUi.qtShowAllSliderCheckBox.clicked.connect(showSlider)
fmMappingUi.qtDataSourcePushButton.clicked.connect(showDataSource)
fmMappingUi.qtGlobalStrengthSlider.valueChanged.connect(sliderStrengthChanged)
fmMappingUi.qtGlobalStrengthSpinBox.valueChanged.connect(spinboxStrengthChanged)
fmMappingUi.lineEdit_textFilter.textChanged.connect(mappingSearchFilter)

mainWidget.setRelatedWidget(Mapping_widget)

############################### Source & iC Streaming Ui ###############################
loader = QUiLoader()
file = PySide2.QtCore.QFile(dataSourceUI)
file.open(PySide2.QtCore.QFile.ReadOnly)
fmDataSourceUi = loader.load(file)
mainWidget.setRelatedWidget(fmDataSourceUi)
fmDataSourceUi.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

loader = QUiLoader()
file = PySide2.QtCore.QFile(dataSmoothUI)
file.open(PySide2.QtCore.QFile.ReadOnly)
fmDataSmoothUi = loader.load(file)
mainWidget.setRelatedWidget(fmDataSmoothUi)

loader = QUiLoader()
file = PySide2.QtCore.QFile(dataRangeUI)
file.open(PySide2.QtCore.QFile.ReadOnly)
fmDataRangeUi = loader.load(file)
mainWidget.setRelatedWidget(fmDataRangeUi)

loader = QUiLoader()
file = PySide2.QtCore.QFile(iCloneStreamingUI)
file.open(PySide2.QtCore.QFile.ReadOnly)
iCStreamingUi = loader.load(file)
mainWidget.setRelatedWidget(iCStreamingUi)
iCStreamingUi.lineEdit_iCStreamFilter.textChanged.connect(iCStreamingSearchFilter)
iCStreamingUi.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
############################### initUi ###############################
def initUi():
    
    global sourceData

    #### Add Sliders to fmDataSourceUi ####
    for i in range(len(facewareList)):
        temp = DataSourceID(facewareList[i], i, fmDataSourceUi.qtScrollAreaWidgetContents, 1)
        sourceData.append(temp)

    fmMappingUi.qtExpressionComboBox.addItems(facewareList)
    fmMappingUi.qtExpressionComboBox.currentTextChanged.connect(changeData)

    #### Add Sliders to fmMappingUi ####
    for i in range(60):
        temp = FacialID(feRegularList[i], i, fmMappingUi.qtMuscleContextWidget, "feRegularData")
        rlSliderRegularContainer.append(temp)

    for i in range(24):
        temp = FacialID(feCustomList[i], i, fmMappingUi.qtCustomContextWidget, "feCustomData")
        rlSliderCustomContainer.append(temp)

    for i in range(len(feBone)):
        temp = FacialID(feBone[i], i, fmMappingUi.qtBoneContextWidget, "feBoneData")
        rlSliderBoneContainer.append(temp)
   
    for i in range(len(feEyeL)):
        temp = FacialID(feEyeL[i], i, fmMappingUi.qtHeadEyeContextWidget, "feEyeLData")
        rlSliderEyeLContainer.append(temp)
    
    for i in range(len(feEyeR)):
        temp = FacialID(feEyeR[i], i, fmMappingUi.qtHeadEyeContextWidget, "feEyeRData")
        rlSliderEyeRContainer.append(temp)
    
    for i in range(len(feHead)):
        temp = FacialID(feHead[i], i, fmMappingUi.qtHeadEyeContextWidget, "feHeadData")
        rlSliderHeadContainer.append(temp)


    ##### Add Sliders to iClone Streaming UI ####
    for i in range(60):
        temp = Data_iCloneID(feRegularList[i], i, iCStreamingUi.streamMuscleContext, 1)
        iCStreamingData.append(temp)

    for i in range(24):
        temp = Data_iCloneID(feCustomList[i], i, iCStreamingUi.streamCustomContext, 1)
        iCStreamingData.append(temp)

    for i in range(len(feBone)):
        temp = Data_iCloneID(feBone[i], i, iCStreamingUi.streamBoneContext, 1)
        iCStreamingData.append(temp)

    for i in range(len(feEyeL)):
        temp = Data_iCloneID(feEyeL[i], i, iCStreamingUi.streamHeadEyeContext, 1)
        iCStreamingData.append(temp)

    for i in range(len(feEyeR)):
        temp = Data_iCloneID(feEyeR[i], i, iCStreamingUi.streamHeadEyeContext, 1)
        iCStreamingData.append(temp)

    for i in range(len(feHead)):
        temp = Data_iCloneID(feHead[i], i, iCStreamingUi.streamHeadEyeContext, 1)
        iCStreamingData.append(temp)

    global device
    device = Faceware_live()

initUi()
mainWidget.setDevice(device)
mainWidget.show()
loadDefaultData()
# zeroExpressionData()
