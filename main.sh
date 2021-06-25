#!/bin/bash
sudo python3 cam/pan_tilt_tracking.py --cascade cam/haarcascade_eye_tree_eyeglasses.xml &
sudo python3 chatbot.py && fg
