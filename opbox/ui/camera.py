from cv2 import (CAP_PROP_FRAME_HEIGHT,
                 CAP_PROP_FRAME_WIDTH,
                 COLOR_BGR2RGB,
                 cvtColor,
                 VideoCapture,
                 VideoWriter,
                 VideoWriter_fourcc,
                 )
from numpy import ndarray
from PyQt4.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt4.QtGui import (QImage,
                         QLabel,
                         QPixmap,
                         )


videofile = r'C:\Users\cashlab\Documents\data\output.avi'
codecs = 'XVID'  # 'DIVX' or 'MJPG' or 'XVID' or 'IYUV'
write = False


class Worker(QObject):
    """
    """
    newframe = pyqtSignal(ndarray)

    def __init__(self, args):
        super(Worker, self).__init__()
        self.args = args

    @pyqtSlot()
    def start(self):
        self.cap = VideoCapture(0)
        self.cap.set(CAP_PROP_FRAME_WIDTH, self.args.camera_size[0])
        self.cap.set(CAP_PROP_FRAME_HEIGHT, self.args.camera_size[1])

        if write:
            fourcc = VideoWriter_fourcc(*codecs)
            self.out = VideoWriter(videofile, fourcc, float(self.args.cam_fps),
                                   self.args.camera_size)

        if self.cap.isOpened():
            self.timer = QTimer()
            self.timer.setInterval(self.args.cam_timer)
            self.timer.timeout.connect(self.run)
            self.timer.start()

    def run(self):

        running, frame = self.cap.read()
        if running:
            # do opencv processing
            if write:
                self.out.write(frame)
            frame = cvtColor(frame, COLOR_BGR2RGB)
            self.newframe.emit(frame)

    @pyqtSlot()
    def stop(self):
        self.timer.stop()
        self.cap.release()
        if write:
            self.out.release()


class Camera(QLabel):
    """Main widget with the traces.

    """
    def __init__(self, args):
        super(Camera, self).__init__()  # py2
        self.args = args

        self.setFixedSize(*args.camera_size)

    def start(self):
        """Start acquisition by starting a new thread.
        """
        thread = QThread()
        self.thread = thread
        obj = Worker(self.args)
        self.obj = obj
        obj.newframe.connect(self.update_camera)
        obj.moveToThread(thread)

        thread.started.connect(obj.start)
        thread.finished.connect(obj.stop)
        thread.start()
        thread.exec_()  # necessary for QTimer
        thread.quit()  # necessary in case we close the thread

    def stop(self):
        """End acquisition.
        """
        self.thread.exit()

    def update_camera(self, frame):
        """Update the data matrix with the new frame and plot it
        """
        img = QImage(frame, self.args.camera_size[0], self.args.camera_size[1],
                     QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(img))
