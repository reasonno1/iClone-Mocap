import script, scriptEvent
import os, sys, socket, struct
import PySide2
from PySide2 import shiboken2
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.shiboken2 import wrapInstance 
from PySide2.QtCore import QThread
import imp, time, thread, threading, json, math, Queue

######################
## GLOBAL VARIABLES 
######################

NAME = None
obarray = []
dataFromX = None
frame = 0

# BODY PARTS #
pelvis = None; l5 = None; l3 = None; t12 = None; t8 = None; neck = None; head = None; rish = None
riua = None; rifa = None; riha = None; lesh = None; leua = None; lefa = None; leha = None; 
riul = None; rill = None; rifo = None; rito = None; leul = None; lell = None; lefo = None; leto = None;
# BODY PART NAMES #
bodypart_names = ['_pelvis', '_l5', '_l3', '_t12', '_t8', '_neck', '_head', '_rightshoulder',
                  '_rightupperarm', '_rightforearm', '_righthand', '_leftshoulder', '_leftupperarm', '_leftforearm', '_lefthand',
                  '_rightupperleg', '_rightlowerleg', '_rightfoot', '_righttoe', '_leftupperleg', '_leftlowerleg', '_leftfoot', '_lefttoe']
isTpose = True
testbool = True
#############   
## CLASSES 
#############

class Quaternion:
    def __init__ ( self, x, y, z, w ):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.data = (x,y,z,w)
    
    def clamp ( self, _value, _min, _max ):
        return max( _min, min( _max, _value ) )
    
    def makeRotationFromQuaternion( self, q ):
        te = range(16)
        x = q.x; y = q.y; z = q.z; w = q.w
        x2 = x + x; y2 = y + y; z2 = z + z
        xx = x * x2; xy = x * y2; xz = x * z2
        yy = y * y2; yz = y * z2; zz = z * z2
        wx = w * x2; wy = w * y2; wz = w * z2

        te[ 0 ] = 1 - ( yy + zz );
        te[ 4 ] = xy - wz;
        te[ 8 ] = xz + wy;

        te[ 1 ] = xy + wz;
        te[ 5 ] = 1 - ( xx + zz );
        te[ 9 ] = yz - wx;

        te[ 2 ] = xz - wy;
        te[ 6 ] = yz + wx;
        te[ 10 ] = 1 - ( xx + yy );

        #last column
        te[ 3 ] = 0;
        te[ 7 ] = 0;
        te[ 11 ] = 0;

        #bottom row
        te[ 12 ] = 0;
        te[ 13 ] = 0;
        te[ 14 ] = 0;
        te[ 15 ] = 1;
    
        return te
    
    def setFromRotationMatrix ( self, m, order ):
        m11 = m[ 0 ]
        m12 = m[ 4 ]
        m13 = m[ 8 ]
        m21 = m[ 1 ]
        m22 = m[ 5 ]
        m23 = m[ 9 ]
        m31 = m[ 2 ]
        m32 = m[ 6 ]
        m33 = m[ 10 ]

        e = Euler(0,0,0,'XYZ')
        
        if ( order == 'XYZ' ):
            e.y = math.asin( self.clamp( m13, - 1, 1 ) );
            if ( math.fabs( m13 ) < 0.99999 ):
                e.x = math.atan2( - m23, m33 );
                e.z = math.atan2( - m12, m11 );
            else:
                e.x = math.atan2( m32, m22 );
                e.z = 0;
        elif ( order == 'YXZ' ):
            e.x = math.asin( - self.clamp( m23, - 1, 1 ) );
            if ( math.fabs( m23 ) < 0.99999 ):
                e.y = math.atan2( m13, m33 );
                e.z = math.atan2( m21, m22 );
            else:
                e.y = math.atan2( - m31, m11 );
                e.z = 0;
        elif ( order == 'ZXY' ):
            e.x = math.asin( self.clamp( m32, - 1, 1 ) );
            if ( math.fabs( m32 ) < 0.99999 ):
                e.y = math.atan2( - m31, m33 );
                e.z = math.atan2( - m12, m22 );
            else:
                e.y = 0;
                e.z = math.atan2( m21, m11 );
        elif ( order == 'ZYX' ):
            e.y = math.asin( - self.clamp( m31, - 1, 1 ) );
            if ( math.fabs( m31 ) < 0.99999 ):
                e.x = math.atan2( m32, m33 );
                e.z = math.atan2( m21, m11 );
            else:
                e.x = 0;
                e.z = math.atan2( - m12, m22 );
        elif ( order == 'YZX' ):
            e.z = math.asin( self.clamp( m21, - 1, 1 ) );
            if ( math.fabs( m21 ) < 0.99999 ):
                e.x = math.atan2( - m23, m22 );
                e.y = math.atan2( - m31, m11 );
            else:
                e.x = 0;
                e.y = math.atan2( m13, m33 );
        elif ( order == 'XZY' ):
            e.z = math.asin( - self.clamp( m12, - 1, 1 ) );
            if ( math.fabs( m12 ) < 0.99999 ):
                e.x = math.atan2( m32, m22 );
                e.y = math.atan2( m13, m11 );
            else:
                e.x = math.atan2( - m23, m33 );
                e.y = 0;
        else:
            print "error"
        
        e.x = math.degrees(e.x)
        e.y = math.degrees(e.y)
        e.z = math.degrees(e.z)
        
        e.data = ( (e.x), (e.y), (e.z) )
        
        return e
    
    def toE( self, order ):
        return self.setFromRotationMatrix ( self.makeRotationFromQuaternion( self ), order )
  
