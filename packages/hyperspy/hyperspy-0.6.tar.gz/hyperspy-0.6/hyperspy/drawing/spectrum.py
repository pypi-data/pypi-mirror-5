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
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from hyperspy import messages

import utils

class SpectrumFigure():
    """
    """
    def __init__(self):
        self.figure = None
        self.ax = None
        self.right_ax = None
        self.ax_lines = list()
        self.right_ax_lines = list()
        self.autoscale = True
        self.blit = False
        self.lines = list()
        self.axes_manager = None
        self.right_axes_manager = None
        
        # Labels
        self.xlabel = ''
        self.ylabel = ''
        self.title = ''
        self.create_figure()
        self.create_axis()

    def create_figure(self):
        self.figure = utils.create_figure()
        utils.on_figure_window_close(self.figure, self.close)
        self.figure.canvas.mpl_connect('draw_event', self._on_draw)

    def create_axis(self):
        self.ax = self.figure.add_subplot(111)
        self.ax.yaxis.set_animated(True)
        self.ax.hspy_fig = self
        
    def create_right_axis(self):
        if self.ax is None:
            self.create_axis()
        if self.right_ax is None:
            self.right_ax = self.ax.twinx()
            self.right_ax.hspy_fig = self
            #~self.right_ax.set_animated(True)
        
    def add_line(self, line, ax = 'left'):
        if ax == 'left':
            line.ax = self.ax
            if line.axes_manager is None:
                line.axes_manager = self.axes_manager
            self.ax_lines.append(line)
        elif ax == 'right':
            line.ax = self.right_ax
            self.right_ax_lines.append(line)
            if line.axes_manager is None:
                line.axes_manager = self.right_axes_manager
        line.axis = self.axis
        line.autoscale = self.autoscale
        line.blit = self.blit
        
    def plot(self):
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.title)
        x_axis_upper_lims=[]
        x_axis_lower_lims=[]
        for line in self.ax_lines:
            line.plot()
            x_axis_lower_lims.append(line.axis[0])
            x_axis_upper_lims.append(line.axis[-1])
        plt.xlim(np.min(x_axis_lower_lims),np.max(x_axis_upper_lims))
            
        
    def close(self):
        for line in self.ax_lines + self.right_ax_lines:
            line.close()
        if utils.does_figure_object_exists(self.figure):
            plt.close(self.figure)
            
    def _on_draw(self, *args):
        canvas = self.figure.canvas
        self._background = canvas.copy_from_bbox(self.figure.bbox)
        self._draw_animated()
        
    def _draw_animated(self):
        canvas = self.ax.figure.canvas
        canvas.restore_region(self._background)
        for ax in [ax for ax in [self.ax, self.right_ax]
                if ax is not None]:
            artists = []
            artists.extend(ax.collections)
            artists.extend(ax.patches)
            artists.extend(ax.lines)
            artists.extend(ax.texts)
            artists.extend(ax.artists)
            artists.append(ax.get_yaxis())
            [ax.draw_artist(a) for a in artists if 
             a.get_animated() is True]
        canvas.blit()
        
