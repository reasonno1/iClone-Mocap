
#################################  Class  #################################

class Vector3:
    def __init__ ( self, x, y, z ):
        self.x = x
        self.y = y
        self.z = z

#################################  Class Matrix3  #################################

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

        vSin = Vector3(math.sin(fRadianX), math.sin(fRadianY), math.sin(fRadianZ))
        vCos = Vector3(math.cos(fRadianX), math.cos(fRadianY), math.cos(fRadianZ))
        if( order == 'XYZ' ):

            self.x1 = vCos.y * vCos.z
            self.x2 = vCos.y * vSin.z
            self.x3 = -vSin.y
            self.y1 = vSin.x * vSin.y * vCos.z - vCos.x * vSin.z
            self.y2 = vSin.x * vSin.y * vSin.z + vCos.x * vCos.z
            self.y3 = vSin.x * vCos.y
            self.z1 = vCos.x * vSin.y * vCos.z + vSin.x * vSin.z
            self.z2 = vCos.x * vSin.y * vSin.z - vSin.x * vCos.z
            self.z3 = vCos.x * vCos.y

        elif(order == 'YXZ'):

            self.x1 = vCos.y * vCos.z - vSin.x * vSin.y * vSin.z
            self.x2 = vCos.y * vSin.z + vSin.x * vSin.y * vCos.z
            self.x3 = -vCos.x * vSin.y
            self.y1 = -vCos.x * vSin.z
            self.y2 = vCos.x * vCos.z
            self.y3 = vSin.x
            self.z1 = vSin.y * vCos.z + vSin.x * vCos.y * vSin.z;
            self.z2 = vSin.y * vSin.z - vSin.x * vCos.y * vCos.z;
            self.z3 = vCos.x * vCos.y;

    def ToEulerAngle( self, order, rxyz ):
         if ( order == 'XYZ' ):
            if ( ( 1.0 - math.fabs( self.x3 ) ) < 0.00001 ):
                if ( self.x3 < 0.0):
                    rxyz[1] = math.pi/2
                else:
                    rxyz[1] = -math.pi/2
                rxyz[0] = math.atan2( self.y1, self.z1 )
                if ( self.x3 > 0.0 ):
                    rxyz[0] += math.pi
                rxyz[2] = 0.0
            else:
                rxyz[0] = math.atan2( self.y3, self.z3 )
                if ( math.fabs( math.fabs( rxyz[0] ) - math.pi ) < 0.00001 ):
                    t = self.y3 / math.sin( rxyz[0] )
                else:
                    t = self.z3 / math.cos( rxyz[0] )
                rxyz[1] = math.atan2( -self.x3, t )
                rxyz[2] = math.atan2( self.x2, self.x1 )

         elif(order == "YXZ"):
            if((1.0 - math.fabs(self.y3)) < 0.00001):
                if(self.y3 > 0.0):
                    rxyz[0] = math.pi / 2
                else:
                    rxyz[0] = -math.pi / 2
                rxyz[1] = 0.0;
                rxyz[2] = math.atan2(self.x2, self.x1)
            else:
                rxyz[1] = -math.atan2(self.x3, self.z3)
                rxyz[2] = -math.atan2(self.y1, self.y2)
                if(math.fabs((math.fabs(rxyz[2]) - math.pi / 2) < 0.00001)):
                    t = -self.y1 / math.sin(rxyz[2])
                else:
                    t = self.y2 / math.cos(rxyz[2]);
                rxyz[0] = math.atan2(self.y3, t)

#################################  Class leap_listener  #################################