class Euler:
    def __init__ ( self, x, y, z, order ):
        self.x = x
        self.y = y
        self.z = z
        self.order = order
        self.data = (x,y,z,order)
    
    def toQ( self ):
        c1 = math.cos( math.radians( self.x / 2 ) )
        c2 = math.cos( math.radians( self.y / 2 ) )
        c3 = math.cos( math.radians( self.z / 2 ) )
        s1 = math.sin( math.radians( self.x / 2 ) )
        s2 = math.sin( math.radians( self.y / 2 ) )
        s3 = math.sin( math.radians( self.z / 2 ) )
        
        q = Quaternion(0,0,0,0)
        
        if ( self.order == 'XYZ' ):
            q.x = s1 * c2 * c3 + c1 * s2 * s3;
            q.y = c1 * s2 * c3 - s1 * c2 * s3;
            q.z = c1 * c2 * s3 + s1 * s2 * c3;
            q.w = c1 * c2 * c3 - s1 * s2 * s3;
        elif ( self.order == 'YXZ' ):
            q.x = s1 * c2 * c3 + c1 * s2 * s3;
            q.y = c1 * s2 * c3 - s1 * c2 * s3;
            q.z = c1 * c2 * s3 - s1 * s2 * c3;
            q.w = c1 * c2 * c3 + s1 * s2 * s3;
        elif ( self.order == 'ZXY' ):
            q.x = s1 * c2 * c3 - c1 * s2 * s3;
            q.y = c1 * s2 * c3 + s1 * c2 * s3;
            q.z = c1 * c2 * s3 + s1 * s2 * c3;
            q.w = c1 * c2 * c3 - s1 * s2 * s3;
        elif ( self.order == 'ZYX' ):
            q.x = s1 * c2 * c3 - c1 * s2 * s3;
            q.y = c1 * s2 * c3 + s1 * c2 * s3;
            q.z = c1 * c2 * s3 - s1 * s2 * c3;
            q.w = c1 * c2 * c3 + s1 * s2 * s3;
        elif ( self.order == 'YZX' ):
            q.x = s1 * c2 * c3 + c1 * s2 * s3;
            q.y = c1 * s2 * c3 + s1 * c2 * s3;
            q.z = c1 * c2 * s3 - s1 * s2 * c3;
            q.w = c1 * c2 * c3 - s1 * s2 * s3;
        elif ( self.order == 'XZY' ):
            q.x = s1 * c2 * c3 - c1 * s2 * s3;
            q.y = c1 * s2 * c3 - s1 * c2 * s3;
            q.z = c1 * c2 * s3 + s1 * s2 * c3;
            q.w = c1 * c2 * c3 + s1 * s2 * s3;
        else:
            print ("error")
        
        q.data = (q.x,q.y,q.z,q.w)
        return q

class transformation:
                trantuple = None
                rotatuple = None 
                
                #translation and rotation variables
                tranx = None
                trany = None
                tranz = None
                    
                rotx = None
                roty = None
                rotz = None
                    
                ID = None

def getDetail():
    global NAME, pelvis, l5, l3, t12, t8, neck, head
    global rish, riua, rifa, riha, lesh, leua, lefa, leha
    global riul, rill, rifo, rito, leul, lell, lefo, leto
    global obarray
        
    pelvis = transformation(); l5 = transformation(); l3 = transformation(); t12 = transformation(); t8 = transformation(); neck = transformation();
    head = transformation(); rish = transformation(); riua = transformation(); rifa = transformation(); riha = transformation();
    lesh = transformation(); leua = transformation(); lefa = transformation(); leha = transformation(); riul = transformation();
    rill = transformation(); rifo = transformation(); rito = transformation(); leul = transformation(); lell = transformation()
    lefo = transformation(); leto = transformation();

    # place in list of objects
    obarray = [pelvis, l5, l3, t12, t8, neck, head, rish, riua, rifa, riha, lesh, leua, lefa, leha, riul, rill, rifo, rito, leul, lell, lefo, leto]

