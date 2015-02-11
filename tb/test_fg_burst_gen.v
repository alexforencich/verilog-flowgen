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

module test_fg_burst_gen;

// Parameters
parameter FLOW_ADDR_WIDTH = 5;
parameter DEST_WIDTH = 8;
parameter RATE_SCALE = 8;

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
reg output_bd_ready = 0;

// Outputs
wire input_fd_ready;
wire output_bd_valid;
wire [7:0] output_bd_dest;
wire [31:0] output_bd_burst_len;
wire busy;
wire [FLOW_ADDR_WIDTH-1:0] active_flows;

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
                output_bd_ready);
    $to_myhdl(input_fd_ready,
              output_bd_valid,
              output_bd_dest,
              output_bd_burst_len,
              busy,
              active_flows);

    // dump file
    $dumpfile("test_fg_burst_gen.lxt");
    $dumpvars(0, test_fg_burst_gen);
end

fg_burst_gen #(
    .FLOW_ADDR_WIDTH(FLOW_ADDR_WIDTH),
    .DEST_WIDTH(DEST_WIDTH),
    .RATE_SCALE(RATE_SCALE)
)
UUT (
    .clk(clk),
    .rst(rst),
    // Flow descriptor input
    .input_fd_valid(input_fd_valid),
    .input_fd_ready(input_fd_ready),
    .input_fd_dest(input_fd_dest),
    .input_fd_rate_num(input_fd_rate_num),
    .input_fd_rate_denom(input_fd_rate_denom),
    .input_fd_len(input_fd_len),
    .input_fd_burst_len(input_fd_burst_len),
    // Burst descriptor output
    .output_bd_valid(output_bd_valid),
    .output_bd_ready(output_bd_ready),
    .output_bd_dest(output_bd_dest),
    .output_bd_burst_len(output_bd_burst_len),
    // Status signals
    .busy(busy),
    // Configuration signals
    .active_flows(active_flows)
);

endmodule
