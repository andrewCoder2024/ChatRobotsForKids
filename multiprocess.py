#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Process, Pipe
import psutil
from time import sleep
from chatbot_m import main
from cam.pan_tilt_tracking import run

#https://stackoverflow.com/questions/43861164/passing-data-between-separately-running-python-scripts

if __name__ == "__main__":
    try:
        # Create and start the child process
        parent_conn, child_conn = Pipe()
        p = Process(target=run, args=())
        p2 = Process(target=main, args=(child_conn,))
        p.start()
        p2.start()
        pid = p.pid  # Get the pid of the child process
        pause = psutil.Process(pid)  # pass in the pid of the child process
        # Test Pause Child Process
        while True:
            rec = parent_conn.recv()
            if rec == "stop":
                pause.suspend()  # Pause the child process
                #print('The child process is suspended')
            elif rec == "cont":
                pause.resume()  # Resume the child process
                #print('\nThe child process has resumed operation')
    except KeyboardInterrupt:
        print("ending")
