# 4x4 Matrix-Vector Multiply Block

### Functionality

The block stores an internal 4x4 transformation matrix $A$.

For each incoming 4x1 vector $x$, the block computes the 4x1
output vector $y$:

$$
y = Ax
$$

where each output element is

$$
y_i = \sum_{j=0}^{3} A_{ij}x_j,
\qquad i \in \{0,1,2,3\}
$$

### Data Widths and Types

Matrix elements and input vector elements are 16-bit signed
two's-complement integers.

Each multiplication produces a 32-bit signed intermediate product.

All multiply and accumulate operations retain full precision. No
saturation or truncation is performed.

Each output element is represented as a 34-bit signed two's-complement
integer, allowing the sum of four 16-bit x 16-bit products to be
represented without arithmetic overflow.

### Matrix Updates

Matrix contents may only be modified while the block is idle, where
idle means that no vector computation is in progress and no output
vector is awaiting transfer.

Matrix contents are unspecified until explicitly programmed. The matrix must be programmed before the first input vector is accepted.

Matrix contents may be updated one element at a time using a valid/ready
interface. The source drives `matrix_valid`, `matrix_addr[3:0]`, and
`matrix_wdata[15:0]`. The block drives `matrix_ready`.

`matrix_valid` indicates that the address and signed 16-bit write data
are valid. `matrix_ready` indicates that the block can accept a matrix
write. A write occurs on a rising clock edge when both signals are
asserted and reset is deasserted. The value on `matrix_wdata` is written
to the element selected by `matrix_addr`.

Matrix addresses use row-major ordering, where `matrix_addr` = 4*i + j corresponds to $A_{ij}$.

When `matrix_valid` is asserted and `matrix_ready` is deasserted, the
source must hold `matrix_valid`, `matrix_addr`, and `matrix_wdata`
stable until the write is accepted, unless reset is asserted. A write
request may therefore be presented while the block is busy; it does
not modify the matrix until the handshake completes.

Matrix writes and input-vector transactions are mutually exclusive.
An input-vector transaction takes priority: when a vector is accepted,
`matrix_ready` is deasserted and any pending matrix write must wait.
Otherwise, a matrix write may be accepted only while the block is idle.

Each accepted handshake writes one element. To program the full 4x4
matrix, the source supplies sixteen writes at addresses 0 through 15.
After an accepted write, the source may present the next address and
value while keeping `matrix_valid` asserted, or deassert `matrix_valid`
if no further write is pending. No matrix writes occur during reset.

### Vector Bus Packing

A complete 4-element input vector is transferred in a single input
transaction.

A complete 4-element output vector is transferred in a single output
transaction.

The input vector is presented on a 64-bit bus containing four signed 16-bit elements. The output vector is presented on a 136-bit bus containing four signed 34-bit elements.

The least-significant element occupies the least-significant bits of each bus.

| Bus | Bit Range | Vector Element |
|---|---:|---|
| `in_data` | `[15:0]` | $x_0$ |
| `in_data` | `[31:16]` | $x_1$ |
| `in_data` | `[47:32]` | $x_2$ |
| `in_data` | `[63:48]` | $x_3$ |
| `out_data` | `[33:0]` | $y_0$ |
| `out_data` | `[67:34]` | $y_1$ |
| `out_data` | `[101:68]` | $y_2$ |
| `out_data` | `[135:102]` | $y_3$ |

### Input + Output Interface

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

### Reset

The design uses a synchronous active-high reset.

Reset discards all in-flight computations and pending outputs, clears all valid state, and does not modify matrix contents.

While reset is asserted, out_valid is deasserted and no input or output transactions occur.

### Design Targets

The design targets a clock frequency of 200 MHz.

When input vectors are continuously available and the downstream interface does not apply backpressure, the design must support accepting a new input vector at least once every 4 clock cycles and producing one output vector every 4 clock cycles in steady state.
