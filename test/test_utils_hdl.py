#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  # ## #  # #  ## # ## #    # ## ## #  # # ##  # # #  # #  ## ## ##  # ## # #

from myhdl import *
import numpy as np


# clock generator
def clockgen(clk, time):
    while True:
        yield delay(time)
        clk.next = not clk
