#!/usr/bin/env python2
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
import os
from Queue import Queue

import fg_bd_ep
import fg_fd_ep

module = 'fg_burst_gen'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_fg_burst_gen(clk,
                     rst,
                     current_test,

                     input_fd_valid,
                     input_fd_ready,
                     input_fd_dest,
                     input_fd_rate_num,
                     input_fd_rate_denom,
                     input_fd_len,
                     input_fd_burst_len,

                     output_bd_valid,
                     output_bd_ready,
                     output_bd_dest,
                     output_bd_burst_len,

                     busy,
                     active_flows):

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
                
                output_bd_valid=output_bd_valid,
                output_bd_ready=output_bd_ready,
                output_bd_dest=output_bd_dest,
                output_bd_burst_len=output_bd_burst_len,

                busy=busy,
                active_flows=active_flows)

def bench():

    # Parameters
    FLOW_ADDR_WIDTH = 5
    DEST_WIDTH = 8
    RATE_SCALE = 8

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
    output_bd_ready = Signal(bool(0))

    # Outputs
    input_fd_ready = Signal(bool(0))
    output_bd_valid = Signal(bool(0))
    output_bd_dest = Signal(intbv(0)[DEST_WIDTH:])
    output_bd_burst_len = Signal(intbv(0)[32:])
    busy = Signal(bool(0))
    active_flows = Signal(intbv(0)[5:])

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
    dut = dut_fg_burst_gen(clk,
                           rst,
                           current_test,

                           input_fd_valid,
                           input_fd_ready,
                           input_fd_dest,
                           input_fd_rate_num,
                           input_fd_rate_denom,
                           input_fd_len,
                           input_fd_burst_len,

                           output_bd_valid,
                           output_bd_ready,
                           output_bd_dest,
                           output_bd_burst_len,

                           busy,
                           active_flows)

    @always(delay(4))
    def clkgen():
        clk.next = not clk

    # def wait_normal():
    #     while busy or output_payload_tvalid:
    #         yield clk.posedge

    # def wait_pause_sink():
    #     while busy or output_payload_tvalid:
    #         sink_pause.next = True
    #         yield clk.posedge
    #         yield clk.posedge
    #         yield clk.posedge
    #         sink_pause.next = False
    #         yield clk.posedge

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
        print("test 1: single flow")
        current_test.next = 1

        test_fd = fg_fd_ep.FlowDescriptor()
        test_fd.dest = 1
        test_fd.rate_num = 1
        test_fd.rate_denom = 10
        test_fd.len = 128
        test_fd.burst_len = 32

        source_queue.put(test_fd)
        yield clk.posedge
        yield clk.posedge

        while input_fd_valid or busy:
            yield clk.posedge

        yield delay(100)

        yield clk.posedge
        print("test 2: long flow")
        current_test.next = 2

        test_fd = fg_fd_ep.FlowDescriptor()
        test_fd.dest = 1
        test_fd.rate_num = 1
        test_fd.rate_denom = 10
        test_fd.len = 1024
        test_fd.burst_len = 256

        source_queue.put(test_fd)
        yield clk.posedge
        yield clk.posedge

        while input_fd_valid or busy:
            yield clk.posedge

        yield delay(100)

        yield clk.posedge
        print("test 3: two flows")
        current_test.next = 3

        test_fd1 = fg_fd_ep.FlowDescriptor()
        test_fd1.dest = 1
        test_fd1.rate_num = 1
        test_fd1.rate_denom = 10
        test_fd1.len = 1024
        test_fd1.burst_len = 32

        test_fd2 = fg_fd_ep.FlowDescriptor()
        test_fd2.dest = 2
        test_fd2.rate_num = 1
        test_fd2.rate_denom = 10
        test_fd2.len = 1024
        test_fd2.burst_len = 256

        source_queue.put(test_fd1)
        source_queue.put(test_fd2)
        yield clk.posedge
        yield clk.posedge

        while input_fd_valid or busy:
            yield clk.posedge

        yield delay(100)

        raise StopSimulation

    return dut, source, sink, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()

