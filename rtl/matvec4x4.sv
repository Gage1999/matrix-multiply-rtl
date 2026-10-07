module matvec4x4(
    input logic clk,
    input logic rst,

    input logic [3:0] matrix_addr,
    input logic [15:0] matrix_wdata,
    input logic matrix_valid,
    output logic matrix_ready,

    input logic [63:0] in_data,
    input logic in_valid,
    output logic in_ready,

    output logic [135:0] out_data,
    output logic out_valid,
    input logic out_ready
);

    logic signed [15:0] matrix [0:3][0:3];
    logic signed [15:0] in_reg [0:3];

    logic signed [33:0] acc [0:3];

    logic [1:0] j;
    logic compute_active;
    logic computing;

    logic [135:0] out_reg;

    initial begin
        j = 0;
        computing = 0;
        out_valid = 0;

        for(int i = 0; i < 4; i++) begin
            acc[i] = '0;
            for(int k = 0; k < 4; k++) begin
                matrix[i][k] = '0;
            end
        end
    end

    always_comb begin
        out_data = out_valid && out_ready ? out_reg : '0;
        in_ready = !computing || out_valid && out_ready ? 1'b1 : '0;
        compute_active = in_ready && in_valid || computing;
        matrix_ready = !compute_active;
    end

    always_ff @(posedge clk) begin
        if(rst) begin
            for(int i = 0; i < 4; i++) begin
                in_reg[i] <= '0;
                acc[i] <= '0;
                out_reg <= '0;
                out_valid <= '0;
            end
            j <= '0;
        end else begin
            if(compute_active) begin
                if(j==3) j <= '0;
                else j <= j + 1;

                case (j)
                0: begin
                    in_reg[0] <= $signed(in_data[15:0]);
                    in_reg[1] <= $signed(in_data[31:16]);
                    in_reg[2] <= $signed(in_data[47:32]);
                    in_reg[3] <= $signed(in_data[63:48]);

                    for(int i = 0; i < 4; i++) begin
                        acc[i] <= $signed(in_data[15:0]) * matrix[i][j];
                    end

                    computing <= 1;
                    out_valid <= '0;
                end

                1: begin
                    for(int i = 0; i < 4; i++) begin
                        acc[i] <= acc[i] + in_reg[j] * matrix[i][j];
                    end
                end

                2: begin
                    for(int i = 0; i < 4; i++) begin
                        acc[i] <= acc[i] + in_reg[j] * matrix[i][j];
                    end
                end

                3: begin

                    out_reg[33:0] <= acc[0] + in_reg[j] * matrix[0][j];
                    out_reg[67:34] <= acc[1] + in_reg[j] * matrix[1][j];
                    out_reg[101:68] <= acc[2] + in_reg[j] * matrix[2][j];
                    out_reg[135:102] <= acc[3] + in_reg[j] * matrix[3][j];

                    out_valid <= 1;
                    computing <= 0;
                end
                endcase
            end

            else if(matrix_valid && matrix_ready) begin
                matrix[matrix_addr / 4][matrix_addr % 4] <= matrix_wdata;
            end
        end
    end
endmodule
