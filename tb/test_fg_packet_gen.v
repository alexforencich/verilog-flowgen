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

`timescale 1 ns / 1 ps

module test_fg_packet_gen;

// Parameters
parameter DEST_WIDTH = 8;
parameter DATA_WIDTH = 64;
parameter KEEP_WIDTH = DATA_WIDTH/8;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg input_bd_valid = 0;
reg [7:0] input_bd_dest = 0;
reg [31:0] input_bd_burst_len = 0;
reg output_hdr_ready = 0;
reg output_payload_tready = 0;
reg [15:0] payload_mtu = 0;

// Outputs
wire input_bd_ready;
wire output_hdr_valid;
wire [7:0] output_hdr_dest;
wire [63:0] output_payload_tdata;
wire [7:0] output_payload_tkeep;
wire output_payload_tvalid;
wire output_payload_tlast;
wire output_payload_tuser;
wire busy;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_bd_valid,
                input_bd_dest,
                input_bd_burst_len,
                output_hdr_ready,
                output_payload_tready,
                payload_mtu);
    $to_myhdl(input_bd_ready,
              output_hdr_valid,
              output_hdr_dest,
              output_payload_tdata,
              output_payload_tkeep,
              output_payload_tvalid,
              output_payload_tlast,
              output_payload_tuser,
              busy);

    // dump file
    $dumpfile("test_fg_packet_gen.lxt");
    $dumpvars(0, test_fg_packet_gen);
end

fg_packet_gen #(
    .DEST_WIDTH(DEST_WIDTH),
    .DATA_WIDTH(DATA_WIDTH),
    .KEEP_WIDTH(KEEP_WIDTH)
)
UUT (
    .clk(clk),
    .rst(rst),
    // Burst descriptor input
    .input_bd_valid(input_bd_valid),
    .input_bd_ready(input_bd_ready),
    .input_bd_dest(input_bd_dest),
    .input_bd_burst_len(input_bd_burst_len),
    // Packet output
    .output_hdr_valid(output_hdr_valid),
    .output_hdr_ready(output_hdr_ready),
    .output_hdr_dest(output_hdr_dest),
    .output_payload_tdata(output_payload_tdata),
    .output_payload_tkeep(output_payload_tkeep),
    .output_payload_tvalid(output_payload_tvalid),
    .output_payload_tready(output_payload_tready),
    .output_payload_tlast(output_payload_tlast),
    .output_payload_tuser(output_payload_tuser),
    // Status signals
    .busy(busy),
    // Configuration signals
    .payload_mtu(payload_mtu)
);

endmodule
