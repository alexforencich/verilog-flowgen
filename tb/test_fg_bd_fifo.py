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

import fg_bd_ep

module = 'fg_bd_fifo'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_fg_bd_fifo(clk,
                   rst,
                   current_test,

                   input_bd_valid,
                   input_bd_ready,
                   input_bd_dest,
                   input_bd_burst_len,

                   output_bd_valid,
                   output_bd_ready,
                   output_bd_dest,
                   output_bd_burst_len,

                   count,
                   byte_count):

    if os.system(build_cmd):
        raise Exception("Error running build command")
    return Cosimulation("vvp -m myhdl test_%s.vvp -lxt2" % module,
                clk=clk,
                rst=rst,
                current_test=current_test,

                input_bd_valid=input_bd_valid,
                input_bd_ready=input_bd_ready,
                input_bd_dest=input_bd_dest,
                input_bd_burst_len=input_bd_burst_len,

                output_bd_valid=output_bd_valid,
                output_bd_ready=output_bd_ready,
                output_bd_dest=output_bd_dest,
                output_bd_burst_len=output_bd_burst_len,

                count=count,
                byte_count=byte_count)

def bench():

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_bd_valid = Signal(bool(0))
    input_bd_dest = Signal(intbv(0)[8:])
    input_bd_burst_len = Signal(intbv(0)[32:])
    output_bd_ready = Signal(bool(0))

    # Outputs
    input_bd_ready = Signal(bool(0))
    output_bd_valid = Signal(bool(0))
    output_bd_dest = Signal(intbv(0)[8:])
    output_bd_burst_len = Signal(intbv(0)[32:])

    count = Signal(intbv(0)[10:])
    byte_count = Signal(intbv(0)[42:])

    # sources and sinks
    source_queue = Queue()
    source_pause = Signal(bool(0))
    sink_queue = Queue()
    sink_pause = Signal(bool(0))

    source = fg_bd_ep.BurstDescriptorSource(clk,
                                            rst,
                                            valid=input_bd_valid,
                                            ready=input_bd_ready,
                                            dest=input_bd_dest,
                                            burst_len=input_bd_burst_len,
                                            fifo=source_queue,
                                            pause=source_pause,
                                            name='source')

    sink = fg_bd_ep.BurstDescriptorSink(clk,
                                        rst,
                                        valid=output_bd_valid,
                                        ready=output_bd_ready,
                                        dest=output_bd_dest,
                                        burst_len=output_bd_burst_len,
                                        fifo=sink_queue,
                                        pause=sink_pause,
                                        name='sink')

    # DUT
    dut = dut_fg_bd_fifo(clk,
                         rst,
                         current_test,

                         input_bd_valid,
                         input_bd_ready,
                         input_bd_dest,
                         input_bd_burst_len,

                         output_bd_valid,
                         output_bd_ready,
                         output_bd_dest,
                         output_bd_burst_len,

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

        test_bd = fg_bd_ep.BurstDescriptor()
        test_bd.dest = 1
        test_bd.burst_len = 32

        source_queue.put(test_bd)
        yield clk.posedge
        yield clk.posedge

        while count > 0:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        rx_bd = sink_queue.get(False)

        assert rx_bd == test_bd

        yield delay(100)

        yield clk.posedge
        print("test 2: multiple packets")
        current_test.next = 2

        test_bd1 = fg_bd_ep.BurstDescriptor()
        test_bd1.dest = 1
        test_bd1.burst_len = 32

        test_bd2 = fg_bd_ep.BurstDescriptor()
        test_bd2.dest = 2
        test_bd2.burst_len = 256

        test_bd3 = fg_bd_ep.BurstDescriptor()
        test_bd3.dest = 3
        test_bd3.burst_len = 1024

        source_queue.put(test_bd1)
        source_queue.put(test_bd2)
        source_queue.put(test_bd3)
        yield clk.posedge
        yield clk.posedge

        while count > 0:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        rx_bd = sink_queue.get(False)
        assert rx_bd == test_bd1

        rx_bd = sink_queue.get(False)
        assert rx_bd == test_bd2

        rx_bd = sink_queue.get(False)
        assert rx_bd == test_bd3

        yield delay(100)

        yield clk.posedge
        print("test 3: multiple packets with pause")
        current_test.next = 3

        test_bd1 = fg_bd_ep.BurstDescriptor()
        test_bd1.dest = 1
        test_bd1.burst_len = 32

        test_bd2 = fg_bd_ep.BurstDescriptor()
        test_bd2.dest = 2
        test_bd2.burst_len = 256

        test_bd3 = fg_bd_ep.BurstDescriptor()
        test_bd3.dest = 3
        test_bd3.burst_len = 1024

        sink_pause.next = True

        source_queue.put(test_bd1)
        source_queue.put(test_bd2)
        source_queue.put(test_bd3)
        yield clk.posedge
        yield clk.posedge

        yield delay(100)

        assert int(count) == 3
        assert byte_count == test_bd1.burst_len + test_bd2.burst_len + test_bd3.burst_len

        sink_pause.next = False

        while count > 0:
            yield clk.posedge

        yield clk.posedge
        yield clk.posedge

        rx_bd = sink_queue.get(False)
        assert rx_bd == test_bd1

        rx_bd = sink_queue.get(False)
        assert rx_bd == test_bd2

        rx_bd = sink_queue.get(False)
        assert rx_bd == test_bd3

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

