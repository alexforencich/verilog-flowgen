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
 * Flow generator - IP packet generator module
 */
module fg_ip_packet_gen #(
    parameter DEST_WIDTH = 8,
    parameter DATA_WIDTH = 64,
    parameter KEEP_WIDTH = (DATA_WIDTH/8),
    parameter MAC_PREFIX = 48'hDA0000000000,
    parameter IP_PREFIX = 32'hc0a80100
)
(
    input  wire                   clk,
    input  wire                   rst,

    /*
     * Burst descriptor input
     */
    input  wire                   input_bd_valid,
    output wire                   input_bd_ready,
    input  wire [DEST_WIDTH-1:0]  input_bd_dest,
    input  wire [31:0]            input_bd_burst_len,

    /*
     * IP output
     */
    output wire                   output_ip_hdr_valid,
    input  wire                   output_ip_hdr_ready,
    output wire [47:0]            output_ip_eth_dest_mac,
    output wire [47:0]            output_ip_eth_src_mac,
    output wire [15:0]            output_ip_eth_type,
    output wire [5:0]             output_ip_dscp,
    output wire [1:0]             output_ip_ecn,
    output wire [15:0]            output_ip_length,
    output wire [15:0]            output_ip_identification,
    output wire [2:0]             output_ip_flags,
    output wire [12:0]            output_ip_fragment_offset,
    output wire [7:0]             output_ip_ttl,
    output wire [7:0]             output_ip_protocol,
    output wire [31:0]            output_ip_source_ip,
    output wire [31:0]            output_ip_dest_ip,
    output wire [DATA_WIDTH-1:0]  output_ip_payload_tdata,
    output wire [KEEP_WIDTH-1:0]  output_ip_payload_tkeep,
    output wire                   output_ip_payload_tvalid,
    input  wire                   output_ip_payload_tready,
    output wire                   output_ip_payload_tlast,
    output wire                   output_ip_payload_tuser,

    /*
     * Status
     */
    output wire                   busy,

    /*
     * Configuration
     */
    input  wire [47:0]            local_mac,
    input  wire [31:0]            local_ip,
    input  wire [15:0]            frame_mtu,

    input  wire                   dest_wr_en,
    input  wire [DEST_WIDTH-1:0]  dest_index,
    input  wire [47:0]            dest_mac,
    input  wire [31:0]            dest_ip
);

reg output_ip_hdr_valid_reg = 0;
reg [15:0] output_ip_length_reg = 0;

reg [47:0] output_ip_eth_dest_mac_reg = 0;
reg [31:0] output_ip_dest_ip_reg = 0;

reg [47:0] mem_mac[2**DEST_WIDTH-1:0];
reg [31:0] mem_ip[2**DEST_WIDTH-1:0];

integer i;

initial begin
    for (i = 0; i < 2**DEST_WIDTH; i = i + 1) begin
        mem_mac[i] <= MAC_PREFIX + i;
        mem_ip[i] <= IP_PREFIX + i;
    end
end

wire pkt_hdr_valid;
wire [7:0] pkt_hdr_dest;
wire [15:0] pkt_hdr_len;

assign output_ip_hdr_valid = output_ip_hdr_valid_reg;
assign output_ip_eth_dest_mac = output_ip_eth_dest_mac_reg;
assign output_ip_eth_src_mac = local_mac;
assign output_ip_eth_type = 16'h0800;
assign output_ip_dscp = 0;
assign output_ip_ecn = 0;
assign output_ip_length = output_ip_length_reg;
assign output_ip_identification = 0;
assign output_ip_flags = 3'b010;
assign output_ip_fragment_offset = 0;
assign output_ip_ttl = 64;
assign output_ip_protocol = 8'h11;
assign output_ip_source_ip = local_ip;
assign output_ip_dest_ip = output_ip_dest_ip_reg;

fg_packet_gen #(
    .DATA_WIDTH(DATA_WIDTH),
    .KEEP_WIDTH(KEEP_WIDTH)
)
fg_packet_gen_inst (
    .clk(clk),
    .rst(rst),

    .input_bd_valid(input_bd_valid),
    .input_bd_ready(input_bd_ready),
    .input_bd_dest(input_bd_dest),
    .input_bd_burst_len(input_bd_burst_len),

    .output_hdr_valid(pkt_hdr_valid),
    .output_hdr_ready(output_ip_hdr_ready),
    .output_hdr_dest(pkt_hdr_dest),
    .output_hdr_len(pkt_hdr_len),
    .output_payload_tdata(output_ip_payload_tdata),
    .output_payload_tkeep(output_ip_payload_tkeep),
    .output_payload_tvalid(output_ip_payload_tvalid),
    .output_payload_tready(output_ip_payload_tready),
    .output_payload_tlast(output_ip_payload_tlast),
    .output_payload_tuser(output_ip_payload_tuser),

    .busy(busy),

    .payload_mtu(frame_mtu-20)
);

always @(posedge clk) begin
    if (rst) begin
        output_ip_hdr_valid_reg <= 0;
        output_ip_eth_dest_mac_reg <= 0;
        output_ip_dest_ip_reg <= 0;
    end else begin
        if (pkt_hdr_valid & ~output_ip_hdr_valid) begin
            output_ip_hdr_valid_reg <= 1;
            output_ip_length_reg <= pkt_hdr_len + 20;
            output_ip_eth_dest_mac_reg <= mem_mac[pkt_hdr_dest];
            output_ip_dest_ip_reg <= mem_ip[pkt_hdr_dest];
        end else begin
            output_ip_hdr_valid_reg <= output_ip_hdr_valid_reg & ~output_ip_hdr_ready;
        end

        if (dest_wr_en) begin
            mem_mac[dest_index] <= dest_mac;
            mem_ip[dest_index] <= dest_ip;
        end
    end
end

endmodule
