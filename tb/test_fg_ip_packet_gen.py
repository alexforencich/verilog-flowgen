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
import ip_ep

module = 'fg_ip_packet_gen'

srcs = []

srcs.append("../rtl/%s.v" % module)
srcs.append("../rtl/fg_packet_gen.v")
srcs.append("test_%s.v" % module)

src = ' '.join(srcs)

build_cmd = "iverilog -o test_%s.vvp %s" % (module, src)

def dut_fg_ip_packet_gen(clk,
                         rst,
                         current_test,

                         input_bd_valid,
                         input_bd_ready,
                         input_bd_dest,
                         input_bd_burst_len,

                         output_ip_hdr_valid,
                         output_ip_hdr_ready,
                         output_ip_eth_dest_mac,
                         output_ip_eth_src_mac,
                         output_ip_eth_type,
                         output_ip_dscp,
                         output_ip_ecn,
                         output_ip_length,
                         output_ip_identification,
                         output_ip_flags,
                         output_ip_fragment_offset,
                         output_ip_ttl,
                         output_ip_protocol,
                         output_ip_source_ip,
                         output_ip_dest_ip,
                         output_ip_payload_tdata,
                         output_ip_payload_tkeep,
                         output_ip_payload_tvalid,
                         output_ip_payload_tready,
                         output_ip_payload_tlast,
                         output_ip_payload_tuser,

                         busy,

                         local_mac,
                         local_ip,
                         frame_mtu,

                         dest_wr_en,
                         dest_index,
                         dest_mac,
                         dest_ip):

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

                output_ip_hdr_valid=output_ip_hdr_valid,
                output_ip_hdr_ready=output_ip_hdr_ready,
                output_ip_eth_dest_mac=output_ip_eth_dest_mac,
                output_ip_eth_src_mac=output_ip_eth_src_mac,
                output_ip_eth_type=output_ip_eth_type,
                output_ip_dscp=output_ip_dscp,
                output_ip_ecn=output_ip_ecn,
                output_ip_length=output_ip_length,
                output_ip_identification=output_ip_identification,
                output_ip_flags=output_ip_flags,
                output_ip_fragment_offset=output_ip_fragment_offset,
                output_ip_ttl=output_ip_ttl,
                output_ip_protocol=output_ip_protocol,
                output_ip_source_ip=output_ip_source_ip,
                output_ip_dest_ip=output_ip_dest_ip,
                output_ip_payload_tdata=output_ip_payload_tdata,
                output_ip_payload_tkeep=output_ip_payload_tkeep,
                output_ip_payload_tvalid=output_ip_payload_tvalid,
                output_ip_payload_tready=output_ip_payload_tready,
                output_ip_payload_tlast=output_ip_payload_tlast,
                output_ip_payload_tuser=output_ip_payload_tuser,

                busy=busy,

                local_mac=local_mac,
                local_ip=local_ip,
                frame_mtu=frame_mtu,

                dest_wr_en=dest_wr_en,
                dest_index=dest_index,
                dest_mac=dest_mac,
                dest_ip=dest_ip)

