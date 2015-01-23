from cv2 import (CAP_PROP_FRAME_HEIGHT,
                 CAP_PROP_FRAME_WIDTH,
                 COLOR_BGR2RGB,
                 cvtColor,
                 VideoCapture,
                 VideoWriter,
                 VideoWriter_fourcc,
                 )
from numpy import ndarray
from PyQt4.QtCore import Qt, QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt4.Qt import QCoreApplication
from PyQt4.QtGui import (QHBoxLayout,
                         QImage,
                         QLabel,
                         QPixmap,
                         QPushButton,
                         QVBoxLayout,
                         QWidget,
                         )


webcam_size = 320, 240
refresh_rate = 24.
videofile = r'C:\Users\cashlab\Documents\data\output.avi'
codecs = 'MJPG'  # 'DIVX' or 'MJPG' or 'Ysomething'

from sys import exit
from PyQt4.QtGui import QApplication, QMainWindow
from time import sleep


class Worker(QObject):
    """
    """
    newframe = pyqtSignal(ndarray)

    @pyqtSlot()
    def start_task(self):
        print(2)
        self.cap = VideoCapture(0)
        self.cap.set(CAP_PROP_FRAME_WIDTH, webcam_size[0])
        self.cap.set(CAP_PROP_FRAME_HEIGHT, webcam_size[1])

        fourcc = VideoWriter_fourcc(*codecs)
        self.out = VideoWriter(videofile, fourcc, refresh_rate, webcam_size)

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            sleep(0.5)
            if ret:
                self.out.write(frame)
                frame = cvtColor(frame, COLOR_BGR2RGB)
                self.newframe.emit(frame)

    def stop_task(self):
        self.cap.release()
        self.out.release()


class ControlPanel(QWidget):
    """Widget to start and stop the recordings.
    """
    def __init__(self):
        super(ControlPanel, self).__init__()  # py2

        push = QPushButton()
        push.setText('Start')
        self.push_start = push

        push = QPushButton()
        push.setText('Stop')
        self.push_stop = push

        layout = QVBoxLayout(self)
        layout.addWidget(self.push_start)
        layout.addWidget(self.push_stop, 1, Qt.AlignTop)


class Webcam(QWidget):
    """Main widget with the traces.

    """
    def __init__(self):
        super(Webcam, self).__init__()  # py2

        control = ControlPanel()
        control.push_start.clicked.connect(self.start_acq)
        control.push_stop.clicked.connect(self.stop_acq)

        self.label = QLabel()
        self.label.setGeometry(0, 0, *webcam_size)

        layout = QHBoxLayout()
        layout.addWidget(control, 1)
        layout.addWidget(self.label, 5)
        self.setLayout(layout)

    def start_acq(self):
        """Start acquisition by starting a new thread.
        """
        thread = QThread()
        self.thread = thread
        obj = Worker()
        self.obj = obj
        obj.newframe.connect(self.update_webcam)
        obj.moveToThread(thread)

        thread.started.connect(obj.start_task)
        thread.start()
        thread.quit()  # why does it go here?

    def stop_acq(self):
        """End acquisition.
        """
        self.obj.stop_task()

    def update_webcam(self, frame):
        """Update the data matrix with the recordings and plot it

        Parameters
        ----------
        data : ndarray
            matrix with the incoming recordings
        """
        print(frame[0])
        img = QImage(frame, webcam_size[0], webcam_size[1],
                     QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(img))
        QCoreApplication.processEvents()


class MainWindow(QMainWindow):
    """Main Window that holds all the widgets (traces with raw signal, webcam
    and other behavioral data.)"""
    def __init__(self):
        super(MainWindow, self).__init__()
        self.traces = Webcam()
        self.setCentralWidget(self.traces)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    exit(app.exec_())
