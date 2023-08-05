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


import os

import numpy as np
from nose.tools import (
    assert_true,
    assert_equal,
    assert_not_equal,
    raises)

from hyperspy.signal import Signal

class Test1D:
    def setUp(self):
        self.signal = Signal(np.arange(10))
        self.data = self.signal.data.copy()
        
    def test_slice_None(self):
        s = self.signal[:]
        d = self.data
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 
                     self.signal.axes_manager._axes[0].offset)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale)
        
        
    def test_std_slice(self):
        s = self.signal[1:-1]
        d = self.data[1:-1]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 1)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale)

    def test_reverse_slice(self):
        s = self.signal[-1:1:-1]
        d = self.data[-1:1:-1]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 9)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale * -1)
                     
    def test_step2_slice(self):
        s = self.signal[1:-1:2]
        d = self.data[1:-1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 1)
        assert_equal(np.sign(s.axes_manager._axes[0].scale),
                     np.sign(self.signal.axes_manager._axes[0].scale))
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale*2.)
    
    @raises(ValueError)    
    def test_step0_slice(self):
        s = self.signal[::0]        

    def test_index(self):
        s = self.signal[3]
        assert_equal(s.data, 3)
        assert_equal(len(s.axes_manager._axes), 1)
        assert_equal(s.data.shape, (1,))
        
    def test_float_index(self):
        s = self.signal[3.4]
        assert_equal(s.data, 3)
        assert_equal(len(s.axes_manager._axes), 1)
        assert_equal(s.data.shape, (1,))
        
    def test_signal_indexer_slice(self):
        s = self.signal.signal_indexer[1:-1]
        d = self.data[1:-1]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 1)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale)

    def test_signal_indexer_reverse_slice(self):
        s = self.signal.signal_indexer[-1:1:-1]
        d = self.data[-1:1:-1]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 9)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale * -1)
                     
    def test_signal_indexer_step2_slice(self):
        s = self.signal.signal_indexer[1:-1:2]
        d = self.data[1:-1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 1)
        assert_equal(np.sign(s.axes_manager._axes[0].scale),
                     np.sign(self.signal.axes_manager._axes[0].scale))
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale*2.)

    def test_signal_indexer_index(self):
        s = self.signal.signal_indexer[3]
        assert_equal(s.data, 3)
     
    @raises(IndexError)    
    def test_navigation_indexer_navdim0(self):
        s = self.signal.navigation_indexer[3]
        
    def test_minus_one_index(self):
        s = self.signal[-1]
        assert_equal(s.data, self.data[-1])
        
        
class Test3D_SignalDim0:
    def setUp(self):
        self.signal = Signal(np.arange(24).reshape((2,3,4)))
        self.data = self.signal.data.copy()
        self.signal.axes_manager._axes[2].navigate = True
        
    def test_signal_dim0(self):
        s = self.signal
        assert((s[:].data == s.data).all())
        
    def test_signal_indexer_signal_dim0(self):
        s = self.signal
        assert((s.signal_indexer[:].data == s.data).all())
    
    @raises(IndexError)  
    def test_signal_indexer_signal_dim0(self):
        s = self.signal
        assert((s.signal_indexer[:,:].data == s.data).all())

    @raises(IndexError)  
    def test_signal_indexer_signal_dim0(self):
        s = self.signal
        s.signal_indexer[0]
    
    def test_navigation_indexer_signal_dim0(self):
        s = self.signal
        assert((s.navigation_indexer[:].data == s.data).all())
        