def bench():

    # Parameters
    DEST_WIDTH = 8
    DATA_WIDTH = 64
    KEEP_WIDTH = (DATA_WIDTH/8)
    MAC_PREFIX = 0xDA0000000000
    IP_PREFIX = 0xc0a80100

    # Inputs
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    current_test = Signal(intbv(0)[8:])

    input_bd_valid = Signal(bool(0))
    input_bd_dest = Signal(intbv(0)[DEST_WIDTH:])
    input_bd_burst_len = Signal(intbv(0)[32:])

    output_ip_hdr_ready = Signal(bool(0))
    output_ip_payload_tready = Signal(bool(0))

    local_mac = Signal(intbv(0)[48:])
    local_ip = Signal(intbv(0)[32:])
    frame_mtu = Signal(intbv(0)[16:])

    dest_wr_en = Signal(bool(0))
    dest_index = Signal(intbv(0)[DEST_WIDTH:])
    dest_mac = Signal(intbv(0)[48:])
    dest_ip = Signal(intbv(0)[32:])

    # Outputs
    input_bd_ready = Signal(bool(0))

    output_ip_hdr_valid = Signal(bool(0))
    output_ip_eth_dest_mac = Signal(intbv(0)[48:])
    output_ip_eth_src_mac = Signal(intbv(0)[48:])
    output_ip_eth_type = Signal(intbv(0)[16:])
    output_ip_dscp = Signal(intbv(0)[6:])
    output_ip_ecn = Signal(intbv(0)[2:])
    output_ip_length = Signal(intbv(0)[16:])
    output_ip_identification = Signal(intbv(0)[16:])
    output_ip_flags = Signal(intbv(0)[3:])
    output_ip_fragment_offset = Signal(intbv(0)[13:])
    output_ip_ttl = Signal(intbv(0)[8:])
    output_ip_protocol = Signal(intbv(0)[8:])
    output_ip_source_ip = Signal(intbv(0)[32:])
    output_ip_dest_ip = Signal(intbv(0)[32:])
    output_ip_payload_tdata = Signal(intbv(0)[DATA_WIDTH:])
    output_ip_payload_tkeep = Signal(intbv(0)[KEEP_WIDTH:])
    output_ip_payload_tvalid = Signal(bool(0))
    output_ip_payload_tlast = Signal(bool(0))
    output_ip_payload_tuser = Signal(bool(0))

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

    sink = ip_ep.IPFrameSink(clk,
                             rst,
                             ip_hdr_ready=output_ip_hdr_ready,
                             ip_hdr_valid=output_ip_hdr_valid,
                             eth_dest_mac=output_ip_eth_dest_mac,
                             eth_src_mac=output_ip_eth_src_mac,
                             eth_type=output_ip_eth_type,
                             ip_dscp=output_ip_dscp,
                             ip_ecn=output_ip_ecn,
                             ip_length=output_ip_length,
                             ip_identification=output_ip_identification,
                             ip_flags=output_ip_flags,
                             ip_fragment_offset=output_ip_fragment_offset,
                             ip_ttl=output_ip_ttl,
                             ip_protocol=output_ip_protocol,
                             ip_source_ip=output_ip_source_ip,
                             ip_dest_ip=output_ip_dest_ip,
                             ip_payload_tdata=output_ip_payload_tdata,
                             ip_payload_tkeep=output_ip_payload_tkeep,
                             ip_payload_tvalid=output_ip_payload_tvalid,
                             ip_payload_tready=output_ip_payload_tready,
                             ip_payload_tlast=output_ip_payload_tlast,
                             ip_payload_tuser=output_ip_payload_tuser,
                             fifo=sink_queue,
                             pause=sink_pause,
                             name='sink')

    # DUT
    dut = dut_fg_ip_packet_gen(clk,
                               rst,
                               current_test,

                               input_bd_valid,
                               input_bd_ready,
                               input_bd_dest,
                               input_bd_burst_len,

                               output_ip_hdr_valid,
                               output_ip_hdr_ready,
                               output_ip_eth_dest_mac,
                               output_ip_eth_src_mac,
                               output_ip_eth_type,
                               output_ip_dscp,
                               output_ip_ecn,
                               output_ip_length,
                               output_ip_identification,
                               output_ip_flags,
                               output_ip_fragment_offset,
                               output_ip_ttl,
                               output_ip_protocol,
                               output_ip_source_ip,
                               output_ip_dest_ip,
                               output_ip_payload_tdata,
                               output_ip_payload_tkeep,
                               output_ip_payload_tvalid,
                               output_ip_payload_tready,
                               output_ip_payload_tlast,
                               output_ip_payload_tuser,

                               busy,

                               local_mac,
                               local_ip,
                               frame_mtu,

                               dest_wr_en,
                               dest_index,
                               dest_mac,
                               dest_ip)

    @always(delay(4))
    def clkgen():
        clk.next = not clk

    def wait_normal():
        while busy or output_ip_payload_tvalid:
            yield clk.posedge

    def wait_pause_sink():
        while busy or output_ip_payload_tvalid:
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

        # set MAC and IP address
        local_mac.next = 0x5A5152535455
        local_ip.next = 0xc0a80164

        frame_mtu.next = 128

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
                total += len(rx_frame.payload.data)

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
                total += len(rx_frame.payload.data)

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
