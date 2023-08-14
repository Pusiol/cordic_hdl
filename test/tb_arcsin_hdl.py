#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  # ## #  # #  ## # ## #    # ## ## #  # # ##  # # #  # #  ## ## ##  # ## # #

import unittest

from myhdl import *
import numpy as np
import matplotlib.pyplot as plt
import os

from test_utils_hdl import *

import sys
sys.path.append('../')   # noqa
from cordic_core_prot import *
from cordic_core_hdl import *

native_sim = 1
print_vcd = 0

in_wid = 16
tt_phase_scale = 2**15
tt_trig_scale = 10000


def cordic_core_hdl_c(clk,
                      in_vld, in_x, in_y, in_z,
                      in_cmp_target,
                      out_vld, out_x, out_y, out_z):
    os.system(
        "iverilog -o cordic_core_hdl.o cordic_core_hdl.v tb_cordic_core_hdl.v")
    return Cosimulation("vvp -m /home/" +
                        os.getlogin() +
                        "/git/myhdl/cosimulation/icarus/myhdl.vpi cordic_core_hdl.o", **locals())


class TestHardVit(unittest.TestCase):
    def test_sweep(self):
        def test(clk,
                 in_vld, in_x, in_y, in_z,
                 in_cmp_target,
                 out_vld, out_x, out_y, out_z):

            alfa, z_arcsin, _ = inverse_comp_test()

            while True:
                for ii in range(len(alfa)):
                    in_vld.next = 1
                    in_cmp_target.next = int(alfa[ii])
                    while True:
                        yield clk.posedge
                        in_vld.next = 0
                        if out_vld == 1:
                            self.assertEqual(out_z, z_arcsin[ii])
                            break

                raise StopSimulation
        self.runTests(test)

    def runTests(self, test):
        """Helper method to run the actual tests."""

        clk = Signal(False)

        # CORDIC gain
        nn = 8
        AnGain = np.prod(np.sqrt(1+2**(-2*np.arange(nn, dtype=float))))
        inv_AnGain = int(tt_trig_scale / AnGain)

        in_vld = Signal(False)
        in_x = tt_trig_scale
        in_y = 0
        phase_wid = int(np.ceil(np.log2(tt_phase_scale))+2)
        in_z = 0

        in_cmp_target = Signal(intbv(0, min=-2**(in_wid-1), max=2**(in_wid-1)))

        out_vld = Signal(False)
        out_x = Signal(intbv(0, min=-2**(in_wid-1), max=2**(in_wid-1)))
        out_y = Signal(intbv(0, min=-2**(in_wid-1), max=2**(in_wid-1)))
        out_z = Signal(intbv(0, min=-2**(phase_wid-1), max=2**(phase_wid-1)))

        # design under test
        dut = cordic_core_hdl(clk,
                              in_vld, in_x, in_y, in_z,
                              in_cmp_target,
                              out_vld, out_x, out_y, out_z,
                              nn=nn, tlut=None,
                              phase_scale=tt_phase_scale, trig_scale=tt_trig_scale,
                              cmp_var='y')

        if native_sim == 1:
            dut.convert(hdl='Verilog', initial_values=True)
            dut = cordic_core_hdl_c(clk,
                                    in_vld, in_x, in_y, in_z,
                                    in_cmp_target,
                                    out_vld, out_x, out_y, out_z)

        clock = clockgen(clk, 10)
        check = test(clk,
                     in_vld, in_x, in_y, in_z,
                     in_cmp_target,
                     out_vld, out_x, out_y, out_z)
        sim = Simulation(clock, dut, check)
        if print_vcd == 1:
            dut.config_sim(trace=True)
        sim.run(quiet=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