class Test3D_Navigate_0_and_1:
    def setUp(self):
        self.signal = Signal(np.arange(24).reshape((2,3,4)))
        self.data = self.signal.data.copy()
        self.signal.axes_manager._axes[0].navigate = True
        self.signal.axes_manager._axes[1].navigate = True
        self.signal.axes_manager._axes[2].navigate = False
    
    def test_1px_slice(self):
        s = self.signal[1:2]
        d = self.data[:,1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[1].offset, 1)
        assert_equal(s.axes_manager._axes[1].size, 1)
        assert_equal(s.axes_manager._axes[1].scale,
                     self.signal.axes_manager._axes[1].scale)
                     
    def test_1px_navigation_indexer_slice(self):
        s = self.signal.navigation_indexer[1:2]
        d = self.data[:,1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[1].offset, 1)
        assert_equal(s.axes_manager._axes[1].size, 1)
        assert_equal(s.axes_manager._axes[1].scale,
                     self.signal.axes_manager._axes[1].scale)
                     
    def test_1px_signal_indexer_slice(self):
        s = self.signal.signal_indexer[1:2]
        d = self.data[:,:,1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager.signal_axes[0].offset, 1)
        assert_equal(s.axes_manager.signal_axes[0].size, 1)
        assert_equal(s.axes_manager.signal_axes[0].scale,
                     self.signal.axes_manager.signal_axes[0].scale)
                     
    def test_dimension_when_indexing(self):
        s = self.signal[0]
        assert_equal(s.data.shape, self.data[:,0,:].shape)
        
    def test_dimension_when_slicing(self):
        s = self.signal[0:1]
        assert_equal(s.data.shape, self.data[:,0:1,:].shape)
                     
class Test3D_Navigate_1:
    def setUp(self):
        self.signal = Signal(np.arange(24).reshape((2,3,4)))
        self.data = self.signal.data.copy()
        self.signal.axes_manager._axes[0].navigate = False
        self.signal.axes_manager._axes[1].navigate = True
        self.signal.axes_manager._axes[2].navigate = False
    
    def test_1px_slice(self):
        s = self.signal[1:2]
        d = self.data[:,1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[1].offset, 1)
        assert_equal(s.axes_manager._axes[1].size, 1)
        assert_equal(s.axes_manager._axes[1].scale,
                     self.signal.axes_manager._axes[1].scale)
                     
    def test_1px_navigation_indexer_slice(self):
        s = self.signal.navigation_indexer[1:2]
        d = self.data[:,1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[1].offset, 1)
        assert_equal(s.axes_manager._axes[1].size, 1)
        assert_equal(s.axes_manager._axes[1].scale,
                     self.signal.axes_manager._axes[1].scale)
                     
    def test_1px_signal_indexer_slice(self):
        s = self.signal.signal_indexer[1:2]
        d = self.data[:,:,1:2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager.signal_axes[0].offset, 1)
        assert_equal(s.axes_manager.signal_axes[0].size, 1)
        assert_equal(s.axes_manager.signal_axes[0].scale,
                     self.signal.axes_manager.signal_axes[0].scale)
                     
class TestFloatArguments:
    def setUp(self):
        self.signal = Signal(np.arange(10))
        self.signal.axes_manager[0].scale = 0.5
        self.signal.axes_manager[0].offset = 0.25
        self.data = self.signal.data.copy()
        
    def test_float_start(self):
        s = self.signal[0.75:-1]
        d = self.data[1:-1]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 0.75)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale)

    def test_float_end(self):
        s = self.signal[1:4.75]
        d = self.data[1:-1]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 0.75)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale)
                     
    def test_float_both(self):
        s = self.signal[0.75:4.75]
        d = self.data[1:-1]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 0.75)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale)
                     
    def test_float_step(self):
        s = self.signal[::1.1]
        d = self.data[::2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 0.25)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale * 2)
                     
    def test_negative_float_step(self):
        s = self.signal[::-1.1]
        d = self.data[::-2]
        assert_true((s.data==d).all())
        assert_equal(s.axes_manager._axes[0].offset, 4.75)
        assert_equal(s.axes_manager._axes[0].scale,
                     self.signal.axes_manager._axes[0].scale * -2)
                     
class TestEllipsis:
    def setUp(self):
        self.signal = Signal(np.arange(2**4).reshape(
            (2,2,2,2)))
        self.data = self.signal.data.copy()
        
    def test_ellipsis_beginning(self):
        s = self.signal[...,0,0]
        assert_true((s.data == self.data[0, ...,0]).all())
        
    def test_in_between(self):
        s = self.signal[0,...,0]
        assert_true((s.data == self.data[...,0,0]).all())
        
    def test_ellipsis_navigation(self):
        s = self.signal.navigation_indexer[...,0]
        assert_true((s.data == self.data[0, ...]).all())
        
    def test_ellipsis_navigation(self):
        self.signal.axes_manager._axes[-2].navigate = False
        self.signal.axes_manager._axes[-3].navigate = False
        s = self.signal.signal_indexer[...,0]
        assert_true((s.data == self.data[:,0, ...]).all())
                     
            
