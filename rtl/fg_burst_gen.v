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
 * Flow generator - burst generator module
 */
module fg_burst_gen #(
    parameter FLOW_ADDR_WIDTH = 5,
    parameter DEST_WIDTH = 8,
    parameter RATE_SCALE = 8
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
     * Burst descriptor output
     */
    output wire                   output_bd_valid,
    input  wire                   output_bd_ready,
    output wire [DEST_WIDTH-1:0]  output_bd_dest,
    output wire [31:0]            output_bd_burst_len,

    /*
     * Status
     */
    output wire busy,
    output wire [FLOW_ADDR_WIDTH-1:0] active_flows

    /*
     * Configuration
     */
);

reg [FLOW_ADDR_WIDTH-1:0] cur_flow_reg = 0, cur_flow_next;

// flow state
reg update_flow_state;
reg        flow_active[(2**FLOW_ADDR_WIDTH)-1:0], cur_flow_active, flow_active_next;
reg [DEST_WIDTH-1:0]  flow_dest[(2**FLOW_ADDR_WIDTH)-1:0], cur_flow_dest, flow_dest_next;
reg [15:0] flow_rate_num[(2**FLOW_ADDR_WIDTH)-1:0], cur_flow_rate_num, flow_rate_num_next;
reg [15:0] flow_rate_denom[(2**FLOW_ADDR_WIDTH)-1:0], cur_flow_rate_denom, flow_rate_denom_next;
reg [31:0] flow_len[(2**FLOW_ADDR_WIDTH)-1:0], cur_flow_len, flow_len_next;
reg [31:0] flow_burst_len[(2**FLOW_ADDR_WIDTH)-1:0], cur_flow_burst_len, flow_burst_len_next;
reg [31:0] flow_delay[(2**FLOW_ADDR_WIDTH)-1:0], cur_flow_delay, flow_delay_next;

integer i;

initial begin
    for (i = 0; i < 2**FLOW_ADDR_WIDTH; i = i + 1) begin
        flow_active[i] <= 0;
        flow_dest[i] <= 0;
        flow_rate_num[i] <= 0;
        flow_rate_denom[i] <= 0;
        flow_len[i] <= 0;
        flow_burst_len[i] <= 0;
        flow_delay[i] <= 0;
    end
end

// debug
wire [DEST_WIDTH-1:0] flow_dest_0 = flow_dest[0];
wire [15:0]           flow_rate_num_0 = flow_rate_num[0];
wire [15:0]           flow_rate_denom_0 = flow_rate_denom[0];
wire [31:0]           flow_len_0 = flow_len[0];
wire [31:0]           flow_burst_len_0 = flow_burst_len[0];
wire [31:0]           flow_delay_0 = flow_delay[0];

reg input_fd_ready_reg = 0, input_fd_ready_next;

reg busy_reg = 0;

reg [FLOW_ADDR_WIDTH-1:0] active_flows_reg = 0, active_flows_next;

// internal datapath
reg [DEST_WIDTH-1:0] output_bd_dest_int;
reg [31:0]           output_bd_burst_len_int;
reg                  output_bd_valid_int;
reg                  output_bd_ready_int = 0;
wire                 output_bd_ready_int_early;

assign input_fd_ready = input_fd_ready_reg;

assign busy = busy_reg;

assign active_flows = active_flows_reg;

always @* begin
    cur_flow_next = cur_flow_reg+1;

    input_fd_ready_next = 0;

    output_bd_dest_int = 0;
    output_bd_burst_len_int = 0;
    output_bd_valid_int = 0;

    update_flow_state = 0;

    flow_active_next = cur_flow_active;
    flow_dest_next = cur_flow_dest;
    flow_rate_num_next = cur_flow_rate_num;
    flow_rate_denom_next = cur_flow_rate_denom;
    flow_len_next = cur_flow_len;
    flow_burst_len_next = cur_flow_burst_len;
    flow_delay_next = cur_flow_delay;

    active_flows_next = active_flows_reg;

    if (cur_flow_active) begin
        // flow has data to send
        if (cur_flow_delay >= (cur_flow_rate_num * RATE_SCALE * (2**FLOW_ADDR_WIDTH))) begin
            // waiting - update counter
            flow_delay_next = cur_flow_delay - (cur_flow_rate_num * RATE_SCALE * (2**FLOW_ADDR_WIDTH));
            update_flow_state = 1;
        end else begin
            // send burst
            output_bd_dest_int = cur_flow_dest;
            output_bd_valid_int = 1;
            if (cur_flow_len > cur_flow_burst_len) begin
                // not last burst
                flow_len_next = cur_flow_len - cur_flow_burst_len;
                flow_delay_next = cur_flow_delay + (cur_flow_burst_len * cur_flow_rate_denom) - (cur_flow_rate_num * RATE_SCALE * (2**FLOW_ADDR_WIDTH));
                output_bd_burst_len_int = cur_flow_burst_len;
                update_flow_state = 1;
            end else begin
                // last burst
                flow_active_next = 0;
                flow_len_next = 0;
                flow_delay_next = 0;
                output_bd_burst_len_int = cur_flow_len;
                update_flow_state = 1;
                active_flows_next = active_flows - 1;
            end
        end
    end else if (input_fd_valid & ~input_fd_ready) begin
        // read new flow descriptor into empty slot
        input_fd_ready_next = 1;
        update_flow_state = 1;
        flow_active_next = 1;
        flow_dest_next = input_fd_dest;
        flow_rate_num_next = input_fd_rate_num;
        flow_rate_denom_next = input_fd_rate_denom;
        flow_len_next = input_fd_len;
        flow_burst_len_next = input_fd_burst_len;
        flow_delay_next = 0;
        active_flows_next = active_flows + 1;
    end