getDetail()

def dist(a1, a2, a3, b1, b2, b3):
    d1 = (a1 - b1)**2
    d2 = (a2 - b2)**2
    d3 = (a3 - b3)**2
    return math.sqrt(d1 + d2 + d3)

def setBonePos(parent, x, y, z):

    childX = parent[0] + x
    childY = parent[1] + y
    childZ = parent[2] + z

    child = (childX, childY, childZ, 0, 0, 0)

    return child


def sendToIC():
    global frame
    hip = (pelvis.tranx, pelvis.trany, pelvis.tranz, pelvis.rotx, pelvis.roty, pelvis.rotz)
    rUpLeg = (riul.tranx, riul.trany, riul.tranz, riul.rotx, riul.roty, riul.rotz)
    rLeg = (rill.tranx, rill.trany, rill.tranz, rill.rotx, rill.roty, rill.rotz)
    rFoot = (rifo.tranx, rifo.trany, rifo.tranz, rifo.rotx, rifo.roty, rifo.rotz)
    
    lUpLeg = (leul.tranx, leul.trany, leul.tranz, leul.rotx, leul.roty, leul.rotz)
    lLeg = (lell.tranx, lell.trany, lell.tranz, lell.rotx, lell.roty, lell.rotz)
    lFoot = (lefo.tranx, lefo.trany, lefo.tranz, lefo.rotx, lefo.roty, lefo.rotz)
    
    chest1 = (l5.tranx, l5.trany, l5.tranz, l5.rotx, l5.roty, l5.rotz)
    #chest2 = (l3.tranx, l3.trany, l3.tranz, l3.rotx, l3.roty, l3.rotz)
    chest2 = (t12.tranx, t12.trany, t12.tranz, t12.rotx, t12.roty, t12.rotz)
    chest3 = (t8.tranx, t8.trany, t8.tranz, t8.rotx, t8.roty, t8.rotz)
    
    neck1 = (neck.tranx, neck.trany, neck.tranz, neck.rotx, neck.roty, neck.rotz)
    head1 = (head.tranx, head.trany, head.tranz, head.rotx, head.roty, head.rotz)
    
    rShoulder = (rish.tranx, rish.trany, rish.tranz, rish.rotx, rish.roty, rish.rotz)
    rArm = (riua.tranx, riua.trany, riua.tranz, riua.rotx, riua.roty, riua.rotz)
    rForearm = (rifa.tranx, rifa.trany, rifa.tranz, rifa.rotx, rifa.roty, rifa.rotz)
    rHand = (riha.tranx, riha.trany, riha.tranz, riha.rotx, riha.roty, riha.rotz)
    
    lShoulder = (lesh.tranx, lesh.trany, lesh.tranz, lesh.rotx, lesh.roty, lesh.rotz)
    lArm = (leua.tranx, leua.trany, leua.tranz, leua.rotx, leua.roty, leua.rotz)
    lForearm = (lefa.tranx, lefa.trany, lefa.tranz, lefa.rotx, lefa.roty, lefa.rotz)
    lHand = (leha.tranx, leha.trany, leha.tranz, leha.rotx, leha.roty, leha.rotz)

    rToe = (rito.tranx, rito.trany, rito.tranz, rito.rotx, rito.roty, rito.rotz)
    lToe = (leto.tranx, leto.trany, leto.tranz, leto.rotx, leto.roty, leto.rotz)
    
    #print getXsensDataByIndex(21,received)
    
    #23*6 = 138
    
    values = hip + rUpLeg + rLeg + rFoot+ lUpLeg + lLeg + lFoot + chest1 + chest2 + chest3 + neck1 + head1 + rShoulder + rArm + rForearm + rHand + lShoulder + lArm + lForearm + lHand + rToe + lToe
    s = struct.Struct('!132f')
    packed_data = s.pack(*values)
    Datas = struct.unpack('!132f', packed_data)
    Result = []

    for item in range(0, 132, 1):
        Result.append(Datas[item])
    transferToIC(Result)

    global isTpose
    if isTpose:
        tpose_hip = (0, 0, 0, 0, 0, 0)

        ## Legs ##
        dUpleg = dist(rUpLeg[0], rUpLeg[1], rUpLeg[2], hip[0], hip[1], hip[2])
        dLeg = dist(rLeg[0], rLeg[1], rLeg[2], rUpLeg[0], rUpLeg[1], rUpLeg[2])
        dFoot = dist(rFoot[0], rFoot[1], rFoot[2], rLeg[0], rLeg[1], rLeg[2])
        dToe = dist(rToe[0], rToe[1], rToe[2], rFoot[0], rFoot[1], rFoot[2])

        tpose_rUpLeg = setBonePos(tpose_hip, -dUpleg, 0, 0)
        tpose_rLeg = setBonePos(tpose_rUpLeg, 0, 0, -dLeg)
        tpose_rFoot = setBonePos(tpose_rLeg, 0, 0, -dFoot)
        tpose_rToe = setBonePos(tpose_rFoot, 0, 0, -dToe)

        tpose_lUpLeg = setBonePos(tpose_hip, dUpleg, 0, 0)
        tpose_lLeg = setBonePos(tpose_lUpLeg, 0, 0, -dLeg)
        tpose_lFoot = setBonePos(tpose_lLeg, 0, 0, -dFoot)
        tpose_lToe = setBonePos(tpose_lFoot, 0, 0, -dToe)

        ## Chest & Head ##
        dChest1 = dist(chest1[0], chest1[1], chest1[2], hip[0], hip[1], hip[2])
        dChest2 = dist(chest2[0], chest2[1], chest2[2], chest1[0], chest1[1], chest1[2])
        dChest3 = dist(chest3[0], chest3[1], chest3[2], chest2[0], chest2[1], chest2[2])
        dNeck = dist(neck1[0], neck1[1], neck1[2], chest3[0], chest3[1], chest3[2])
        dHead = dist(head1[0], head1[1], head1[2], neck1[0], neck1[1], neck1[2])

        tpose_chest1 = setBonePos(tpose_hip, 0, 0, dChest1)
        tpose_chest2 = setBonePos(tpose_chest1, 0, 0, dChest2)
        tpose_chest3 = setBonePos(tpose_chest2, 0, 0, dChest3)
        tpose_neck1 = setBonePos(tpose_chest3, 0, 0, dNeck)
        tpose_head1 = setBonePos(tpose_neck1, 0, 0, dHead)

        ## Arm ##
        dShoulder = dist(rShoulder[0], rShoulder[1], rShoulder[2], chest3[0], chest3[1], chest3[2] + (dNeck/2))
        dArm = dist(rArm[0], rArm[1], rArm[2], rShoulder[0], rShoulder[1], rShoulder[2])
        dForearm = dist(rForearm[0], rForearm[1], rForearm[2], rArm[0], rArm[1], rArm[2])
        dHand = dist(rHand[0], rHand[1], rHand[2], rForearm[0], rForearm[1], rForearm[2])

        tpose_rShoulder = setBonePos(tpose_chest3, -dShoulder, 0, dNeck/2)
        tpose_rArm = setBonePos(tpose_rShoulder, -dArm, 0, 0)
        tpose_rForearm = setBonePos(tpose_rArm, -dForearm, 0, 0)
        tpose_rHand = setBonePos(tpose_rForearm, -dHand, 0, 0)

        tpose_lShoulder = setBonePos(tpose_chest3, dShoulder, 0, dNeck/2)
        tpose_lArm = setBonePos(tpose_lShoulder, dArm, 0, 0)
        tpose_lForearm = setBonePos(tpose_lArm, dForearm, 0, 0)
        tpose_lHand = setBonePos(tpose_lForearm, dHand, 0, 0)

        ## Sum ##
        values = tpose_hip + tpose_rUpLeg + tpose_rLeg + tpose_rFoot + tpose_lUpLeg + tpose_lLeg + tpose_lFoot + tpose_chest1 + tpose_chest2 + tpose_chest3 + tpose_neck1 + tpose_head1 + tpose_rShoulder + tpose_rArm + tpose_rForearm + tpose_rHand + tpose_lShoulder + tpose_lArm + tpose_lForearm + tpose_lHand + tpose_rToe + tpose_lToe

        s = struct.Struct('!132f')
        packed_data = s.pack(*values)
        Datas = struct.unpack('!132f', packed_data)
        TposeData = []

        for item in range(0, 132, 1):
            TposeData.append(Datas[item])

        script.SetDeviceMultiPuppetTPose(script.GetPickedObjectName(), TposeData, 132)
        isTpose = False

    # global testbool
    # if testbool:
    #     debugMsg(Result)
    #     testbool = False

    try:
        script.ProcessMocapData(Result, 132, script.ConvertTimeToFrame(script.GetCurrentTimeScript()))
    except:
        debugMsg("error")
    frame = frame + 1

