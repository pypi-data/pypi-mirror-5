# -*- coding: utf-8 -*-
# Copyright 2007-2011 The Hyperspy developers
#
# This file is part of  Hyperspy.
#
#  Hyperspy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  Hyperspy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  Hyperspy.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np

from hyperspy.decorators import auto_replot
from hyperspy.signals.spectrum import Spectrum

class SpectrumSimulation(Spectrum):
    def __init__(self, *args, **kwargs):
        super(SpectrumSimulation, self).__init__(*args, **kwargs)

    @auto_replot
    def add_poissonian_noise(self, **kwargs):
        """Add Poissonian noise to the data"""
        original_type = self.data.dtype
        self.data = np.random.poisson(self.data, **kwargs).astype(
                                      original_type)

    @auto_replot
    def add_gaussian_noise(self, std, **kwargs):
        """Add Gaussian noise to the data
        Parameters
        ----------
        std : float

        """
        noise = np.random.normal(0, std, self.data.shape, **kwargs)
        self.data += noise



