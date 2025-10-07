# Project name
Estimating Seated Postures from Acoustic Signals using Python

## Overview
We perform skeletal estimation of seated postures using Python.

As inputs, the program requires a WAV file of audio signals, a CSV file containing the ground-truth posture labels for each frame, and a TXT file used for synchronization.

As output, a MOV file with the estimated skeleton is generated.

This program is an adaptation of the paper ***“Listening Human Behavior: 3D Human Pose Estimation with Acoustic Signals”*** to seated postures, and its overall workflow follows that of the original paper.

## Usage

**1.Equipment Used**

・Intel RealSense Depth Camera D455

・FOCUSRITE Scarlett 18i20

・8 Piezo Microphones

・Speaker

・Armchair

**2.Setup Procedure**

Place the Intel RealSense Depth Camera D455 facing the armchair.

Adjust the camera so that the entire body is visible.

Next, place the speaker and the 8 piezo microphones behind the chair.

Connect the installed speaker and piezo microphones to the FOCUSRITE Scarlett 18i20.

Finally, connect your computer to the FOCUSRITE Scarlett 18i20.

At this time, please make sure that Focusrite Control is installed on your computer.

**3.Experiment**

3-1.Make chrip sounds

Please run Make_Chirp.py in the Experiment folder.

When executed, it generates chirp sounds for the duration specified.

Modify num_chirps according to the length of time you want to record.

(For example, if num_chirps = 3000, a WAV file containing 300 seconds of chirp sounds will be created.)

3-2.Start Experiment

Run record.py in the same folder.

When executed, video recording and audio recording will start simultaneously.

**4.Preprocessing**

4-1.Data preprocessing

Run skeletal_estimation.py located in the Preprocessing folder.

Before running, please change the MOV file name specified in the code.

When executed, the script will save the skeleton estimation results obtained using MediaPipe as a CSV file.

Although the generated MOV file with the estimated skeleton is not used during training, it will also be output.

Next, run csv_conversion.py.

Before executing, please change the CSV file name specified in the code.

This script converts the 33 pose landmarks from MediaPipe into a 21-joint Humanoid structure and saves the result as a CSV file.

Please note that this process is designed to follow the model described in ***“Listening Human Behavior: 3D Human Pose Estimation with Acoustic Signals.”***

The following table shows the correspondence between MediaPipe and Humanoid joints.

| No. | **Humanoid Joint** | **Computation (from MediaPipe points)** | **Description**                                                  |
| --: | ------------------ | --------------------------------------- | ---------------------------------------------------------------- |
|   1 | **Hips**           | (left_hip + right_hip) / 2              | Midpoint between the left and right hips (center of the pelvis). |
|   2 | **Spine**          | (Hips + Neck) / 2                       | Midpoint between hips and neck — lower spine.                    |
|   3 | **Spine1**         | (Spine + Neck) / 2                      | Midpoint between spine and neck — upper spine (chest).           |
|   4 | **Neck**           | (left_shoulder + right_shoulder) / 2    | Midpoint between shoulders — base of the neck.                   |
|   5 | **Head**           | nose                                    | Center of the face (nose).                                       |
|   6 | **LeftShoulder**   | left_shoulder                           | Left shoulder joint.                                             |
|   7 | **LeftArm**        | (left_shoulder + left_elbow) / 2        | Midpoint between shoulder and elbow — upper arm.                 |
|   8 | **LeftForeArm**    | left_elbow                              | Left elbow joint.                                                |
|   9 | **LeftHand**       | left_wrist                              | Left wrist joint.                                                |
|  10 | **RightShoulder**  | right_shoulder                          | Right shoulder joint.                                            |
|  11 | **RightArm**       | (right_shoulder + right_elbow) / 2      | Midpoint between shoulder and elbow — upper arm.                 |
|  12 | **RightForeArm**   | right_elbow                             | Right elbow joint.                                               |
|  13 | **RightHand**      | right_wrist                             | Right wrist joint.                                               |
|  14 | **LeftUpLeg**      | left_hip                                | Left upper leg (hip joint).                                      |
|  15 | **LeftLeg**        | left_knee                               | Left knee joint.                                                 |
|  16 | **LeftFoot**       | left_ankle                              | Left ankle joint.                                                |
|  17 | **LeftToeBase**    | left_foot_index                         | Left toe base (tip of the foot).                                 |
|  18 | **RightUpLeg**     | right_hip                               | Right upper leg (hip joint).                                     |
|  19 | **RightLeg**       | right_knee                              | Right knee joint.                                                |
|  20 | **RightFoot**      | right_ankle                             | Right ankle joint.                                               |
|  21 | **RightToeBase**   | right_foot_index                        | Right toe base (tip of the foot).                                |