def transform():
    global obarray
    global bodypart_names
    global NAME
    global dataFromX
    if dataFromX == None:
        return
    # points to index in the message [dataFromX]
    index_pointer = 24
    # points to index in the object array [objectarray]
    array_pointer = 0
    # points to index in the segmentbox array [segmentbox]
    segmentbox_pointer = 0
    # keep track of the float cycles
    cycle_counter = 1
    
    objid = None
    # 4 bytes will be unpacked to one single precision type (float) #
    byte1 = None 
    byte2 = None
    byte3 = None 
    byte4 = None
    # floatcontainer1-6 are xyz translation and xyz rotation #
    fcon1 = None #x tran
    fcon2 = None #y tran
    fcon3 = None #z tran
    fcon4 = None #x rot
    fcon5 = None #y rot
    fcon6 = None #z rot
    #array that holds segment parts
    segmentbox = [objid, fcon1, fcon2, fcon3, fcon4, fcon5, fcon6]
    #print (len(dataFromX))
    # validate euler message #
    if len(dataFromX) == 668:
        #print("valid")
        # Beginning of the post-processing round #
        while index_pointer < 668: 
           
            # object segment ID calculation #
            byte1 = dataFromX[index_pointer] #first round 24
            index_pointer += 1
            byte2 = dataFromX[index_pointer]
            index_pointer += 1
            byte3 = dataFromX[index_pointer]
            index_pointer += 1
            byte4 = dataFromX[index_pointer] #first round 27
            index_pointer += 1

            segmentbox[segmentbox_pointer] = byte1+byte2+byte3+byte4
            #print(byte1,byte2,byte3,byte4);
            segmentbox[segmentbox_pointer] = struct.unpack('>i', segmentbox[segmentbox_pointer])
            #print("Current ID: ", segmentbox[segmentbox_pointer]);

            # place ID in 'item.ID'
            obarray[array_pointer].ID = segmentbox[segmentbox_pointer][0] 
            # point to next part of the segment
            segmentbox_pointer += 1 
            
            # end of segment ID calculation #
            
            # Beginning of the 'float cycles' #
            for cycle in range(6):
            
                #print(index_pointer)
                byte1 = dataFromX[index_pointer]
                index_pointer += 1
                byte2 = dataFromX[index_pointer]
                index_pointer += 1
                byte3 = dataFromX[index_pointer]
                index_pointer += 1
                byte4 = dataFromX[index_pointer] 
                index_pointer += 1          

                #merge into a fcon
                segmentbox[segmentbox_pointer] = byte1+byte2+byte3+byte4
                segmentbox[segmentbox_pointer] = struct.unpack('>f', segmentbox[segmentbox_pointer])
                #print(segmentbox[segmentbox_pointer])
                # python has no switch statement .. #
                if cycle_counter == 1:
                    obarray[array_pointer].tranx = segmentbox[segmentbox_pointer][0]
                    cycle_counter += 1
                elif cycle_counter == 2:
                    obarray[array_pointer].trany = segmentbox[segmentbox_pointer][0]
                    cycle_counter += 1
                elif cycle_counter == 3:
                    obarray[array_pointer].tranz = segmentbox[segmentbox_pointer][0]
                    cycle_counter += 1
                elif cycle_counter == 4:
                    obarray[array_pointer].rotx = segmentbox[segmentbox_pointer][0]
                    cycle_counter += 1
                elif cycle_counter == 5:
                    obarray[array_pointer].roty = segmentbox[segmentbox_pointer][0]
                    cycle_counter += 1
                elif cycle_counter == 6:
                    obarray[array_pointer].rotz = segmentbox[segmentbox_pointer][0]
                    cycle_counter = 1 #reset counter to 1 at last cycle
                

                segmentbox_pointer += 1 
                
            # at the end of the float cycles :
            obarray[array_pointer].trantuple = (obarray[array_pointer].tranx, obarray[array_pointer].trany, obarray[array_pointer].tranz)
            obarray[array_pointer].rotatuple = (obarray[array_pointer].rotx, obarray[array_pointer].roty, obarray[array_pointer].rotz)
            
            # point to next segment for post-processing
            array_pointer += 1
            segmentbox_pointer = 0

        sendToIC()

