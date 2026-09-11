# 4x4 Matrix-Vector Multiply Block

The block stores an internal 4x4 transformation matrix \(A\).

For each incoming 4x1 vector \(x\), the block computes the 4x1
output vector \(y\):

$$
y = Ax
$$

where each output element is

$$
y_i = \sum_{j=0}^{3} A_{ij}x_j,
\qquad i \in \{0,1,2,3\}
$$

Matrix elements and input vector elements are 16-bit signed
two's-complement integers.

Each multiplication produces a 32-bit signed intermediate product.

All multiply and accumulate operations retain full precision. No
saturation or truncation is performed.

Each output element is represented as a 34-bit signed two's-complement
integer, allowing the sum of four 16-bit x 16-bit products to be
represented without arithmetic overflow.

Matrix contents may only be modified while the block is idle, where
idle means that no vector computation is in progress and no output
vector is awaiting transfer.

Matrix contents are unspecified until explicitly programmed. The matrix must be programmed before the first input vector is accepted.

Matrix contents may be updated one element at a time using `matrix_we`, `matrix_addr[3:0]`, and `matrix_wdata[15:0]`. When matrix_we is asserted while the block is idle, the 16-bit value on matrix_wdata is written to the matrix element selected by matrix_addr.

Matrix addresses use row-major ordering, where `matrix_addr` = 4*i + j corresponds to \(A_{ij}\).

Matrix writes occur on a rising edge when `matrix_we` = 1 and the block is idle.

A complete 4-element input vector is transferred in a single input
transaction.

A complete 4-element output vector is transferred in a single output
transaction.

The input vector is presented on a 64-bit bus containing four signed 16-bit elements. The output vector is presented on a 136-bit bus containing four signed 34-bit elements.

The input interface uses valid/ready handshaking. `in_valid` indicates
that the input bus contains a valid vector. `in_ready` indicates that
the block can accept the vector. A transfer occurs on a rising clock
edge when both are asserted.

The output interface uses valid/ready handshaking. `out_valid`
indicates that the output bus contains a valid result. `out_ready`
indicates that the downstream consumer can accept the result. A
transfer occurs on a rising clock edge when both are asserted.

When `in_valid` is asserted and `in_ready` is deasserted, the input
vector must remain stable until the transaction completes.

When `out_valid` is asserted and `out_ready` is deasserted, the block
must hold `out_valid` and the output vector constant until the
transaction completes.

### Vector Bus Packing

The least-significant element occupies the least-significant bits of each bus.

| Bus | Bit Range | Vector Element |
|---|---:|---|
| `in_data` | `[15:0]` | \(x_0\) |
| `in_data` | `[31:16]` | \(x_1\) |
| `in_data` | `[47:32]` | \(x_2\) |
| `in_data` | `[63:48]` | \(x_3\) |
| `out_data` | `[33:0]` | \(y_0\) |
| `out_data` | `[67:34]` | \(y_1\) |
| `out_data` | `[101:68]` | \(y_2\) |
| `out_data` | `[135:102]` | \(y_3\) |

The design uses a synchronous active-high reset.

Reset discards all in-flight computations and pending outputs, clears all valid state, and does not modify matrix contents.

The design targets a clock frequency of 200 MHz.

The design must support accepting a new input vector at least once every 4 clock cycles and producing one output vector every 4 clock cycles in steady state.