from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QPushButton,
                         QVBoxLayout,
                         QWidget,
                         )


class ControlPanel(QWidget):
    """Widget to start and stop the recordings.
    """
    def __init__(self, widgets):
        super(ControlPanel, self).__init__()  # py2
        self.widgets = widgets

        push = QPushButton()
        push.setText('Start')
        push.clicked.connect(self.start)
        self.push_start = push

        push = QPushButton()
        push.setText('Stop')
        push.clicked.connect(self.stop)
        self.push_stop = push

        layout = QVBoxLayout(self)
        layout.addWidget(self.push_start)
        layout.addWidget(self.push_stop, 1, Qt.AlignTop)

    def start(self):
        for one_widget in self.widgets.values():
            one_widget.start()

    def stop(self):
        for one_widget in self.widgets.values():
            one_widget.stop()