class Vector3:
    def __init__ ( self, x, y, z ):
        self.x = x
        self.y = y
        self.z = z

class Matrix3:
    def __init__ ( self, x1, x2, x3, y1, y2, y3, z1, z2, z3 ):
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.z1 = z1
        self.z2 = z2
        self.z3 = z3
    def FromEulerAngle( self, order, fRadianX, fRadianY, fRadianZ):
        if ( order == 'XYZ' ):
            vSin = Vector3( math.sin( fRadianX ), math.sin( fRadianY ), math.sin( fRadianZ ) )
            vCos = Vector3( math.cos( fRadianX ), math.cos( fRadianY ), math.cos( fRadianZ ) )
            self.x1 = vCos.y * vCos.z
            self.x2 = vCos.y * vSin.z
            self.x3 = -vSin.y
            self.y1 = vSin.x * vSin.y * vCos.z - vCos.x * vSin.z;
            self.y2 = vSin.x * vSin.y * vSin.z + vCos.x * vCos.z;
            self.y3 = vSin.x * vCos.y;
            self.z1 = vCos.x * vSin.y * vCos.z + vSin.x * vSin.z;
            self.z2 = vCos.x * vSin.y * vSin.z - vSin.x * vCos.z;
            self.z3 = vCos.x * vCos.y;
    def ToEulerAngle( self, order, rxyz ):
         if ( order == 'XYZ' ):
            if ( ( 1.0 - math.fabs( self.x3 ) ) < 0.00001 ):
                if ( self.x3 < 0.0):
                    rxyz[1] = math.pi/2
                else:
                    rxyz[1] = -math.pi/2;
                rxyz[0] = math.atan2( self.y1, self.z1 );
                if ( self.x3 > 0.0 ):
                    rxyz[0] +=  math.pi;
                rxyz[2] = 0.0;
            else:
                rxyz[0] = math.atan2( self.y3, self.z3 );
                if ( math.fabs( math.fabs( rxyz[0] ) - math.pi ) < 0.00001 ):
                    t = self.y3 / math.sin( rxyz[0] );
                else:
                    t = self.z3 / math.cos( rxyz[0] );
                rxyz[1] = math.atan2( -self.x3, t );
                rxyz[2] = math.atan2( self.x2, self.x1 );

