# Four-Lane MAC Engine

The datapath contains four parallel multiply-accumulate lanes.

Each MAC lane corresponds to one output row of matrix $A$:

- Lane 0 computes $y_0$
- Lane 1 computes $y_1$
- Lane 2 computes $y_2$
- Lane 3 computes $y_3$

During each compute cycle, all four lanes process the same input-vector
element $x_j$, while each lane reads the coefficient from its
corresponding matrix row.

For lane $i$:

$$
acc_i \leftarrow acc_i + A_{ij}x_j
$$

The column index $j$ advances from 0 through 3.

After four MAC operations, the completed value for each lane is $y_i$.

The target initiation interval is four cycles. Exact end-to-end latency
depends on pipeline and output-register placement.

### Control

A 2-bit column counter `j` tracks the currently processed vector
element and matrix column.

During each compute cycle, `j` advances from 0 through 3.

When `j = 3`, the final accumulation completes and the four results are
made available to the output interface.

The datapath may accept another input vector once the accumulator
resources required for the previous vector are available.

Output backpressure may prevent a new computation from beginning if no
storage is available for the completed result.

A compute-active state bit tracks whether a vector computation is
currently in progress.

When a vector is accepted, compute-active is asserted and `j` begins
at 0. After the final computation for `j = 3`, compute-active is
cleared.

Matrix writes and input-vector transactions are mutually exclusive. While `matrix_we` is asserted, `in_ready` is deasserted.

### Datapath

Lane 0: $ A_{0j} * x_j \rightarrow acc_0 \rightarrow y_0 $ \
Lane 1: $ A_{1j} * x_j \rightarrow acc_1 \rightarrow y_1 $ \
Lane 2: $ A_{2j} * x_j \rightarrow acc_2 \rightarrow y_2 $ \
Lane 3: $ A_{3j} * x_j \rightarrow acc_3 \rightarrow y_3 $

All four lanes process the same $x_j$ each cycle but use different matrix rows.

| Value | Width |
|---|---:|
| $x_j$ | signed 16-bit |
| $A_{ij}$ | signed 16-bit |
| Product | signed 32-bit |
| $acc_i$ | signed 34-bit |
| $y_i$ | signed 34-bit |

i`in_data` $\rightarrow$ `x_reg`

`x_reg` and matrix storage $\rightarrow$ 4 parallel MACs
$\rightarrow$ accumulators $\rightarrow$ `out_reg`
$\rightarrow$ `out_data`

Each signed 32-bit multiplication result is sign-extended to 34 bits
before being added to the corresponding 34-bit accumulator.

### Input Storage

Internal register `x_reg[0:3]` is loaded with `in_data` when `in_valid` && `in_ready` 

### Output Storage

The four completed 34-bit results are stored in a 136-bit output
register `out_reg`.

`out_data` is driven from `out_reg`.

When a result is written to `out_reg`, `out_valid` is asserted.

If `out_valid = 1` and `out_ready = 0`, both `out_valid` and
`out_reg` remain unchanged.

When `out_valid = 1` and `out_ready = 1` on a rising clock edge,
the output transaction completes.

### Matrix Storage

The matrix is stored as sixteen 16-bit signed registers arranged
logically as `A[0:3][0:3]`.

During compute cycle `j`, four coefficients are read in parallel:

$A_{0j}$, $A_{1j}$, $A_{2j}$, and $A_{3j}$.

These four values feed the four MAC lanes respectively.

### Cycle Schedule

| Cycle | Input | Accumulator operation |
|---|---|---|
| 0 | $x_0$ | $acc_i \leftarrow A_{i0}x_0$ |
| 1 | $x_1$ | $acc_i \leftarrow acc_i + A_{i1}x_1$ |
| 2 | $x_2$ | $acc_i \leftarrow acc_i + A_{i2}x_2$ |
| 3 | $x_3$ | $out_i \leftarrow acc_i + A_{i3}x_3$ |

for all four lanes $i \in \{0,1,2,3\}$.

After the final compute edge, `out_reg` contains the four completed output elements $y_0$ through $y_3$ and out_valid is asserted.

The initial microarchitecture treats each multiply-accumulate operation as a single-cycle datapath operation. Additional internal pipelining may be introduced if required to meet the 200 MHz timing target, provided the required initiation interval is preserved.

### Handshake Behavior

A new input vector may be accepted when the MAC datapath is idle and either the output register is empty or its current contents will be transferred on the same rising clock edge.

On an input handshake, the complete 64-bit in_data vector is captured into x_reg[0:3]. On that same edge, $x_0$ is taken directly from in_data[15:0] for the first MAC operation. Subsequent compute cycles use `x_reg[1]`, `x_reg[2]`, and `x_reg[3]`.

On the final compute cycle ($j=3$), the final MAC result is written directly into the output register.

### Resource Estimate

### Resource Estimate

| Resource | Count / Width |
|---|---:|
| Signed multipliers | 4 × 16×16 |
| Accumulators | 4 × 34-bit |
| Input vector register | 1 × 64-bit |
| Matrix storage | 16 × 16-bit |
| Column counter | 1 × 2-bit |
| Compute-active state | 1 bit |
| Output-valid state | 1 bit |
| Output register | 1 × 136-bit |



### Timing Table

| Rising Edge | Event |
|---|---|
| $N$ | Accept vector A; compute A, $j=0$ |
| $N+1$ | Compute A, $j=1$ |
| $N+2$ | Compute A, $j=2$ |
| $N+3$ | Compute A, $j=3$; write output A |
| $N+4$ | Transfer output A and accept vector B; compute B, $j=0$ |
| $N+5$ | Compute B, $j=1$ |
| $N+6$ | Compute B, $j=2$ |
| $N+7$ | Compute B, $j=3$; write output B |
| $N+8$ | Transfer output B and accept vector C; compute C, $j=0$ |