#!/usr/bin/env python3

from argparse import ArgumentParser
from os.path import realpath, join, dirname
from sys import path, exit

from PyQt4.QtCore import (QSettings,
                          Qt,
                          )
from PyQt4.QtGui import (QApplication,
                         QDockWidget,
                         QMainWindow,
                         )

# ADD MODULE
opbox_path = realpath(join(dirname(realpath(__file__)), '..'))
path.append(opbox_path)
from opbox.ui import Camera

# INPUT ARGUMENTS
parser = ArgumentParser(prog='choose_camera',
                        description='GUI to choose camera')
parser.add_argument('-n', default=1,
                    help='Number of camera connected')
parser.add_argument('--cam_size', type=str, default='320x240',
                    help='Camera size (default: 320x240)')
parser.add_argument('--cam_timer', type=int, default=5,
                    help='How often the camera should be read, in ms (default: 5)')
parser.add_argument('--cam_fps', type=int, default=30,
                    help='Frames per second of the camera (default: 30)')
args = parser.parse_args()
args.camera_size = [int(i) for i in args.cam_size.split('x')]


class MainWindow(QMainWindow):
    """Main Window that holds all the cameras"""
    def __init__(self):
        super(MainWindow, self).__init__()  # py2

        all_cam = []
        for i in range(args.n):
            cam = Camera(args)
            dock_cam = QDockWidget('Camera', self)
            dock_cam.setWidget(cam)
            dock_cam.setObjectName('Camera')
            self.addDockWidget(Qt.TopDockWidgetArea, dock_cam)
            all_cam.append(cam)

        for one_cam in all_cam:
            one_cam.start()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    exit(app.exec_())
