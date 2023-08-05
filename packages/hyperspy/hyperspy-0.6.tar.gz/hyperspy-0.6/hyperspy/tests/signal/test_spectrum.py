# Copyright 2007-2012 The Hyperspy developers
#
# This file is part of Hyperspy.
#
# Hyperspy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hyperspy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hyperspy. If not, see <http://www.gnu.org/licenses/>.


import os

import numpy as np

from nose.tools import assert_true, assert_equal, assert_not_equal
from hyperspy.signals.spectrum import Spectrum

class TestAlignTools:
    def setUp(self):
        s = Spectrum(np.zeros((10,100)))
        self.scale = 0.1
        self.offset = -2
        eaxis = s.axes_manager.signal_axes[0]
        eaxis.scale = self.scale
        eaxis.offset = self.offset
        self.izlp = eaxis.value2index(0)
        self.bg = 2
        self.ishifts = np.array([0,  4,  2, -2,  5, -2, -5, -9, -9, -8])
        self.new_offset = self.offset - self.ishifts.min() * self.scale
        s.data[np.arange(10), self.ishifts + self.izlp] = 10
        s.data += self.bg
        self.spectrum = s
        
    def test_estimate_shift(self):
        s = self.spectrum
        eshifts = -1 * s.estimate_shift1D()
        assert_true(np.allclose(eshifts, self.ishifts * self.scale))
        
    def test_shift1D(self):
        s = self.spectrum
        s.shift1D(-1 * self.ishifts[:, np.newaxis] * self.scale)
        i_zlp = s.axes_manager.signal_axes[0].value2index(0)
        assert_true(np.allclose(s.data[:, i_zlp], 12))
        # Check that at the edges of the spectrum the value == to the
        # background value. If it wasn't it'll mean that the cropping
        # code is buggy
        assert_true((s.data[:,-1] == 2).all())
        assert_true((s.data[:,0] == 2).all())
        # Check that the calibration is correct
        assert_equal(s.axes_manager._axes[1].offset, self.new_offset)
        assert_equal(s.axes_manager._axes[1].scale, self.scale)
        
    def test_align(self):
        s = self.spectrum
        s.align1D()
        i_zlp = s.axes_manager.signal_axes[0].value2index(0)
        assert_true(np.allclose(s.data[:, i_zlp], 12))
        # Check that at the edges of the spectrum the value == to the
        # background value. If it wasn't it'll mean that the cropping
        # code is buggy
        assert_true((s.data[:,-1] == 2).all())
        assert_true((s.data[:,0] == 2).all())
        # Check that the calibration is correct
        assert_equal(s.axes_manager._axes[1].offset, self.new_offset)
        assert_equal(s.axes_manager._axes[1].scale, self.scale)
        
    def test_align_axis0(self):
        s = self.spectrum
        s.swap_axes(0, 1)
        s.align1D()
        s.swap_axes(0, 1)
        i_zlp = s.axes_manager.signal_axes[0].value2index(0)
        assert_true(np.allclose(s.data[:, i_zlp], 12))
        # Check that at the edges of the spectrum the value == to the
        # background value. If it wasn't it'll mean that the cropping
        # code is buggy
        assert_true((s.data[:,-1] == 2).all())
        assert_true((s.data[:,0] == 2).all())
        # Check that the calibration is correct
        assert_equal(s.axes_manager._axes[1].offset, self.new_offset)
        assert_equal(s.axes_manager._axes[1].scale, self.scale)
        
class TestFindPeaks1D:
    def setUp(self):
        x = np.arange(0,50,0.01)
        s = Spectrum(np.vstack((np.cos(x), np.sin(x))))
        s.axes_manager.signal_axes[0].scale = 0.01
        self.peak_positions0 = np.arange(8) *2 * np.pi
        self.peak_positions1 = np.arange(8) *2 * np.pi + np.pi/2
        self.spectrum = s
        
        
    def test_single_spectrum(self):
        peaks = self.spectrum[0].find_peaks1D_ohaver()
        assert_true(np.allclose(peaks[0]['position'],
                    self.peak_positions0, rtol=1e-5, atol=1e-4))
                    
    def test_two_spectra(self):
        peaks = self.spectrum.find_peaks1D_ohaver()
        peaks = self.spectrum.find_peaks1D_ohaver()
        assert_true(np.allclose(peaks[1]['position'],
                    self.peak_positions1, rtol=1e-5, atol=1e-4))
                    
class TestInterpolateInBetween:
    def setUp(self):
        s = Spectrum(np.arange(40).reshape((2,20)))
        s.axes_manager.signal_axes[0].scale = 0.1
        s[:,8:12] = 0
        self.s = s
        
    def test_single_spectrum(self):
        s = self.s[0]
        s.interpolate_in_between(8,12)
        assert_true((s.data == np.arange(20)).all())
        
    def test_single_spectrum_in_units(self):
        s = self.s[0]
        s.interpolate_in_between(0.8,1.2)
        assert_true((s.data == np.arange(20)).all())
        
    def test_two_spectra(self):
        s = self.s
        s.interpolate_in_between(8,12)
        assert_true((s.data == np.arange(40).reshape(2,20)).all())
        

        
        

