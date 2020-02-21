
JOINTS = ['Root_M',
          'COM_M',
          'Spine1_M',
          'Spine2_M',
          'Spine3_M',
          'Chest_M',
          'Neck_M',
          'Head_M',
          'HeadEnd_M',
          'Jaw_M',
          'JawEnd_M',
          'Hip_R',
          'Knee_R',
          'Ankle_R',
          'Toes_R',
          'ToesEnd_R',
          'Breast_R',
          'BreastEnd_R',
          'Clavicle_R',
          'Shoulder_R',
          'Elbow_R',
          'Wrist_R',
          'FingerThumb1_R',
          'FingerThumb2_R',
          'FingerThumb3_R',
          'FingerThumbEnd_R',
          'FingerIndex1_R',
          'FingerIndex2_R',
          'FingerIndex3_R',
          'FingerIndexEnd_R',
          'FingerMiddle1_R',
          'FingerMiddle2_R',
          'FingerMiddle3_R',
          'FingerMiddleEnd_R',
          'FingerRing1_R',
          'FingerRing2_R',
          'FingerRing3_R',
          'FingerRingEnd_R',
          'FingerPinky1_R',
          'FingerPinky2_R',
          'FingerPinky3_R',
          'FingerPinkyEnd_R',
          'Eye_R',
          'EyeEnd_R',
          'Hip_L',
          'Knee_L',
          'Ankle_L',
          'Toes_L',
          'ToesEnd_L',
          'Breast_L',
          'BreastEnd_L',
          'Clavicle_L',
          'Shoulder_L',
          'Elbow_L',
          'Wrist_L',
          'FingerThumb1_L',
          'FingerThumb2_L',
          'FingerThumb3_L',
          'FingerThumbEnd_L',
          'FingerIndex1_L',
          'FingerIndex2_L',
          'FingerIndex3_L',
          'FingerIndexEnd_L',
          'FingerMiddle1_L',
          'FingerMiddle2_L',
          'FingerMiddle3_L',
          'FingerMiddleEnd_L',
          'FingerRing1_L',
          'FingerRing2_L',
          'FingerRing3_L',
          'FingerRingEnd_L',
          'FingerPinky1_L',
          'FingerPinky2_L',
          'FingerPinky3_L',
          'FingerPinkyEnd_L',
          'Eye_L',
          'EyeEnd_L']

TREE = {'Root_M': None,
        'COG_M': 'Root_M',
        'Spine1_M': 'COG_M',
        'Spine2_M': 'Spine1_M',
        'Spine3_M': 'Spine2_M',
        'Chest_M': 'Spine3_M',
        'Neck_M': 'Chest_M',
        'Head_M': 'Neck_M',
        'HeadEnd_M': 'Head_M',
        'Jaw_M': 'Head_M',
        'JawEnd_M': 'Jaw_M',
        'Hip_R': 'COG_M',
        'Knee_R': 'Hip_R',
        'Ankle_R': 'Knee_R',
        'Toes_R': 'Ankle_R',
        'ToesEnd_R': 'Toes_R',
        'Breast_R': 'Spine3_M',
        'BreastEnd_R':'Breast_R',
        'Clavicle_R': 'Chest_M',
        'Shoulder_R': 'Clavicle_R',
        'Elbow_R': 'Shoulder_R',
        'Wrist_R': 'Elbow_R',
        'FingerThumb1_R': 'Wrist_R',
        'FingerThumb2_R': 'Wrist_R',
        'FingerThumb3_R': 'Wrist_R',
        'FingerThumbEnd_R': 'Wrist_R',
        'FingerIndex1_R': 'Wrist_R',
        'FingerIndex2_R': 'Wrist_R',
        'FingerIndex3_R': 'Wrist_R',
        'FingerIndexEnd_R': 'Wrist_R',
        'FingerMiddle1_R': 'Wrist_R',
        'FingerMiddle2_R': 'Wrist_R',
        'FingerMiddle3_R': 'Wrist_R',
        'FingerMiddleEnd_R': 'Wrist_R',
        'FingerRing1_R': 'Wrist_R',
        'FingerRing2_R': 'Wrist_R',
        'FingerRing3_R': 'Wrist_R',
        'FingerRingEnd_R': 'Wrist_R',
        'FingerPinky1_R': 'Wrist_R',
        'FingerPinky2_R': 'Wrist_R',
        'FingerPinky3_R': 'Wrist_R',
        'FingerPinkyEnd_R': 'Wrist_R',
        'Eye_R': 'Head_M',
        'EyeEnd_R': 'Eye_R',
        'Hip_L': 'COG_M',
        'Knee_L': 'Hip_L',
        'Ankle_L': 'Knee_L',
        'Toes_L': 'Ankle_L',
        'ToesEnd_L': 'Toes_L',
        'Breast_L': 'Spine3_M',
        'BreastEnd_L':'Breast_L',
        'Clavicle_L': 'Chest_M',
        'Shoulder_L': 'Clavicle_L',
        'Elbow_L': 'Shoulder_L',
        'Wrist_L': 'Elbow_L',
        'FingerThumb1_L': 'Wrist_L',
        'FingerThumb2_L': 'Wrist_L',
        'FingerThumb3_L': 'Wrist_L',
        'FingerThumbEnd_L': 'Wrist_L',
        'FingerIndex1_L': 'Wrist_L',
        'FingerIndex2_L': 'Wrist_L',
        'FingerIndex3_L': 'Wrist_L',
        'FingerIndexEnd_L': 'Wrist_L',
        'FingerMiddle1_L': 'Wrist_L',
        'FingerMiddle2_L': 'Wrist_L',
        'FingerMiddle3_L': 'Wrist_L',
        'FingerMiddleEnd_L': 'Wrist_L',
        'FingerRing1_L': 'Wrist_L',
        'FingerRing2_L': 'Wrist_L',
        'FingerRing3_L': 'Wrist_L',
        'FingerRingEnd_L': 'Wrist_L',
        'FingerPinky1_L': 'Wrist_L',
        'FingerPinky2_L': 'Wrist_L',
        'FingerPinky3_L': 'Wrist_L',
        'FingerPinkyEnd_L': 'Wrist_L',
        'Eye_L': 'Head_M',
        'EyeEnd_L': 'Eye_L'}
