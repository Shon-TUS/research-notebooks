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

