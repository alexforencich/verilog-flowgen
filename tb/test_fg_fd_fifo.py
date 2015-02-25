#!/usr/bin/env python2
"""

Copyright (c) 2014 Alex Forencich

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
import os
from Queue import Queue

import fg_fd_ep

module = 'fg_fd_fifo'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_fg_fd_fifo(clk,
                   rst,
                   current_test,

                   input_fd_valid,
                   input_fd_ready,
                   input_fd_dest,
                   input_fd_rate_num,
                   input_fd_rate_denom,
                   input_fd_len,
                   input_fd_burst_len,

                   output_fd_valid,
                   output_fd_ready,
                   output_fd_dest,
                   output_fd_rate_num,
                   output_fd_rate_denom,
                   output_fd_len,
                   output_fd_burst_len,

                   count,
                   byte_count):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,

                input_fd_valid=input_fd_valid,
                input_fd_ready=input_fd_ready,
                input_fd_dest=input_fd_dest,
                input_fd_rate_num=input_fd_rate_num,
                input_fd_rate_denom=input_fd_rate_denom,
                input_fd_len=input_fd_len,
                input_fd_burst_len=input_fd_burst_len,

                output_fd_valid=output_fd_valid,
                output_fd_ready=output_fd_ready,
                output_fd_dest=output_fd_dest,
                output_fd_rate_num=output_fd_rate_num,
                output_fd_rate_denom=output_fd_rate_denom,
                output_fd_len=output_fd_len,
                output_fd_burst_len=output_fd_burst_len,

                count=count,
                byte_count=byte_count)

def bench():

    # Parameters
    ADDR_WIDTH = 10
    DEST_WIDTH = 8

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_fd_valid = Signal(bool(0))
    input_fd_dest = Signal(intbv(0)[DEST_WIDTH:])
    input_fd_rate_num = Signal(intbv(0)[16:])
    input_fd_rate_denom = Signal(intbv(0)[16:])
    input_fd_len = Signal(intbv(0)[32:])
    input_fd_burst_len = Signal(intbv(0)[32:])
    output_fd_ready = Signal(bool(0))

    # Outputs
    input_fd_ready = Signal(bool(0))
    output_fd_valid = Signal(bool(0))
    output_fd_dest = Signal(intbv(0)[DEST_WIDTH:])
    output_fd_rate_num = Signal(intbv(0)[16:])
    output_fd_rate_denom = Signal(intbv(0)[16:])
    output_fd_len = Signal(intbv(0)[32:])
    output_fd_burst_len = Signal(intbv(0)[32:])

    count = Signal(intbv(0)[ADDR_WIDTH:])
    byte_count = Signal(intbv(0)[ADDR_WIDTH+32:])

    # sources and sinks
    source_queue = Queue()
    source_pause = Signal(bool(0))
    sink_queue = Queue()
    sink_pause = Signal(bool(0))

    source = fg_fd_ep.FlowDescriptorSource(clk,
                                           rst,
                                           valid=input_fd_valid,
                                           ready=input_fd_ready,
                                           dest=input_fd_dest,
                                           rate_num=input_fd_rate_num,
                                           rate_denom=input_fd_rate_denom,
                                           len=input_fd_len,
                                           burst_len=input_fd_burst_len,
                                           fifo=source_queue,
                                           pause=source_pause,
                                           name='source')

    sink = fg_fd_ep.FlowDescriptorSink(clk,
                                       rst,
                                       valid=output_fd_valid,
                                       ready=output_fd_ready,
                                       dest=output_fd_dest,
                                       rate_num=output_fd_rate_num,
                                       rate_denom=output_fd_rate_denom,
                                       len=output_fd_len,
                                       burst_len=output_fd_burst_len,
                                       fifo=sink_queue,
                                       pause=sink_pause,
                                       name='sink')

    # DUT
    dut = dut_fg_fd_fifo(clk,
                         rst,
                         current_test,

                         input_fd_valid,
                         input_fd_ready,
                         input_fd_dest,
                         input_fd_rate_num,
                         input_fd_rate_denom,
                         input_fd_len,
                         input_fd_burst_len,

                         output_fd_valid,
                         output_fd_ready,
                         output_fd_dest,
                         output_fd_rate_num,
                         output_fd_rate_denom,
                         output_fd_len,
                         output_fd_burst_len,

                         count,
                         byte_count)

    @always(delay(4))
    def clkgen():
        clk.next = not clk

    @instance
    def check():
        yield delay(100)
        yield clk.posedge
        rst.next = 1
        yield clk.posedge
        rst.next = 0
        yield clk.posedge
        yield delay(100)
        yield clk.posedge

        yield clk.posedge

        yield clk.posedge
        print("test 1: test packet")
        current_test.next = 1

        test_fd = fg_fd_ep.FlowDescriptor()
        test_fd.dest = 1
        test_fd.rate_num = 1
        test_fd.rate_denom = 10
        test_fd.len = 2048
        test_fd.burst_len = 32

        source_queue.put(test_fd)
        yield clk.posedge
        yield clk.posedge

        while count > 0:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        rx_fd = sink_queue.get(False)

        assert rx_fd == test_fd

        yield delay(100)

        yield clk.posedge
        print("test 2: multiple packets")
        current_test.next = 2

        test_fd1 = fg_fd_ep.FlowDescriptor()
        test_fd1.dest = 1
        test_fd1.rate_num = 1
        test_fd1.rate_denom = 10
        test_fd1.len = 2048
        test_fd1.burst_len = 32

        test_fd2 = fg_fd_ep.FlowDescriptor()
        test_fd2.dest = 2
        test_fd2.rate_num = 1
        test_fd2.rate_denom = 10
        test_fd2.len = 2048
        test_fd2.burst_len = 256

        test_fd3 = fg_fd_ep.FlowDescriptor()
        test_fd3.dest = 3
        test_fd3.rate_num = 1
        test_fd3.rate_denom = 10
        test_fd3.len = 2048
        test_fd3.burst_len = 1024

        source_queue.put(test_fd1)
        source_queue.put(test_fd2)
        source_queue.put(test_fd3)
        yield clk.posedge
        yield clk.posedge

        while count > 0:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        rx_fd = sink_queue.get(False)
        assert rx_fd == test_fd1

        rx_fd = sink_queue.get(False)
        assert rx_fd == test_fd2

        rx_fd = sink_queue.get(False)
        assert rx_fd == test_fd3

        yield delay(100)

        yield clk.posedge
        print("test 3: multiple packets with pause")
        current_test.next = 3

        test_fd1 = fg_fd_ep.FlowDescriptor()
        test_fd1.dest = 1
        test_fd1.rate_num = 1
        test_fd1.rate_denom = 10
        test_fd1.len = 2048
        test_fd1.burst_len = 32

        test_fd2 = fg_fd_ep.FlowDescriptor()
        test_fd2.dest = 2
        test_fd2.rate_num = 1
        test_fd2.rate_denom = 10
        test_fd2.len = 2048
        test_fd2.burst_len = 256

        test_fd3 = fg_fd_ep.FlowDescriptor()
        test_fd3.dest = 3
        test_fd3.rate_num = 1
        test_fd3.rate_denom = 10
        test_fd3.len = 2048
        test_fd3.burst_len = 1024

        sink_pause.next = True

        source_queue.put(test_fd1)
        source_queue.put(test_fd2)
        source_queue.put(test_fd3)
        yield clk.posedge
        yield clk.posedge

        yield delay(100)

        assert int(count) == 3
        assert byte_count == test_fd1.len + test_fd2.len + test_fd3.len

        sink_pause.next = False

        while count > 0:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        rx_fd = sink_queue.get(False)
        assert rx_fd == test_fd1

        rx_fd = sink_queue.get(False)
        assert rx_fd == test_fd2

        rx_fd = sink_queue.get(False)
        assert rx_fd == test_fd3

        yield delay(100)

        raise StopSimulation

    return dut, source, sink, clkgen, check

def test_bench():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()