def VecMultiMatix( kPos, mMatrix ):
    kPosResult = Vector3( 0, 0, 0 )
    kPosResult.x = kPos.x * mMatrix.x1 + kPos.y * mMatrix.y1 + kPos.z * mMatrix.z1
    kPosResult.y = kPos.x * mMatrix.x2 + kPos.y * mMatrix.y2 + kPos.z * mMatrix.z2
    kPosResult.z = kPos.x * mMatrix.x3 + kPos.y * mMatrix.y3 + kPos.z * mMatrix.z3
    kPos.x = kPosResult.x
    kPos.y = kPosResult.y
    kPos.z = kPosResult.z

def transferToIC( Result ):
    for item in range( 0, 132 / 6, 1 ):
        kPos = Vector3( Result[ item*6 + 0 ], Result[ item*6 + 1 ], Result[ item*6 + 2 ] )
        mAxisTransform = Matrix3( 1, 0, 0, 0, 1, 0, 0, 0, 1 )
        mRotate = Matrix3( 1, 0, 0, 0, 1, 0, 0, 0, 1 )
        fAngle = math.pi * 0.5
        tCos = math.cos( fAngle )
        tSin = math.sin( fAngle )
        mAxisTransform.x1 = 1
        mAxisTransform.x2 = 0
        mAxisTransform.x3 = 0
        mAxisTransform.y1 = 0
        mAxisTransform.y2 = tCos
        mAxisTransform.y3 = tSin
        mAxisTransform.z1 = 0
        mAxisTransform.z2 = -tSin
        mAxisTransform.z3 = tCos
        #print 'mAxisTransform:', mAxisTransform.x1, mAxisTransform.x2, mAxisTransform.x3, mAxisTransform.y1, mAxisTransform.y2, mAxisTransform.y3, mAxisTransform.z1, mAxisTransform.z2, mAxisTransform.z3
        #print 'before pos:'
        #print kPos.x, kPos.y, kPos.z
        VecMultiMatix( kPos, mAxisTransform )
        #print 'after pos:'
        #print kPos.x, kPos.y, kPos.z
        mRotate.FromEulerAngle('XYZ', Result[ item * 6 + 3 ] / 180 * math.pi, Result[ item * 6 + 4 ] / 180 * math.pi, Result[ item * 6 + 5 ] / 180 * math.pi )
        vX = Vector3( mRotate.x1, mRotate.x2, mRotate.x3 )
        vY = Vector3( mRotate.y1, mRotate.y2, mRotate.y3 )
        vZ = Vector3( mRotate.z1, mRotate.z2, mRotate.z3 )
        #print 'rotate before:', mRotate.x1, mRotate.x2, mRotate.x3, mRotate.y1, mRotate.y2, mRotate.y3, mRotate.z1, mRotate.z2, mRotate.z3
        mRotate.x1 = vX.x
        mRotate.x2 = -vX.z
        mRotate.x3 = vX.y
        mRotate.y1 = -vZ.x
        mRotate.y2 = vZ.z
        mRotate.y3 = -vZ.y
        mRotate.z1 = vY.x
        mRotate.z2 = -vY.z
        mRotate.z3 = vY.y
        #print 'rotate after:', mRotate.x1, mRotate.x2, mRotate.x3, mRotate.y1, mRotate.y2, mRotate.y3, mRotate.z1, mRotate.z2, mRotate.z3
        rxyz = [  0.0, 0.0, 0.0 ]
        mRotate.ToEulerAngle('XYZ', rxyz)
        #print 'rotation'
        #print rxyz[ 0 ], rxyz[ 1 ], rxyz[ 2 ]
        Result[ item*6 + 0 ] = kPos.x
        Result[ item*6 + 1 ] = kPos.y
        Result[ item*6 + 2 ] = kPos.z
        Result[ item*6 + 3 ] = rxyz[ 0 ]
        Result[ item*6 + 4 ] = rxyz[ 1 ]
        Result[ item*6 + 5 ] = rxyz[ 2 ]

