from numpy import zeros

# package to control NI
from ctypes import byref  # also in PyDAQmx
from PyDAQmx.DAQmxConstants import (DAQmx_Val_Diff,
                                    DAQmx_Val_Volts,
                                    DAQmx_Val_Rising,
                                    DAQmx_Val_ContSamps,
                                    DAQmx_Val_Acquired_Into_Buffer,
                                    DAQmx_Val_GroupByChannel,
                                    DAQmx_Val_Auto,
                                    )
from PyDAQmx.DAQmxTypes import int32
from PyDAQmx.Task import Task

from .edf import ExportEdf


class DAQmxReader(Task):
    """Class to interact with NI devices.

    Parameters
    ----------
    args : argparse.Namespace
        arguments specified by the user
    funct : function
        function to be called when the recording is being read.
    """
    def __init__(self, args, funct):
        super().__init__()

        # this line is also in the EDF input
        physicalChannel = (args.dev + '/ai' + args.analoginput).encode('utf-8')
        nameToAssignToChannel  = ''.encode('utf-8')  # use default names
        s_freq = float(args.s_freq)
        self.buffer_size = int(s_freq * args.buffer_size)
        self.timeout = args.timeout
        self.n_chan = args.n_chan
        self.funct = funct

        self.CreateAIVoltageChan(physicalChannel, nameToAssignToChannel,
                                 DAQmx_Val_Diff, args.minval, args.maxval,
                                 DAQmx_Val_Volts, None)
        self.CfgSampClkTiming(b'', s_freq, DAQmx_Val_Rising,
                              DAQmx_Val_ContSamps, self.buffer_size)
        self.AutoRegisterEveryNSamplesEvent(DAQmx_Val_Acquired_Into_Buffer,
                                            self.buffer_size, 0)
        self.AutoRegisterDoneEvent(0)

        self.edf = None
        if args.edf is not None:
            self.edf = ExportEdf()
            self.edf.open(args)

    def EveryNCallback(self):
        """Read the recording once buffer on the device is ready.
        """
        read = int32()
        data = zeros(self.buffer_size * self.n_chan)
        self.ReadAnalogF64(DAQmx_Val_Auto, self.timeout,
                           DAQmx_Val_GroupByChannel, data,
                           self.buffer_size * self.n_chan, byref(read), None)

        data = data.reshape((self.n_chan, self.buffer_size))
        if self.edf is not None:
            self.edf.write(data)
        self.funct(data, self.buffer_size)
        return 0  # The function should return an integer

    def DoneCallback(self, status):
        """Close the recordings, although I'm not sure when this is called.

        Probably raise error if recordings are interrupted
        """
        if self.edf is not None:
            self.edf.close()
        return 0
