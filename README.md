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

When executed, the script will save the skeleton estimation results obtained using OpenPose as a CSV file.

Although the generated MOV file with the estimated skeleton is not used during training, it will also be output.

