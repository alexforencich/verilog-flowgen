"""

Copyright (c) 2015 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from myhdl import *
from Queue import Queue
import struct

class BurstDescriptor(object):
    def __init__(self,
                 dest=0,
                 burst_len=0):

        self.dest = dest
        self.burst_len = burst_len

        if type(dest) is dict:
            self.dest = dest['dest']
            self.burst_len = dest['burst_len']
        if type(dest) is BurstDescriptor:
            self.dest = dest.dest
            self.burst_len = dest.burst_len

    def __eq__(self, other):
        if type(other) is BurstDescriptor:
            return (self.dest == other.dest and
                self.burst_len == other.burst_len)

    def __repr__(self):
        return (('BurstDescriptor(dest=0x%02x, ' % self.dest) +
                ('burst_len=%d)' % self.burst_len))

def BurstDescriptorSource(clk, rst,
                          valid=None,
                          ready=None,
                          dest=Signal(intbv(0)[8:]),
                          burst_len=Signal(intbv(0)[32:]),
                          fifo=None,
                          pause=0,
                          name=None):

    ready_int = Signal(bool(False))
    valid_int = Signal(bool(False))

    @always_comb
    def pause_logic():
        ready_int.next = ready and not pause
        valid.next = valid_int and not pause

    @instance
    def logic():
        bd = dict()

        while True:
            yield clk.posedge, rst.posedge

            if rst:
                valid_int.next = False
            else:
                if ready_int:
                    valid_int.next = False
                if (ready_int and valid) or not valid_int:
                    if not fifo.empty():
                        bd = fifo.get()
                        bd = BurstDescriptor(bd)
                        dest.next = bd.dest
                        burst_len.next = bd.burst_len

                        if name is not None:
                            print("[%s] Sending burst %s" % (name, repr(bd)))

                        valid_int.next = True

    return logic, pause_logic


def BurstDescriptorSink(clk, rst,
                        valid=None,
                        ready=None,
                        dest=Signal(intbv(0)[8:]),
                        burst_len=Signal(intbv(0)[32:]),
                        fifo=None,
                        pause=0,
                        name=None):

    ready_int = Signal(bool(False))
    valid_int = Signal(bool(False))

    @always_comb
    def pause_logic():
        ready.next = ready_int and not pause
        valid_int.next = valid and not pause

    @instance
    def logic():
        bd = BurstDescriptor()

        while True:
            yield clk.posedge, rst.posedge

            if rst:
                ready_int.next = False
            else:
                ready_int.next = True

                if ready_int and valid_int:
                    bd = BurstDescriptor()
                    bd.dest = int(dest)
                    bd.burst_len = int(burst_len)
                    fifo.put(bd)

                    if name is not None:
                        print("[%s] Got burst %s" % (name, repr(bd)))

    return logic, pause_logic

