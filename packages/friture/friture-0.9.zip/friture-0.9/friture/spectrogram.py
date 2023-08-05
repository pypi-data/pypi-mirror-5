#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui
from numpy import log10, floor, zeros, float64, tile
from friture.imageplot import ImagePlot
from friture.audioproc import audioproc # audio processing class
from friture.spectrogram_settings import Spectrogram_Settings_Dialog# settings dialog
from friture.audiobackend import SAMPLING_RATE
from friture.logger import PrintLogger
#from glrollingcanvaswidget import GLRollingCanvasWidget
from fractions import Fraction

# shared with spectrogram_settings.py
DEFAULT_FFT_SIZE = 7 #4096 points
DEFAULT_FREQ_SCALE = 1 #log10
DEFAULT_MAXFREQ = SAMPLING_RATE/2
DEFAULT_MINFREQ = 20
DEFAULT_SPEC_MIN = -140
DEFAULT_SPEC_MAX = 0
DEFAULT_TIMERANGE = 10.
DEFAULT_WEIGHTING = 1 #A

class Spectrogram_Widget(QtGui.QWidget):
    def __init__(self, parent, audiobackend, logger = PrintLogger()):
        QtGui.QWidget.__init__(self, parent)

        self.logger = logger

        self.setObjectName("Spectrogram_Widget")
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneImage = ImagePlot(self, self.logger, audiobackend)
        #self.PlotZoneImage = GLRollingCanvasWidget(self, self.logger)
        self.PlotZoneImage.setObjectName("PlotZoneImage")
        self.gridLayout.addWidget(self.PlotZoneImage, 0, 1, 1, 1)

        self.audiobuffer = None
        self.audiobackend = audiobackend
        
        # initialize the class instance that will do the fft
        self.proc = audioproc(self.logger)

        self.maxfreq = DEFAULT_MAXFREQ
        self.proc.set_maxfreq(self.maxfreq)
        self.minfreq = DEFAULT_MINFREQ
        self.fft_size = 2**DEFAULT_FFT_SIZE*32
        self.proc.set_fftsize(self.fft_size)
        self.spec_min = DEFAULT_SPEC_MIN
        self.spec_max = DEFAULT_SPEC_MAX
        self.weighting = DEFAULT_WEIGHTING
        
        self.update_weighting()
        self.freq = self.proc.get_freq_scale()
              
        self.timerange_s = DEFAULT_TIMERANGE
        self.canvas_width = 100.
        
        self.old_index = 0        
        self.overlap = 3./4.
        self.overlap_frac = Fraction(3, 4)
        self.dT_s = self.fft_size*(1. - self.overlap)/float(SAMPLING_RATE)
        
        self.PlotZoneImage.setlog10freqscale() #DEFAULT_FREQ_SCALE = 1 #log10
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)
        self.PlotZoneImage.setweighting(self.weighting)
        self.PlotZoneImage.settimerange(self.timerange_s, self.dT_s)

        sfft_rate_frac = Fraction(SAMPLING_RATE, self.fft_size)/(Fraction(1) - self.overlap_frac)/1000
        self.PlotZoneImage.set_sfft_rate(sfft_rate_frac)
        
        # initialize the settings dialog
        self.settings_dialog = Spectrogram_Settings_Dialog(self, self.logger)

    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer
        self.old_index = self.audiobuffer.ringbuffer.offset

    def log_spectrogram(self, sp):
        # Note: implementing the log10 of the array in Cython did not bring
        # any speedup.
        # Idea: Instead of computing the log of the data, I could pre-compute
        # a list of values associated with the colormap, and then do a search...
        epsilon = 1e-30
        return 10.*log10(sp + epsilon)

    # scale the db spectrum from [- spec_range db ... 0 db] > [0..1]    
    def scale_spectrogram(self, sp):
        return (sp.clip(min = self.spec_min, max = self.spec_max) - self.spec_min)/(self.spec_max - self.spec_min)

    # method
    def update(self):
        if not self.isVisible():
            return        
        
        # we need to maintain an index of where we are in the buffer
        index = self.audiobuffer.ringbuffer.offset

        available = index - self.old_index

        if available < 0:
            #ringbuffer must have grown or something...
            available = 0
            self.old_index = index
    
        # if we have enough data to add a frequency column in the time-frequency plane, compute it
        needed = self.fft_size*(1. - self.overlap)        
        realizable = int(floor(available/needed))

        if realizable > 0:
            spn = zeros((len(self.freq), realizable), dtype=float64)
        
            for i in range(realizable):
                floatdata = self.audiobuffer.data_indexed(self.old_index, self.fft_size)
    
                # for now, take the first channel only
                floatdata = floatdata[0,:]
    
                # FIXME We should allow here for more intelligent transforms, especially when the log freq scale is selected
                spn[:, i] = self.proc.analyzelive(floatdata)
    
                self.old_index += int(needed)
                    
            w = tile(self.w, (1, realizable))
            norm_spectrogram = self.scale_spectrogram(self.log_spectrogram(spn) + w)            
            self.PlotZoneImage.addData(self.freq, norm_spectrogram)
        self.PlotZoneImage.updatePlot()
            
        # thickness of a frequency column depends on FFT size and window overlap
        # hamming window with 75% overlap provides good quality (Perfect reconstruction,
        # aliasing from side lobes only, 42 dB channel isolation)
        
        # number of frequency columns that we keep depends on the time history that the user has chosen
        
        # actual displayed spectrogram is a scaled version of the time-frequency plane
        
    def setminfreq(self, freq):
        self.minfreq = freq
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)

    def setmaxfreq(self, freq):
        self.maxfreq = freq
        self.PlotZoneImage.setfreqrange(self.minfreq, self.maxfreq)
        self.proc.set_maxfreq(freq)
        self.update_weighting()
        self.freq = self.proc.get_freq_scale()
    
    def setfftsize(self, fft_size):
        self.fft_size = fft_size
        
        self.proc.set_fftsize(fft_size)
        self.update_weighting()
        self.freq = self.proc.get_freq_scale()
                    
        self.dT_s = self.fft_size*(1. - self.overlap)/float(SAMPLING_RATE)
        self.PlotZoneImage.settimerange(self.timerange_s, self.dT_s)

        sfft_rate_frac = Fraction(SAMPLING_RATE, self.fft_size)/(Fraction(1) - self.overlap_frac)/1000
        self.PlotZoneImage.set_sfft_rate(sfft_rate_frac)

    def setmin(self, value):
        self.spec_min = value
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)
    
    def setmax(self, value):
        self.spec_max = value
        self.PlotZoneImage.setspecrange(self.spec_min, self.spec_max)
    
    def setweighting(self, weighting):
        self.weighting = weighting
        self.PlotZoneImage.setweighting(weighting)
        self.update_weighting()
    
    def update_weighting(self):    
        A, B, C = self.proc.get_freq_weighting()
        if self.weighting is 0:
            self.w = 0.
        elif self.weighting is 1:
            self.w = A
        elif self.weighting is 2:
            self.w = B
        else:
            self.w = C
        self.w.shape = (len(self.w), 1)

    def settings_called(self, checked):
        self.settings_dialog.show()
    
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)

    # slot
    def timerangechanged(self, value):
        self.timerange_s = value
        self.PlotZoneImage.settimerange(self.timerange_s, self.dT_s)

    # slot
    def canvasWidthChanged(self, width):
        self.canvas_width = width
