#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  # ## #  # #  ## # ## #    # ## ## #  # # ##  # # #  # #  ## ## ##  # ## # #

# CORDIC-based computation of Cos, Sin, ArcCos and ArcSin

import numpy as np
import matplotlib.pyplot as plt


def cordic_core(xx, yy, zz, cmp_target, tlut, nn, cmp_var='z'):
    xtmp = xx
    ytmp = yy
    for idx in range(nn):
        if cmp_var == 'x':
            cmp_value = xx
        elif cmp_var == 'y':
            cmp_value = yy
        else:
            cmp_value = zz

        if cmp_value < cmp_target:
            zz = zz + tlut[idx]
            xx = xx - ytmp
            yy = yy + xtmp
        else:
            zz = zz - tlut[idx]
            xx = xx + ytmp
            yy = yy - xtmp
        xtmp = int(xx) >> (idx+1)
        ytmp = int(yy) >> (idx+1)
    return xx, yy, zz


def direte_comp_test(dbg=0):
    trig_scale = 10000
    phase_scale = 2**15
    theta = np.round(phase_scale * np.arange(-np.pi/2, np.pi/2, 2**-4))
    ref = trig_scale * np.exp(-1j*theta/phase_scale)

    i = np.zeros(len(theta), dtype=int)
    q = np.zeros(len(theta), dtype=int)
    z = np.zeros(len(theta), dtype=int)

    n = 8
    tlut = np.round(phase_scale * np.arctan(2**(-np.arange(n, dtype=float))))

    # CORDIC gain
    AnGain = np.prod(np.sqrt(1+2**(-2*np.arange(n, dtype=float))))
    inv_AnGain = int(trig_scale / AnGain)

    for idx in range(len(theta)):
        i[idx], q[idx], z[idx] = cordic_core(
            inv_AnGain, 0, theta[idx], 0, tlut, n, cmp_var='z')

    if dbg:
        fig, axs = plt.subplots(2)
        fig.suptitle("Direte computations")
        axs[0].plot(theta/phase_scale, np.real(ref) /
                    trig_scale, "y-", label="reference")
        axs[0].plot(theta/phase_scale, i/trig_scale,
                    "b.", label="cordic output")
        axs[0].legend()
        axs[0].set_xlabel("arc [rad]")
        axs[0].set_ylabel("cos(x)")
        axs[0].set_title("Cosine")
        axs[1].plot(theta/phase_scale, np.imag(ref) /
                    trig_scale, "y-", label="reference")
        axs[1].plot(theta/phase_scale, q/trig_scale,
                    "b.", label="cordic output")
        axs[1].legend()
        axs[1].set_xlabel("arc [rad]")
        axs[1].set_ylabel("sin(x)")
        axs[1].set_title("Sine")
        plt.show()

    return theta, i, q


def inverse_comp_test(dbg=0):
    trig_scale = 10000
    phase_scale = 2**15
    alfa = trig_scale * np.arange(-1, 1, 2**-4)
    ref_arcsin = phase_scale * np.arcsin(alfa/trig_scale)
    ref_arccos = phase_scale * np.arccos(alfa/trig_scale)

    i_arcsin = np.zeros(len(alfa), dtype=int)
    q_arcsin = np.zeros(len(alfa), dtype=int)
    z_arcsin = np.zeros(len(alfa), dtype=int)
    i_arccos = np.zeros(len(alfa), dtype=int)
    q_arccos = np.zeros(len(alfa), dtype=int)
    z_arccos = np.zeros(len(alfa), dtype=int)

    n = 8
    tlut = np.round(phase_scale * np.arctan(2**(-np.arange(n, dtype=float))))

    # CORDIC gain
    AnGain = np.prod(np.sqrt(1+2**(-2*np.arange(n, dtype=float))))
    alfa_cor = np.round(AnGain*alfa)

    for idx in range(len(alfa)):
        i_arcsin[idx], q_arcsin[idx], z_arcsin[idx] = cordic_core(
            trig_scale, 0, 0, alfa_cor[idx], tlut, n, cmp_var='y')
        i_arccos[idx], q_arccos[idx], z_arccos[idx] = cordic_core(
            0, trig_scale, 0, alfa_cor[idx], tlut, n, cmp_var='y')

    if dbg:
        fig, axs = plt.subplots(2)
        fig.suptitle("Inverse computations")
        axs[0].plot(alfa/trig_scale, ref_arcsin /
                    phase_scale, "y-", label="reference")
        axs[0].plot(alfa/trig_scale, z_arcsin /
                    phase_scale, "b.", label="cordic output")
        axs[0].legend()
        axs[0].set_xlabel("sin")
        axs[0].set_ylabel("ArcSin(alfa) [rad]")
        axs[0].set_title("ArcSin")
        axs[1].plot(alfa/trig_scale, ref_arccos /
                    phase_scale, "y-", label="reference")
        axs[1].plot(alfa/trig_scale, -z_arccos/phase_scale,
                    "b.", label="cordic output")
        axs[1].legend()
        axs[1].set_xlabel("cos")
        axs[1].set_ylabel("ArcCos(alfa) [rad]")
        axs[1].set_title("ArcCos")
        plt.show()

    return alfa_cor, z_arcsin, z_arccos


if __name__ == "__main__":
    direte_comp_test(dbg=1)
    inverse_comp_test(dbg=1)