class MyCacheBuffer():
    def __init__(self):
        self.queue = Queue.Queue(maxsize = 10)
        self.lock = False
    def SetData( self, dataX ):
        if self.queue.qsize() == 10:
            return
        while self.lock == True:
            pass
        self.lock = True
        print 'setData'
        self.queue.put(dataX)
        self.lock = False
    def GetData(self):
        global dataFromX
        if self.queue.qsize() == 0:
            dataFromX = None
            return
        while self.lock == True: 
            print 'Locking'
        self.lock = True
        print 'GetData'
        dataFromX = self.queue.get()
        while self.queue.qsize() != 0:
            self.queue.get()
        self.lock = False

class DataRecvThread(QThread):
        def __init__(self, n, parent = None):
                QThread.__init__(self, parent)
                self.exiting = False
                self.index = n
                self.sock = None
        def connect(self):
            if self.sock == None:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind(('localhost', 9763))
                self.sock.settimeout(0.5)
                try:
                    if self.exiting == False:
                        self.exiting = True
                except socket.timeout:
                    self.exiting = False
            
        def disconnect(self):
            self.exiting = False
            try:
                self.sock.close()
            except:
                debugMsg("Close Error")
        def run(self):
            global CacheBuf
            while self.exiting == True:

                if self.sock != None:
                    dataX = self.sock.recv(64*1024)
                    CacheBuf.SetData( dataX )


def debugMsg(_str):
    info_dialog = PySide2.QtWidgets.QMessageBox()
    info_dialog.setWindowTitle('Xsens Debug Window')
    info_dialog.setText(str(_str))
    info_dialog.exec_()
                            
def Loop():
    global CacheBuf
    CacheBuf.GetData()
    transform()

def Stop():
    script.EndMocapAPI()

previewing = False
recording = False

def StartPreviewClick():
    global previewing
    global index
    global RevThread
    global HandMask

    isHandMask = HandMask.isChecked()

    if not previewing:

        if (script.GetPickedObjectName() == ""):
            return
        if RevThread != None:
            return
        previewing = not previewing
        RecordBtn.setEnabled(False)
        PreviewBtn.setText("Stop Preview")

        RevThread = DataRecvThread(1)
        RevThread.connect()
        RevThread.start()

        script.SetDataWithParent(
            [[1, 1], [5, 1], [6, 5], [7, 6], [2, 1], [3, 2], [4, 3], [8, 1], [23, 8], [24, 23], [20, 24], [15, 20],
             [19, 24], [12, 19], [13, 12], [14, 13], [18, 24], [9, 18], [10, 9], [11, 10], [17, 7], [16, 4]])
        script.SetRotationOrder(0)
        try:
            script.BeginMocapAPI(script.GetPickedObjectName(), False, False)
            script.SetActivePart(script.GetPickedObjectName(), False, False, False, False, isHandMask, isHandMask,
                                 False, False, True, False)
            scriptEvent.Append("Timer", "Loop()", [1, -1])
        except:
            debugMsg("Wrong Target")
        
    else:
        RecordBtn.setEnabled(True)
        PreviewBtn.setText("Start Preview")
        previewing = not previewing
        Stop()
        script.Stop()
        scriptEvent.StopTimer()

        RevThread.disconnect()
        RevThread.quit()
        RevThread.wait()
        RevThread = None
        # CacheBuf = MyCacheBuffer()
        script.EndCommand()
        #
        # global testbool
        # if not testbool:
        #     testbool = True

        global isTpose
        if not isTpose:
            isTpose = True