class SpectrumLine():
    def __init__(self):
        """
        """
        # Data attributes
        self.data_function = None
        self.axis = None
        self.axes_manager = None
        self.auto_update = True
        self.get_complex = False
        
        # Properties
        self.line = None
        self.line_properties = dict()
        self.autoscale = True
        self.plot_indices = False
        self.text = None
        self.text_position = (-0.1, 1.05,)

    def line_properties_helper(self, color, type):
        """This function provides an easy way of defining some basic line 
        properties.
        
        Further customization is possible by adding keys to the line_properties 
        attribute
        
        Parameters
        ----------
        
        color : any valid matplotlib color definition, e.g. 'red'
        type : it can be one of 'scatter', 'step', 'line'
        """
        lp = self.line_properties
        if type == 'scatter':
            lp['marker'] = 'o'
            lp['linestyle'] = 'None'
            lp['markersize'] = 1
            lp['markeredgecolor'] = color
        elif type == 'line':
            lp['color'] = color
            lp['linestyle'] = '-'
            lp['marker'] = None
        elif type == 'step':
            lp['color'] = color
            lp['drawstyle'] = 'steps-mid'
    def set_properties(self):
        for key in self.line_properties:
            plt.setp(self.line, **self.line_properties)
        self.ax.figure.canvas.draw()
        
    def plot(self, data=1):
        f = self.data_function
        if self.get_complex is False:
            data = f(axes_manager=self.axes_manager).real
        else:
            data = f(axes_manager=self.axes_manager).imag
        self.line, = self.ax.plot(self.axis, data, 
                                  **self.line_properties)
        self.line.set_animated(True)
        self.axes_manager.connect(self.update)
        if not self.axes_manager or self.axes_manager.navigation_size==0:
            self.plot_indices = False
        if self.plot_indices is True:
            self.text = self.ax.text(*self.text_position,
                            s=str(self.axes_manager.indices),
                            transform = self.ax.transAxes,
                            fontsize=12,
                            color=self.line.get_color(),
                            animated=True)
        self.ax.figure.canvas.draw()
                  
    def update(self, force_replot=False):
        """Update the current spectrum figure"""
        if self.auto_update is False:
            return           
        if force_replot is True:
            self.close()
            self.plot()
        if self.get_complex is False:
            ydata = self.data_function(axes_manager=self.axes_manager).real
        else:
            ydata = self.data_function(axes_manager=self.axes_manager).imag
        self.line.set_ydata(ydata)
        
        if self.autoscale is True:
            self.ax.relim()
            y1, y2 = np.searchsorted(self.axis, 
                                     self.ax.get_xbound())
            y2 += 2
            y1, y2 = np.clip((y1,y2),0,len(ydata-1))
            clipped_ydata = ydata[y1:y2]
            y_max, y_min = (np.nanmax(clipped_ydata),
                            np.nanmin(clipped_ydata))
            self.ax.set_ylim(y_min, y_max)
        if self.plot_indices is True:
            self.text.set_text((self.axes_manager.indices))
        self.ax.hspy_fig._draw_animated()
        #self.ax.figure.canvas.draw_idle()
        
    def close(self):
        if self.line in self.ax.lines:
            self.ax.lines.remove(self.line)
        if self.text and self.text in self.ax.texts:
            self.ax.texts.remove(self.text)
        self.axes_manager.disconnect(self.update)
        try:
            self.ax.figure.canvas.draw()
        except:
            pass

def _plot_component(factors, idx, ax=None, cal_axis=None, 
                    comp_label='PC'):
    if ax==None:
        ax=plt.gca()
    if cal_axis <> None:
        x=cal_axis.axis
        plt.xlabel(cal_axis.units)
    else:
        x=np.arange(factors.shape[0])
        plt.xlabel('Channel index')
    ax.plot(x,factors[:,idx],label='%s %i'%(comp_label,idx))
    return ax

def _plot_loading(loadings, idx, axes_manager, ax=None, 
                comp_label='PC',no_nans=True, calibrate=True,
                cmap=plt.cm.gray):
    if ax==None:
        ax=plt.gca()
    if no_nans:
        loadings=np.nan_to_num(loadings)
    if axes_manager.navigation_dimension==2:
        extent=None
        # get calibration from a passed axes_manager
        shape=axes_manager._navigation_shape_in_array
        if calibrate:
            extent=(axes_manager._axes[0].low_value,
                    axes_manager._axes[0].high_value,
                    axes_manager._axes[1].high_value,
                    axes_manager._axes[1].low_value)
        im=ax.imshow(loadings[idx].reshape(shape),cmap=cmap,extent=extent, 
                     interpolation = 'nearest')
        div=make_axes_locatable(ax)
        cax=div.append_axes("right",size="5%",pad=0.05)
        plt.colorbar(im,cax=cax)
    elif axes_manager.navigation_dimension ==1:
        if calibrate:
            x=axes_manager._axes[0].axis
        else:
            x=np.arange(axes_manager._axes[0].size)
        ax.step(x,loadings[idx])
    else:
        messages.warning_exit('View not supported')
            
        
