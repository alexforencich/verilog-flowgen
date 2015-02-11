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

module test_fg_fd_fifo;

// Parameters
parameter ADDR_WIDTH = 10;
parameter DEST_WIDTH = 8;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg input_fd_valid = 0;
reg [7:0] input_fd_dest = 0;
reg [15:0] input_fd_rate_num = 0;
reg [15:0] input_fd_rate_denom = 0;
reg [31:0] input_fd_len = 0;
reg [31:0] input_fd_burst_len = 0;
reg output_fd_ready = 0;

// Outputs
wire input_fd_ready;
wire output_fd_valid;
wire [7:0] output_fd_dest;
wire [15:0] output_fd_rate_num;
wire [15:0] output_fd_rate_denom;
wire [31:0] output_fd_len;
wire [31:0] output_fd_burst_len;
wire [ADDR_WIDTH-1:0] count;
wire [ADDR_WIDTH+32-1:0] byte_count;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_fd_valid,
                input_fd_dest,
                input_fd_rate_num,
                input_fd_rate_denom,
                input_fd_len,
                input_fd_burst_len,
                output_fd_ready);
    $to_myhdl(input_fd_ready,
              output_fd_valid,
              output_fd_dest,
              output_fd_rate_num,
              output_fd_rate_denom,
              output_fd_len,
              output_fd_burst_len,
              count,
              byte_count);

    // dump file
    $dumpfile("test_fg_fd_fifo.lxt");
    $dumpvars(0, test_fg_fd_fifo);
end

fg_fd_fifo #(
    .ADDR_WIDTH(ADDR_WIDTH),
    .DEST_WIDTH(DEST_WIDTH)
)
UUT (
    .clk(clk),
    .rst(rst),
    // burst descriptor input
    .input_fd_valid(input_fd_valid),
    .input_fd_ready(input_fd_ready),
    .input_fd_dest(input_fd_dest),
    .input_fd_rate_num(input_fd_rate_num),
    .input_fd_rate_denom(input_fd_rate_denom),
    .input_fd_len(input_fd_len),
    .input_fd_burst_len(input_fd_burst_len),
    // burst descriptor output
    .output_fd_valid(output_fd_valid),
    .output_fd_ready(output_fd_ready),
    .output_fd_dest(output_fd_dest),
    .output_fd_rate_num(output_fd_rate_num),
    .output_fd_rate_denom(output_fd_rate_denom),
    .output_fd_len(output_fd_len),
    .output_fd_burst_len(output_fd_burst_len),
    // status
    .count(count),
    .byte_count(byte_count)
);

endmodule
