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

class FlowDescriptor(object):
    def __init__(self,
                 dest=0,
                 rate_num=0,
                 rate_denom=0,
                 len=0,
                 burst_len=0):

        self.dest = dest
        self.rate_num = rate_num
        self.rate_denom = rate_denom
        self.len = len
        self.burst_len = burst_len

        if type(dest) is dict:
            self.dest = dest['dest']
            self.rate_num = dest['rate_num']
            self.rate_denom = dest['rate_denom']
            self.len = dest['len']
            self.burst_len = dest['burst_len']
        if type(dest) is FlowDescriptor:
            self.dest = dest.dest
            self.rate_num = dest.rate_num
            self.rate_denom = dest.rate_denom
            self.len = dest.len
            self.burst_len = dest.burst_len

    def __eq__(self, other):
        if type(other) is FlowDescriptor:
            return (self.dest == other.dest and
                self.rate_num == other.rate_num and
                self.rate_denom == other.rate_denom and
                self.len == other.len and
                self.burst_len == other.burst_len)

    def __repr__(self):
        return (('FlowDescriptor(dest=0x%02x, ' % self.dest) +
                ('rate_num=%d, ' % self.rate_num) +
                ('rate_denom=%d, ' % self.rate_denom) +
                ('len=%d, ' % self.len) +
                ('burst_len=%d)' % self.burst_len))

def FlowDescriptorSource(clk, rst,
                         valid=None,
                         ready=None,
                         dest=Signal(intbv(0)[8:]),
                         rate_num=Signal(intbv(0)[16:]),
                         rate_denom=Signal(intbv(0)[16:]),
                         len=Signal(intbv(0)[32:]),
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
        fd = dict()

        while True:
            yield clk.posedge, rst.posedge

            if rst:
                valid_int.next = False
            else:
                if ready_int:
                    valid_int.next = False
                if (ready_int and valid) or not valid_int:
                    if not fifo.empty():
                        fd = fifo.get()
                        fd = FlowDescriptor(fd)
                        dest.next = fd.dest
                        rate_num.next = fd.rate_num
                        rate_denom.next = fd.rate_denom
                        len.next = fd.len
                        burst_len.next = fd.burst_len

                        if name is not None:
                            print("[%s] Sending flow %s" % (name, repr(fd)))

                        valid_int.next = True

    return logic, pause_logic


def FlowDescriptorSink(clk, rst,
                       valid=None,
                       ready=None,
                       dest=Signal(intbv(0)[8:]),
                       rate_num=Signal(intbv(0)[16:]),
                       rate_denom=Signal(intbv(0)[16:]),
                       len=Signal(intbv(0)[32:]),
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
        fd = FlowDescriptor()

        while True:
            yield clk.posedge, rst.posedge

            if rst:
                ready_int.next = False
            else:
                ready_int.next = True

                if ready_int and valid_int:
                    fd = FlowDescriptor()
                    fd.dest = int(dest)
                    fd.rate_num = int(rate_num)
                    fd.rate_denom = int(rate_denom)
                    fd.len = int(len)
                    fd.burst_len = int(burst_len)
                    fifo.put(fd)

                    if name is not None:
                        print("[%s] Got flow %s" % (name, repr(fd)))

    return logic, pause_logic

