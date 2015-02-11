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

module test_fg_bd_fifo;

// Parameters
parameter ADDR_WIDTH = 10;
parameter DEST_WIDTH = 8;

// Inputs
reg clk = 0;
reg rst = 0;
reg [7:0] current_test = 0;

reg input_bd_valid = 0;
reg [7:0] input_bd_dest = 0;
reg [31:0] input_bd_burst_len = 0;
reg output_bd_ready = 0;

// Outputs
wire input_bd_ready;
wire output_bd_valid;
wire [7:0] output_bd_dest;
wire [31:0] output_bd_burst_len;
wire [ADDR_WIDTH-1:0] count;
wire [ADDR_WIDTH+32-1:0] byte_count;

initial begin
    // myhdl integration
    $from_myhdl(clk,
                rst,
                current_test,
                input_bd_valid,
                input_bd_dest,
                input_bd_burst_len,
                output_bd_ready);
    $to_myhdl(input_bd_ready,
              output_bd_valid,
              output_bd_dest,
              output_bd_burst_len,
              count,
              byte_count);

    // dump file
    $dumpfile("test_fg_bd_fifo.lxt");
    $dumpvars(0, test_fg_bd_fifo);
end

fg_bd_fifo #(
    .ADDR_WIDTH(ADDR_WIDTH),
    .DEST_WIDTH(DEST_WIDTH)
)
UUT (
    .clk(clk),
    .rst(rst),
    // burst descriptor input
    .input_bd_valid(input_bd_valid),
    .input_bd_ready(input_bd_ready),
    .input_bd_dest(input_bd_dest),
    .input_bd_burst_len(input_bd_burst_len),
    // burst descriptor output
    .output_bd_valid(output_bd_valid),
    .output_bd_ready(output_bd_ready),
    .output_bd_dest(output_bd_dest),
    .output_bd_burst_len(output_bd_burst_len),
    // status
    .count(count),
    .byte_count(byte_count)
);

endmodule