def StartRecordClick():
    global recording
    global index
    global RevThread
    global HandMask

    isHandMask = HandMask.isChecked()
    RecordWithFace = RecordPlay.isChecked()


    if not recording:

        if (script.GetPickedObjectName() == ""):
            return
        if RevThread != None:
            return
        recording = not recording
        PreviewBtn.setEnabled(False)
        RecordBtn.setText("Stop Record")

        RevThread = DataRecvThread(1)
        RevThread.connect()
        RevThread.start()

        script.SetDataWithParent(
            [[1, 1], [5, 1], [6, 5], [7, 6], [2, 1], [3, 2], [4, 3], [8, 1], [23, 8], [24, 23], [20, 24], [15, 20],
             [19, 24], [12, 19], [13, 12], [14, 13], [18, 24], [9, 18], [10, 9], [11, 10], [17, 7], [16, 4]])
        script.SetRotationOrder(0)
        try:
            script.BeginMocapAPI(script.GetPickedObjectName(), True, False)
            script.SetActivePart(script.GetPickedObjectName(), False, False, False, False, isHandMask, isHandMask,
                                 False, False, True, False)

            if not RecordWithFace:
                script.Play()

            scriptEvent.Append("Timer", "Loop()", [1, -1])
        except:
            debugMsg("Wrong Target")

    else:

        PreviewBtn.setEnabled(True)
        RecordBtn.setText("Start Record")
        recording = not recording
        Stop()
        # script.Stop()
        scriptEvent.StopTimer()

        RevThread.disconnect()
        RevThread.quit()
        RevThread.wait()
        RevThread = None
        # CacheBuf = MyCacheBuffer()
        script.EndCommand()

        # global testbool
        # if not testbool:
        #     testbool = True

        global isTpose
        if not isTpose:
            isTpose = True


##############################################################################
app = PySide2.QtWidgets.QApplication.instance()
if not app:
  app = PySide2.QtWidgets.QApplication ([])
index = 0

CacheBuf = MyCacheBuffer()

RevThread = None

MainWindowptr = script.GetMainWindow()
MainWindow = wrapInstance( MainWindowptr, PySide2.QtWidgets.QMainWindow )
qPushButtonStyle = 'QPushButton{font-size:12px;text-align:center; min-height:23px;color:#c8c8c8;background-color:#282828; border:1px solid #505050; } QPushButton:hover{color:#c8c8c8;background-color:#505050; } QPushButton:pressed{color:#000000;background-color:#c8c8c8; } QPushButton:selected{color:#000000;background-color:#c8c8c8;} QPushButton:checked{color:#000000;background-color:#c8c8c8;} QPushButton:disabled{color:#464646;border:1px solid #3c3c3c;}'


myDockWidget = PySide2.QtWidgets.QDockWidget("Xsens")
myDockWidget.setAllowedAreas(PySide2.QtCore.Qt.LeftDockWidgetArea | PySide2.QtCore.Qt.RightDockWidgetArea)
MainWindow.addDockWidget( PySide2.QtCore.Qt.LeftDockWidgetArea, myDockWidget)
myDockWidget.setFloating(True)

# qCharacterNameEditText = PySide2.QtWidgets.QLineEdit()
# qCharacterNameEditText.setPlaceholderText("Please Enter Your Character's Name")

myWidget = PySide2.QtWidgets.QWidget()
myBtnLayout = PySide2.QtWidgets.QVBoxLayout()
PreviewBtn = PySide2.QtWidgets.QPushButton("Start Preview")
PreviewBtn.setStyleSheet(qPushButtonStyle)
RecordBtn = PySide2.QtWidgets.QPushButton("Start Record")
RecordBtn.setStyleSheet(qPushButtonStyle)
HandMask = PySide2.QtWidgets.QCheckBox("Mask Hand")
HandMask.setChecked(True)
HandMask.setStyleSheet(qPushButtonStyle)
RecordPlay = PySide2.QtWidgets.QCheckBox("Recording With Facial")
RecordPlay.setChecked(False)
RecordPlay.setStyleSheet(qPushButtonStyle)

# myBtnLayout.addWidget( qCharacterNameEditText )

myBtnLayout.addWidget(HandMask)
myBtnLayout.addWidget(PreviewBtn)
myBtnLayout.addWidget(RecordBtn)
myBtnLayout.addWidget(RecordPlay)
myWidget.setLayout(myBtnLayout)
PreviewBtn.clicked.connect(StartPreviewClick)
RecordBtn.clicked.connect(StartRecordClick)


myDockWidget.setWidget(myWidget)
myDockWidget.show()
