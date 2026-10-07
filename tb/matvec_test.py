import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import numpy as np

async def reset_dut(dut):
    dut.rst.value = 1
    dut.in_valid.value = 0
    dut.out_ready.value = 0
    dut.matrix_valid.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.rst.value = 0
    await RisingEdge(dut.clk)


async def write_matrix_element(dut, addr, val):
    dut.matrix_valid.value = 1
    dut.matrix_wdata.value = int(val)
    dut.matrix_addr.value = addr

    while True:
        await RisingEdge(dut.clk)
        if dut.matrix_ready.value == 1:
            break

    dut.matrix_valid.value = 0


async def program_matrix(dut, matrix):
    addr = 0
    for i in range(4):
        for j in range(4):
            await write_matrix_element(dut, addr, matrix[i][j])
            addr = addr + 1


def pack_input_vector(x):
    packed = 0

    for i in range(4):
        packed |= (x[i] & 0xFFFF) << (16*i)

    return packed

def unpack_output_vector(raw):
    unpacked = np.zeros(4);
    raw = int(raw)

    for i in range(4):
        value = (raw >> (34*i)) & ((1 << 34) - 1)

        if value &( 1 << 33):
            value -= 1 << 34

        unpacked[i] = value

    return unpacked

async def send_vector(dut, vec):
    dut.in_valid.value = 1
    dut.in_data.value = int(pack_input_vector(vec))

    while True:
        await RisingEdge(dut.clk)

        if(dut.in_ready.value == 1):
            break

    dut.in_valid.value = 0


async def receive_vector(dut):
    dut.out_ready.value = 1

    while True:
        await RisingEdge(dut.clk)

        if(dut.out_valid.value == 1):
            out = dut.out_data.value
            break

    dut.out_ready.value = 0
    return unpack_output_vector(out)


@cocotb.test()
async def test_identity_matrix(dut):
    cocotb.start_soon(Clock(dut.clk, 5, unit="ns").start())

    await reset_dut(dut)

    identity = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    x = [10, -3, 25, -7]

    await program_matrix(dut, identity)
    await send_vector(dut, x)

    result = await receive_vector(dut)
    expected = x

    assert np.array_equal(result, expected), (
        f"Identity matrix failed:\n"
        f"input    = {x}\n"
        f"expected = {expected}\n"
        f"received = {result}"
    )

@cocotb.test()
async def test_complicated_positive_matrix(dut):
    cocotb.start_soon(Clock(dut.clk, 5, unit="ns").start())

    await reset_dut(dut)

    matrix = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ])

    x = np.array([17, 18, 19, 20])

    await program_matrix(dut, matrix)
    await send_vector(dut, x)

    result = await receive_vector(dut)
    expected = matrix @ x

    assert np.array_equal(result, expected), (
        f"Real Matrix failed:\n"
        f"input    = {x}\n"
        f"expected = {expected}\n"
        f"received = {result}\n"
    )

@cocotb.test()
async def test_simple_negative_matrix(dut):
    cocotb.start_soon(Clock(dut.clk, 5, unit="ns").start())

    await reset_dut(dut)

    matrix = np.array([
        [-1, -2, -3, -4],
        [-1, -1, -1, -1],
        [-1, -1, -1, -1],
        [-1, -1, -1, -1]
    ])

    x = np.array([-1, -2, -3, -4])

    await program_matrix(dut, matrix)
    await send_vector(dut, x)

    result = await receive_vector(dut)
    expected = matrix @ x

    assert np.array_equal(result, expected), (
        f"Real Matrix failed:\n"
        f"input    = {x}\n"
        f"expected = {expected}\n"
        f"received = {result}\n"
    )
    
@cocotb.test()
async def test_simple_positive_matrix(dut):
    cocotb.start_soon(Clock(dut.clk, 5, unit="ns").start())

    await reset_dut(dut)

    matrix = np.array([
        [1, 2, 3, 4],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1]
    ])

    x = np.array([1, 2, 3, 4])

    await program_matrix(dut, matrix)
    await send_vector(dut, x)

    result = await receive_vector(dut)
    expected = matrix @ x

    assert np.array_equal(result, expected), (
        f"Real Matrix failed:\n"
        f"input    = {x}\n"
        f"expected = {expected}\n"
        f"received = {result}\n"
    )

@cocotb.test()
async def test_simple_mixed_matrix(dut):
    cocotb.start_soon(Clock(dut.clk, 5, unit="ns").start())

    await reset_dut(dut)

    matrix = np.array([
        [1, 2, -3, 4],
        [-4, 3, 2, 1],
        [2, 1, -3, 4],
        [2, -1, 4, -3]
    ])

    x = np.array([-1, 2, -3, 4])

    await program_matrix(dut, matrix)
    await send_vector(dut, x)

    result = await receive_vector(dut)
    expected = matrix @ x

    assert np.array_equal(result, expected), (
        f"Real Matrix failed:\n"
        f"input    = {x}\n"
        f"expected = {expected}\n"
        f"received = {result}\n"
    )

