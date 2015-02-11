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
 * Flow generator - flow descriptor FIFO
 */
module fg_fd_fifo #
(
    parameter ADDR_WIDTH = 10,
    parameter DEST_WIDTH = 8
)
(
    input  wire                   clk,
    input  wire                   rst,

    /*
     * Flow descriptor input
     */
    input  wire                   input_fd_valid,
    output wire                   input_fd_ready,
    input  wire [DEST_WIDTH-1:0]  input_fd_dest,
    input  wire [15:0]            input_fd_rate_num,
    input  wire [15:0]            input_fd_rate_denom,
    input  wire [31:0]            input_fd_len,
    input  wire [31:0]            input_fd_burst_len,

    /*
     * Flow descriptor output
     */
    output wire                   output_fd_valid,
    input  wire                   output_fd_ready,
    output wire [DEST_WIDTH-1:0]  output_fd_dest,
    output wire [15:0]            output_fd_rate_num,
    output wire [15:0]            output_fd_rate_denom,
    output wire [31:0]            output_fd_len,
    output wire [31:0]            output_fd_burst_len,

    /*
     * Status
     */
    output wire [ADDR_WIDTH-1:0] count,
    output wire [ADDR_WIDTH+32-1:0] byte_count
);

reg [ADDR_WIDTH:0] wr_ptr = {ADDR_WIDTH+1{1'b0}};
reg [ADDR_WIDTH:0] rd_ptr = {ADDR_WIDTH+1{1'b0}};

reg [DEST_WIDTH-1:0] fd_dest_reg = 0;
reg [15:0] fd_rate_num_reg = 0;
reg [15:0] fd_rate_denom_reg = 0;
reg [31:0] fd_len_reg = 0;
reg [31:0] fd_burst_len_reg = 0;

reg [DEST_WIDTH-1:0] fd_dest_mem[(2**ADDR_WIDTH)-1:0];
reg [15:0] fd_rate_num_mem[(2**ADDR_WIDTH)-1:0];
reg [15:0] fd_rate_denom_mem[(2**ADDR_WIDTH)-1:0];
reg [31:0] fd_len_mem[(2**ADDR_WIDTH)-1:0];
reg [31:0] fd_burst_len_mem[(2**ADDR_WIDTH)-1:0];

reg output_read = 1'b0;

reg output_fd_valid_reg = 1'b0;

reg [ADDR_WIDTH-1:0] count_reg = 0;
reg [ADDR_WIDTH+32-1:0] byte_count_reg = 0;

// full when first MSB different but rest same
wire full = ((wr_ptr[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]) &&
             (wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]));
// empty when pointers match exactly
wire empty = wr_ptr == rd_ptr;

wire write = input_fd_valid & ~full;
wire read = (output_fd_ready | ~output_fd_valid_reg) & ~empty;

assign output_fd_dest = fd_dest_reg;
assign output_fd_rate_num = fd_rate_num_reg;
assign output_fd_rate_denom = fd_rate_denom_reg;
assign output_fd_len = fd_len_reg;
assign output_fd_burst_len = fd_burst_len_reg;

assign count = count_reg;
assign byte_count = byte_count_reg;

assign input_fd_ready = ~full;
assign output_fd_valid = output_fd_valid_reg;

// write
always @(posedge clk or posedge rst) begin
    if (rst) begin
        wr_ptr <= 0;
    end else if (write) begin
        fd_dest_mem[wr_ptr[ADDR_WIDTH-1:0]] <= input_fd_dest;
        fd_rate_num_mem[wr_ptr[ADDR_WIDTH-1:0]] <= input_fd_rate_num;
        fd_rate_denom_mem[wr_ptr[ADDR_WIDTH-1:0]] <= input_fd_rate_denom;
        fd_len_mem[wr_ptr[ADDR_WIDTH-1:0]] <= input_fd_len;
        fd_burst_len_mem[wr_ptr[ADDR_WIDTH-1:0]] <= input_fd_burst_len;
        wr_ptr <= wr_ptr + 1;
    end
end

// read
always @(posedge clk or posedge rst) begin
    if (rst) begin
        rd_ptr <= 0;
    end else if (read) begin
        fd_dest_reg <= fd_dest_mem[rd_ptr[ADDR_WIDTH-1:0]];
        fd_rate_num_reg <= fd_rate_num_mem[rd_ptr[ADDR_WIDTH-1:0]];
        fd_rate_denom_reg <= fd_rate_denom_mem[rd_ptr[ADDR_WIDTH-1:0]];
        fd_len_reg <= fd_len_mem[rd_ptr[ADDR_WIDTH-1:0]];
        fd_burst_len_reg <= fd_burst_len_mem[rd_ptr[ADDR_WIDTH-1:0]];
        rd_ptr <= rd_ptr + 1;
    end
end

// source ready output
always @(posedge clk or posedge rst) begin
    if (rst) begin
        output_fd_valid_reg <= 1'b0;
    end else if (output_fd_ready | ~output_fd_valid_reg) begin
        output_fd_valid_reg <= ~empty;
    end else begin
        output_fd_valid_reg <= output_fd_valid_reg;
    end
end

// counters
always @(posedge clk or posedge rst) begin
    if (rst) begin
        count_reg <= 0;
        byte_count_reg <= 0;
    end else if (output_fd_ready & output_fd_valid_reg & write) begin
        byte_count_reg <= byte_count_reg + input_fd_len - fd_len_reg;
    end else if (output_fd_ready & output_fd_valid_reg) begin
        count_reg <= count_reg - 1;
        byte_count_reg <= byte_count_reg - fd_len_reg;
    end else if (write) begin
        count_reg <= count_reg + 1;
        byte_count_reg <= byte_count_reg + input_fd_len;
    end
end

endmodule
