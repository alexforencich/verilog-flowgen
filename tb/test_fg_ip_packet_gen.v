/*

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

*/

// Language: Verilog 2001

`timescale 1ns / 1ps

/*
 * Testbench for fg_ip_packet_gen
 */
module test_fg_ip_packet_gen;

// Parameters
parameter DEST_WIDTH = 8;
parameter DATA_WIDTH = 64;
parameter KEEP_WIDTH = (DATA_WIDTH/8);
parameter MAC_PREFIX = 48'hDA0000000000;
parameter IP_PREFIX = 32'hc0a80100;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg input_bd_valid = 0;
reg [DEST_WIDTH-1:0] input_bd_dest = 0;
reg [31:0] input_bd_burst_len = 0;
reg output_ip_hdr_ready = 0;
reg output_ip_payload_tready = 0;
reg [47:0] local_mac = 0;
reg [31:0] local_ip = 0;
reg [15:0] frame_mtu = 0;
reg dest_wr_en = 0;
reg [DEST_WIDTH-1:0] dest_index = 0;
reg [47:0] dest_mac = 0;
reg [31:0] dest_ip = 0;

// Outputs
wire input_bd_ready;
wire output_ip_hdr_valid;
wire [47:0] output_ip_eth_dest_mac;
wire [47:0] output_ip_eth_src_mac;
wire [15:0] output_ip_eth_type;
wire [5:0] output_ip_dscp;
wire [1:0] output_ip_ecn;
wire [15:0] output_ip_length;
wire [15:0] output_ip_identification;
wire [2:0] output_ip_flags;
wire [12:0] output_ip_fragment_offset;
wire [7:0] output_ip_ttl;
wire [7:0] output_ip_protocol;
wire [31:0] output_ip_source_ip;
wire [31:0] output_ip_dest_ip;
wire [DATA_WIDTH-1:0] output_ip_payload_tdata;
wire [KEEP_WIDTH-1:0] output_ip_payload_tkeep;
wire output_ip_payload_tvalid;
wire output_ip_payload_tlast;
wire output_ip_payload_tuser;
wire busy;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_bd_valid,
                input_bd_dest,
                input_bd_burst_len,
                output_ip_hdr_ready,
                output_ip_payload_tready,
                local_mac,
                local_ip,
                frame_mtu,
                dest_wr_en,
                dest_index,
                dest_mac,
                dest_ip);
    $to_myhdl(input_bd_ready,
              output_ip_hdr_valid,
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
              output_ip_payload_tlast,
              output_ip_payload_tuser,
              busy);

    // dump file
    $dumpfile("test_fg_ip_packet_gen.lxt");
    $dumpvars(0, test_fg_ip_packet_gen);
end

fg_ip_packet_gen #(
    .DEST_WIDTH(DEST_WIDTH),
    .DATA_WIDTH(DATA_WIDTH),
    .KEEP_WIDTH(KEEP_WIDTH),
    .MAC_PREFIX(MAC_PREFIX),
    .IP_PREFIX (IP_PREFIX)
)
UUT (
    .clk(clk),
    .rst(rst),
    .input_bd_valid(input_bd_valid),
    .input_bd_ready(input_bd_ready),
    .input_bd_dest(input_bd_dest),
    .input_bd_burst_len(input_bd_burst_len),
    .output_ip_hdr_valid(output_ip_hdr_valid),
    .output_ip_hdr_ready(output_ip_hdr_ready),
    .output_ip_eth_dest_mac(output_ip_eth_dest_mac),
    .output_ip_eth_src_mac(output_ip_eth_src_mac),
    .output_ip_eth_type(output_ip_eth_type),
    .output_ip_dscp(output_ip_dscp),
    .output_ip_ecn(output_ip_ecn),
    .output_ip_length(output_ip_length),
    .output_ip_identification(output_ip_identification),
    .output_ip_flags(output_ip_flags),
    .output_ip_fragment_offset(output_ip_fragment_offset),
    .output_ip_ttl(output_ip_ttl),
    .output_ip_protocol(output_ip_protocol),
    .output_ip_source_ip(output_ip_source_ip),
    .output_ip_dest_ip(output_ip_dest_ip),
    .output_ip_payload_tdata(output_ip_payload_tdata),
    .output_ip_payload_tkeep(output_ip_payload_tkeep),
    .output_ip_payload_tvalid(output_ip_payload_tvalid),
    .output_ip_payload_tready(output_ip_payload_tready),
    .output_ip_payload_tlast(output_ip_payload_tlast),
    .output_ip_payload_tuser(output_ip_payload_tuser),
    .busy(busy),
    .local_mac(local_mac),
    .local_ip(local_ip),
    .frame_mtu(frame_mtu),
    .dest_wr_en(dest_wr_en),
    .dest_index(dest_index),
    .dest_mac(dest_mac),
    .dest_ip(dest_ip)
);

endmodule