class leap_listener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        # Get hands
        for hand in frame.hands:
            global rh_palm
            global lh_palm

            hand_ary = lh if hand.is_left else rh

            # Rot Matrix3x3
            leap_hand_mat = hand.arm.basis.to_array_3x3()
            if hand.is_right:
                hand_mat = Matrix3(leap_hand_mat[6], leap_hand_mat[7], leap_hand_mat[8],
                                   leap_hand_mat[3], leap_hand_mat[4], leap_hand_mat[5],
                                   -leap_hand_mat[0], -leap_hand_mat[1], -leap_hand_mat[2])

            else:
                hand_mat = Matrix3(-leap_hand_mat[6], -leap_hand_mat[7], -leap_hand_mat[8],
                                   leap_hand_mat[3], leap_hand_mat[4], leap_hand_mat[5],
                                   -leap_hand_mat[0], -leap_hand_mat[1], -leap_hand_mat[2])



            hand_euler = [0, 0, 0]
            hand_mat.ToEulerAngle('XYZ', hand_euler)
            hand_pos = hand.arm.wrist_position
            # Y-up hand transform
            hand_transform = [hand_pos[0]/10, hand_pos[1]/10, hand_pos[2]/10,
                              hand_euler[0]-(90*math.pi/180), hand_euler[1], hand_euler[2]]
            # Z-up hand transform
            transferToIC(hand_transform)

            zhand_mat = Matrix3(1, 0, 0, 0, 1, 0, 0, 0, 1)
            zhand_mat.FromEulerAngle("XYZ", hand_transform[3], hand_transform[4], hand_transform[5])



            # hand world TRS Matirx4x4
            hand_world = np.mat([(zhand_mat.x1, zhand_mat.x2, zhand_mat.x3, 0),
                                 (zhand_mat.y1, zhand_mat.y2, zhand_mat.y3, 0),
                                 (zhand_mat.z1, zhand_mat.z2, zhand_mat.z3, 0),
                                 (hand_transform[0], hand_transform[1], hand_transform[2], 1)])


            hand_world_inv = hand_world.I

            hand_ary[0] = hand_transform

            for finger in hand.fingers:
                # Get bones
                # print finger.type

                for b in range(0, 4):
                    bone = finger.bone(b)
                    leap_bone_mat = bone.basis.to_array_3x3()

                    if hand.is_right:
                        bone_mat = Matrix3(leap_bone_mat[6], leap_bone_mat[7], leap_bone_mat[8],
                                           leap_bone_mat[3], leap_bone_mat[4], leap_bone_mat[5],
                                           -leap_bone_mat[0], -leap_bone_mat[1], -leap_bone_mat[2])
                    else:
                        bone_mat = Matrix3(-leap_bone_mat[6], -leap_bone_mat[7], -leap_bone_mat[8],
                                           leap_bone_mat[3], leap_bone_mat[4], leap_bone_mat[5],
                                           -leap_bone_mat[0], -leap_bone_mat[1], -leap_bone_mat[2])

                    bone_euler = [0, 0, 0]
                    bone_mat.ToEulerAngle("XYZ", bone_euler)
                    # Y-up bone transform
                    bone_transform = [bone.prev_joint[0]/10, bone.prev_joint[1]/10, bone.prev_joint[2]/10,
                                      bone_euler[0], bone_euler[1], bone_euler[2]]

                    # Z-up bone transform
                    transferToIC(bone_transform)

                    zbone_mat = Matrix3(1, 0, 0, 0, 1, 0, 0, 0, 1)
                    zbone_mat.FromEulerAngle("XYZ", bone_transform[3]-(90*math.pi/180), bone_transform[4], bone_transform[5])

                    # bone World Matirx4x4
                    bone_world = np.mat([(zbone_mat.x1, zbone_mat.x2, zbone_mat.x3, 0),
                                         (zbone_mat.y1, zbone_mat.y2, zbone_mat.y3, 0),
                                         (zbone_mat.z1, zbone_mat.z2, zbone_mat.z3, 0),
                                         (bone_transform[0], bone_transform[1], bone_transform[2], 1)])


                    #child_local = child_world * parent_world_Inverse
                    bone_local = np.array(np.matmul(bone_world, hand_world_inv))
                    hand_ary[finger.type + 1][b] = bone_local

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            pass

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"


#################################  VecMultiMatix  #################################

def VecMultiMatix( kPos, mMatrix ):
    kPosResult = Vector3( 0, 0, 0 )
    kPosResult.x = kPos.x * mMatrix.x1 + kPos.y * mMatrix.y1 + kPos.z * mMatrix.z1
    kPosResult.y = kPos.x * mMatrix.x2 + kPos.y * mMatrix.y2 + kPos.z * mMatrix.z2
    kPosResult.z = kPos.x * mMatrix.x3 + kPos.y * mMatrix.y3 + kPos.z * mMatrix.z3
    kPos.x = kPosResult.x
    kPos.y = kPosResult.y
    kPos.z = kPosResult.z

#################################  transferToIC  #################################

def transferToIC( Result ):

    kPos = Vector3(Result[0], Result[1], Result[2])
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

    VecMultiMatix( kPos, mAxisTransform )

    mRotate.FromEulerAngle('XYZ', Result[3], Result[4], Result[5])
    vX = Vector3( mRotate.x1, mRotate.x2, mRotate.x3 )
    vY = Vector3( mRotate.y1, mRotate.y2, mRotate.y3 )
    vZ = Vector3( mRotate.z1, mRotate.z2, mRotate.z3 )
    mRotate.x1 = vX.x
    mRotate.x2 = -vX.z
    mRotate.x3 = vX.y
    mRotate.y1 = -vZ.x
    mRotate.y2 = vZ.z
    mRotate.y3 = -vZ.y
    mRotate.z1 = vY.x
    mRotate.z2 = -vY.z
    mRotate.z3 = vY.y
    rxyz = [0.0, 0.0, 0.0]
    mRotate.ToEulerAngle('XYZ', rxyz)
    Result[0] = kPos.x
    Result[1] = kPos.y
    Result[2] = kPos.z
    Result[3] = rxyz[0]+90*math.pi/180
    Result[4] = rxyz[1]
    Result[5] = rxyz[2]

##################################################################################################
