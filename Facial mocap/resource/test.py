# import script
import PySide2
from PySide2.QtWidgets import QWidget

mirRegularData = [2, 1, 4, 3, 6, 5, 8, 7, 9, 11, 10, 13, 12, 15, 14, 16, 17, 19, 18, 20,
                  22, 21, 23, 25, 24, 26, 28, 27, 29, 31, 30, 32, 33, 34, 35, 36, 38, 37,
                  39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 48, 51, 50, 52, 53, 54, 56, 55,
                  57, 58, 59, 60]


feBone = ["07.JawRotateY", "08.JawRotateZ", "09.JawRotateX", "10.JawMoveX", "11.JawMoveY", "12.JawMoveZ"]

feEyeL = ["EyeL_rightLeft_l", "EyeL_downUp_l"]

feEyeR = ["EyeR_rightLeft_r", "EyeR_downUp_r"]

feHead = ["Head_up_down", "Head_right_left", "Head_tilt"]

# def debugMsg(_str):
#     _text = str(_str)
#     info_dialog = PySide2.QtWidgets.QMessageBox()
#     info_dialog.setWindowTitle('Debug Window')
#     info_dialog.setText(_text)
#     info_dialog.exec_()
#
# debugMsg(script.GetPickedObjectName())
for i in range(len(mirRegularData)):
    # print i
    print mirRegularData[i]-1
