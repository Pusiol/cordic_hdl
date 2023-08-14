#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  # ## #  # #  ## # ## #    # ## ## #  # # ##  # # #  # #  ## ## ##  # ## # #

# MyHDL CORDIC core

from myhdl import *
import numpy as np


@block
def cordic_core_hdl(clk,
                    in_vld, in_x, in_y, in_z,
                    in_cmp_target,
                    out_vld, out_x, out_y, out_z,
                    nn=8, tlut=None,
                    phase_scale=2**15, trig_scale=2**12,
                    cmp_var='z'):
    """  This module implements a cordic rotation.

    Parameters:
        nn: number of iterations
        tlut: tangent precalculated values
        theta_scale: used for calc tlut if not gived
        cmp_var: variable used in direction decision

    Inputs:
        in_x, in_y, in_z: user inputs
        in_cmp_target: target

    Outputs:
        out_x, out_y, out_z: user outputs

    Notes:


    """
    if type(tlut) == type(None):
        tlut_values = np.round(
            phase_scale * np.arctan(2**(-np.arange(nn, dtype=float))))
        tlut = tuple([int(val) for val in tlut_values])
    else:
        nn = len(tlut)

    ct = Signal(intbv(0, min=0, max=nn+7))

    reg_x = Signal(intbv(0, min=-trig_scale*2**2, max=trig_scale*2**2))
    reg_y = Signal(intbv(0, min=-trig_scale*2**2, max=trig_scale*2**2))
    reg_z = Signal(intbv(0, min=-phase_scale*2**2, max=phase_scale*2**2))

    var_aux_x = Signal(intbv(0,  min=-trig_scale*2**2, max=trig_scale*2**2))
    var_aux_y = Signal(intbv(0,  min=-trig_scale*2**2, max=trig_scale*2**2))

    # assigning the va
    if cmp_var == 'x':
        cmp_value = Signal(
            intbv(0,  min=-trig_scale*2**2, max=trig_scale*2**2))

        @always_comb
        def core_set_cmp_var():
            cmp_value.next = reg_x
    elif cmp_var == 'y':
        cmp_value = Signal(
            intbv(0,  min=-trig_scale*2**2, max=trig_scale*2**2))

        @always_comb
        def core_set_cmp_var():
            cmp_value.next = reg_y
    else:
        cmp_value = Signal(
            intbv(0,  min=-phase_scale*2**2, max=phase_scale*2**2))

        @always_comb
        def core_set_cmp_var():
            cmp_value.next = reg_z

    @always_comb
    def core_calc_instant_shift():
        if ct > 0:
            var_aux_x.next = reg_x >> (ct-1)
            var_aux_y.next = reg_y >> (ct-1)

    @always(clk.posedge)
    def core_rot():
        if ct == 0:
            out_vld.next = 0
            if in_vld == 1:
                reg_x.next = in_x
                reg_y.next = in_y
                reg_z.next = in_z
                ct.next = 1
        elif ct > nn:
            out_vld.next = 1
            out_x.next = reg_x
            out_y.next = reg_y
            out_z.next = reg_z
            ct.next = 0
        else:
            xphase = tlut[ct-1]
            if cmp_value < in_cmp_target:
                reg_z.next = reg_z + xphase
                reg_x.next = reg_x - var_aux_y
                reg_y.next = reg_y + var_aux_x
            else:
                reg_z.next = reg_z - xphase
                reg_x.next = reg_x + var_aux_y
                reg_y.next = reg_y - var_aux_x
            ct.next = ct+1

    return core_set_cmp_var, core_calc_instant_shift, core_rot
