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

import axis_ep
import fg_bd_ep

module = 'fg_packet_gen'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_fg_packet_gen(clk,
                       rst,
                       current_test,

                       input_bd_valid,
                       input_bd_ready,
                       input_bd_dest,
                       input_bd_burst_len,

                       output_hdr_valid,
                       output_hdr_ready,
                       output_hdr_dest,
                       output_payload_tdata,
                       output_payload_tkeep,
                       output_payload_tvalid,
                       output_payload_tready,
                       output_payload_tlast,
                       output_payload_tuser,

                       busy,
                       payload_mtu):

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

                output_hdr_valid=output_hdr_valid,
                output_hdr_ready=output_hdr_ready,
                output_hdr_dest=output_hdr_dest,
                output_payload_tdata=output_payload_tdata,
                output_payload_tkeep=output_payload_tkeep,
                output_payload_tvalid=output_payload_tvalid,
                output_payload_tready=output_payload_tready,
                output_payload_tlast=output_payload_tlast,
                output_payload_tuser=output_payload_tuser,

                busy=busy,
                payload_mtu=payload_mtu)

def bench():

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_bd_valid = Signal(bool(0))
    input_bd_dest = Signal(intbv(0)[8:])
    input_bd_burst_len = Signal(intbv(0)[32:])
    output_payload_tready = Signal(bool(0))
    output_hdr_ready = Signal(bool(0))
    payload_mtu = Signal(intbv(0)[16:])

    # Outputs
    input_bd_ready = Signal(bool(0))
    output_hdr_valid = Signal(bool(0))
    output_hdr_dest = Signal(intbv(0)[8:])
    output_payload_tdata = Signal(intbv(0)[64:])
    output_payload_tkeep = Signal(intbv(0)[8:])
    output_payload_tvalid = Signal(bool(0))
    output_payload_tlast = Signal(bool(0))
    output_payload_tuser = Signal(bool(0))
    busy = Signal(bool(0))

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

    sink = axis_ep.AXIStreamSink(clk,
                                 rst,
                                 tdata=output_payload_tdata,
                                 tkeep=output_payload_tkeep,
                                 tvalid=output_payload_tvalid,
                                 tready=output_payload_tready,
                                 tlast=output_payload_tlast,
                                 tuser=output_payload_tuser,
                                 fifo=sink_queue,
                                 pause=sink_pause,
                                 name='sink')

    # DUT
    dut = dut_fg_packet_gen(clk,
                          rst,
                          current_test,

                          input_bd_valid,
                          input_bd_ready,
                          input_bd_dest,
                          input_bd_burst_len,

                          output_hdr_valid,
                          output_hdr_ready,
                          output_hdr_dest,
                          output_payload_tdata,
                          output_payload_tkeep,
                          output_payload_tvalid,
                          output_payload_tready,
                          output_payload_tlast,
                          output_payload_tuser,

                          busy,
                          payload_mtu)

    @always(delay(4))
    def clkgen():
        clk.next = not clk

    def wait_normal():
        while busy or output_payload_tvalid:
            yield clk.posedge

    def wait_pause_sink():
        while busy or output_payload_tvalid:
            sink_pause.next = True
            yield clk.posedge
            yield clk.posedge
            yield clk.posedge
            sink_pause.next = False
            yield clk.posedge

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

        payload_mtu.next = 100

        yield clk.posedge
        print("test 1: test packet")
        current_test.next = 1

        test_bd = fg_bd_ep.BurstDescriptor()
        test_bd.dest = 1
        test_bd.burst_len = 32

        for wait in wait_normal, wait_pause_sink:
            source_queue.put(test_bd)
            yield clk.posedge
            yield clk.posedge
            yield clk.posedge

            yield wait()

            yield clk.posedge
            yield clk.posedge
            yield clk.posedge

            total = 0

            while not sink_queue.empty():
                rx_frame = sink_queue.get(False)
                total += len(rx_frame.data)

            assert total == test_bd.burst_len

            yield delay(100)

        yield clk.posedge
        print("test 2: test packet")
        current_test.next = 1

        test_bd = fg_bd_ep.BurstDescriptor()
        test_bd.dest = 2
        test_bd.burst_len = 512

        for wait in wait_normal, wait_pause_sink:
            source_queue.put(test_bd)
            yield clk.posedge
            yield clk.posedge
            yield clk.posedge

            yield wait()

            yield clk.posedge
            yield clk.posedge
            yield clk.posedge

            total = 0

            while not sink_queue.empty():
                rx_frame = sink_queue.get(False)
                total += len(rx_frame.data)

            assert total == test_bd.burst_len

            yield delay(100)

        raise StopSimulation

    return dut, source, sink, clkgen, check

def test_bench():
    sim = Simulation(bench())
    sim.run()

if __name__ == '__main__':
    print("Running test...")
    test_bench()

