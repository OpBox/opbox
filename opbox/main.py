#!/usr/bin/env python3

from argparse import ArgumentParser
from os.path import realpath, join, dirname
from sys import path, exit

from PyQt4.QtGui import QApplication, QMainWindow

# ADD MODULE
opbox_path = realpath(join(dirname(realpath(__file__)), '..'))
path.append(opbox_path)
from opbox.ui import Traces


def _count_channels(analoginput):
    """Heuristic to compute number of channel from the channel string.

    Parameters
    ----------
    analoginput : str
        string with the analog names ('0:1' or '0')

    Returns
    -------
    int
        number of channels
    """
    s = analoginput.split(':')
    return int(s[-1]) - int(s[0]) + 1


# INPUT ARGUMENTS
parser = ArgumentParser(prog='OpBox', description='GUI to interact with NI DAQ')
parser.add_argument('-d', '--dev', required=True,
                    help='Device name (such as ''Dev1'' or ''Dev2'')')
parser.add_argument('-a', '--analoginput', required=True,
                    help=('Analog channels to read (such as ''0:2'' for the ' +
                          'first three channels)'))
parser.add_argument('--s_freq', type=int, default=1000,
                    help='Sampling frequency (default: 1000)')
parser.add_argument('--buffer_size', type=float, default=0.1,
                    help='Duration of the buffer in seconds (default: 0.1)')
parser.add_argument('--maxval', type=float, default=1,
                    help=('The maximum value, in units, that you expect to '
                          'measure.'))
parser.add_argument('--minval', type=float, default=-1,
                    help=('The minimum value, in units, that you expect to '
                          'measure.'))
parser.add_argument('--window_size', type=float, default=5,
                    help='The lenght (in s) of the window to display')
parser.add_argument('--timeout', type=float, default=10,
                    help=('The amount of time, in seconds, to wait for the '
                          'function to read the samples.'))
parser.add_argument('--edf',
                    help='Filename of the EDF file to create')
args = parser.parse_args()
args.n_chan = _count_channels(args.analoginput)


class MainWindow(QMainWindow):
    """Main Window that holds all the widgets (traces with raw signal, webcam
    and other behavioral data.)"""
    def __init__(self):
        super().__init__()
        self.traces = Traces(args)
        self.setCentralWidget(self.traces)

    def closeEvent(self, event):
        """Make it more robust. It stops the connection and file when user
        closes the window."""
        try:
            self.traces.stop_acq()
        except AttributeError:  # task not initialized
            pass
        event.accept()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    exit(app.exec_())