end

always @(posedge clk) begin
    if (rst) begin
        for (i = 0; i < 2**FLOW_ADDR_WIDTH; i = i + 1) begin
            flow_active[i] <= 0;
        end
    end else begin
        cur_flow_active <= flow_active[cur_flow_next];
        cur_flow_dest <= flow_dest[cur_flow_next];
        cur_flow_rate_num <= flow_rate_num[cur_flow_next];
        cur_flow_rate_denom <= flow_rate_denom[cur_flow_next];
        cur_flow_len <= flow_len[cur_flow_next];
        cur_flow_burst_len <= flow_burst_len[cur_flow_next];
        cur_flow_delay <= flow_delay[cur_flow_next];

        if (update_flow_state) begin
            flow_active[cur_flow_reg] <= flow_active_next;
            flow_dest[cur_flow_reg] <= flow_dest_next;
            flow_rate_num[cur_flow_reg] <= flow_rate_num_next;
            flow_rate_denom[cur_flow_reg] <= flow_rate_denom_next;
            flow_len[cur_flow_reg] <= flow_len_next;
            flow_burst_len[cur_flow_reg] <= flow_burst_len_next;
            flow_delay[cur_flow_reg] <= flow_delay_next;
        end
    end
end

always @(posedge clk or posedge rst) begin
    if (rst) begin
        cur_flow_reg <= 0;
        input_fd_ready_reg <= 0;
        busy_reg <= 0;
        active_flows_reg <= 0;
    end else begin
        cur_flow_reg <= cur_flow_next;
        input_fd_ready_reg <= input_fd_ready_next;
        busy_reg <= active_flows_next != 0;
        active_flows_reg <= active_flows_next;
    end
end

// output datapath logic
reg [DEST_WIDTH-1:0] output_bd_dest_reg = 0;
reg [31:0]           output_bd_burst_len_reg = 0;
reg                  output_bd_valid_reg = 0;

reg [DEST_WIDTH-1:0] temp_bd_dest_reg = 0;
reg [31:0]           temp_bd_burst_len_reg = 0;
reg                  temp_bd_valid_reg = 0;

assign output_bd_dest = output_bd_dest_reg;
assign output_bd_burst_len = output_bd_burst_len_reg;
assign output_bd_valid = output_bd_valid_reg;

// enable ready input next cycle if output is ready or if there is space in both output registers or if there is space in the temp register that will not be filled next cycle
assign output_bd_ready_int_early = output_bd_ready | (~temp_bd_valid_reg & ~output_bd_valid_reg) | (~temp_bd_valid_reg & ~output_bd_valid_int);

always @(posedge clk or posedge rst) begin
    if (rst) begin
        output_bd_dest_reg <= 0;
        output_bd_burst_len_reg <= 0;
        output_bd_valid_reg <= 0;
        output_bd_ready_int <= 0;
        temp_bd_dest_reg <= 0;
        temp_bd_burst_len_reg <= 0;
        temp_bd_valid_reg <= 0;
    end else begin
        // transfer sink ready state to source
        output_bd_ready_int <= output_bd_ready_int_early;

        if (output_bd_ready_int) begin
            // input is ready
            if (output_bd_ready | ~output_bd_valid_reg) begin
                // output is ready or currently not valid, transfer data to output
                output_bd_dest_reg <= output_bd_dest_int;
                output_bd_burst_len_reg <= output_bd_burst_len_int;
                output_bd_valid_reg <= output_bd_valid_int;
            end else begin
                // output is not ready, store input in temp
                temp_bd_dest_reg <= output_bd_dest_int;
                temp_bd_burst_len_reg <= output_bd_burst_len_int;
                temp_bd_valid_reg <= output_bd_valid_int;
            end
        end else if (output_bd_ready) begin
            // input is not ready, but output is ready
            output_bd_dest_reg <= temp_bd_dest_reg;
            output_bd_burst_len_reg <= temp_bd_burst_len_reg;
            output_bd_valid_reg <= temp_bd_valid_reg;
            temp_bd_dest_reg <= 0;
            temp_bd_valid_reg <= 0;
        end
    end
end

endmodule
