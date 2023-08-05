#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010, 2011, 2012, 2013.

# Author(s):
 
#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This file is part of mpop.

# mpop is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# mpop is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# mpop.  If not, see <http://www.gnu.org/licenses/>.

"""This modules describes the viirs instrument.
It provides VIIRS specific methods for RGB-compositing.
"""
import numpy as np

import mpop.imageo.geo_image as geo_image
from mpop.instruments.visir import VisirCompositer
from mpop.logger import LOG


# VIIRS
# Since there is overlap between I-bands and M-bands we need to 
# specifically re-define some of the RGB composites already defined
# in the standard visir.py module. So, the same names, like "overview"
# can be invoked and based on M-bands only.
# In addition we define new composite names for the I-bands,
# like e.g. hr_overview, hr_night_fog, etc
#
class ViirsCompositer(VisirCompositer):
    """This class sets up the VIIRS instrument channel list.
    """
    
    instrument_name = "viirs"


    def overview(self):
        """Make an Overview RGB image composite from VIIRS
        channels.
        """
        self.check_channels('M05', 'M07', 'M15')
    
        ch1 = self['M05'].check_range()
        ch2 = self['M07'].check_range()
        ch3 = -self['M15'].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")
        
        img.enhance(stretch="crude")
        img.enhance(gamma=1.6)
    
        return img

    overview.prerequisites = set(['M05', 'M07', 'M15'])

    def hr_overview(self):
        """Make a high resolution Overview RGB image composite 
        from the VIIRS I-bands only - 375 meter resolution.
        """
        self.check_channels('I01', 'I02', 'I05')

        ch1 = self['I01'].check_range()
        ch2 = self['I02'].check_range()
        ch3 = -self['I05'].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")

        img.enhance(stretch="crude")
        img.enhance(gamma=1.6)

        return img

    hr_overview.prerequisites = set(['I01', 'I02', 'I05'])


    def truecolor(self):
        """Make a True Color RGB image composite from
        M-bands only.
        """
        self.check_channels('M02', 'M04', 'M05')
    
        ch1 = self['M05'].check_range()
        ch2 = self['M04'].check_range()
        ch3 = self['M02'].check_range()

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=None,
                                 mode="RGB")

        img.enhance(stretch="linear")
        img.enhance(gamma=2.0)
    
        return img

    truecolor.prerequisites = set(['M02', 'M04', 'M05'])


    def natural(self):
        """Make a Natural Colors RGB image composite from
        M-bands only.
        """
        self.check_channels('M05', 'M07', 'M10')
    
        ch1 = self['M10'].check_range()
        ch2 = self['M07'].check_range()
        ch3 = self['M05'].check_range()
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB",
                                 crange=((0, 90),
                                         (0, 90),
                                         (0, 90)))

        img.enhance(gamma=1.8)
    
        return img

    natural.prerequisites = set(['M05', 'M07', 'M10'])

    def hr_natural(self):
        """Make a high resolution Day Natural Colors RGB image 
        composite from I-bands only - 375 meter resolution.
        """
        self.check_channels('I01', 'I02', 'I03')

        ch1 = self['I03'].check_range()
        ch2 = self['I02'].check_range()
        ch3 = self['I01'].check_range()

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB",
                                 crange=((0, 90),
                                         (0, 90),
                                         (0, 90)))

        img.enhance(gamma=1.8)

        return img

    hr_natural.prerequisites = set(['I01', 'I02', 'I03'])

    def vis06(self):
        """Make a black and white image of the VIS 0.635um channel.
        """
        return self.channel_image("M05")

    vis06.prerequisites = set(['M05'])

    def hr_vis06(self):
        """Make a high res black and white image of the 
        'visible' (VIS) I-band at 0.640um.
        """
        return self.channel_image('I01')

    hr_vis06.prerequisites = set(['I01'])


    def green_snow(self):
        """Make a Green Snow RGB image composite.
        """
        self.check_channels('M05', 'M10', 'M15')

        ch1 = self['M10'].check_range()
        ch2 = self['M05'].check_range()
        ch3 = -self['M15'].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")

        img.enhance(stretch = "crude")
        img.enhance(gamma = 1.6)
        
        return img

    green_snow.prerequisites = set(['M05', 'M10', 'M15'])

    def hr_green_snow(self):
        """Make a Green Snow RGB image composite.
        """
        self.check_channels('I01', 'I03', 'I05')

        ch1 = self['I03'].check_range()
        ch2 = self['I01'].check_range()
        ch3 = -self['I05'].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")

        img.enhance(stretch = "crude")
        img.enhance(gamma = 1.6)

        return img

    hr_green_snow.prerequisites = set(['I01', 'I03', 'I05'])

    def red_snow(self):
        """Make a Red Snow RGB image composite.
        """
        self.check_channels('M05', 'M10', 'M15')
    
        ch1 = self['M05'].check_range()
        ch2 = self['M10'].check_range()
        ch3 = -self['M15'].data
    
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")

        img.enhance(stretch = "crude")
        
        return img

    red_snow.prerequisites = set(['M05', 'M10', 'M15'])

    def hr_red_snow(self):
        """Make a high resolution Red Snow RGB image composite
        from the I-bands only.
        """
        self.check_channels('I01', 'I03', 'I05')

        ch1 = self['I01'].check_range()
        ch2 = self['I03'].check_range()
        ch3 = -self['I05'].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")

        img.enhance(stretch = "crude")

        return img

    hr_red_snow.prerequisites = set(['I01', 'I03', 'I05'])


    def night_color(self):
        self.check_channels('M12', 'M15', 'M16')

        ch1 = -self['M12'].data
        ch2 = -self['M15'].data
        ch3 = -self['M16'].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")
        img.stretch(stretch="histogram")

        return img

    night_color.prerequisites = set(['M12', 'M15', 'M16'])

    def night_fog(self):
        """Make a Night Fog RGB image composite.
        """
        self.check_channels('M12', 'M15', 'M16')
        
        ch1 = self['M16'].data - self['M15'].data
        ch2 = self['M15'].data - self['M12'].data
        ch3 = self['M15'].data
        
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB",
                                 crange=((-4, 2),
                                         (0, 6),
                                         (243, 293)))
        
        img.enhance(gamma=(1.0, 2.0, 1.0))
        
        return img

    night_fog.prerequisites = set(['M12', 'M15', 'M16'])

    def dust(self):
        """Make a Dust RGB image composite.
        """
        self.check_channels('M14', 'M15', 'M16')

        ch1 = self['M16'].data - self['M15'].data
        ch2 = self['M15'].data - self['M14'].data
        ch3 = self['M15'].data
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB",
                                 crange=((-4, 2),
                                         (0, 15),
                                         (261, 289)))

        img.enhance(gamma=(1.0, 2.5, 1.0))
        
        return img

    dust.prerequisites = set(['M14', 'M15', 'M16'])


    def ash(self):
        """Make a Ash RGB image composite.
        """
        self.check_channels('M14', 'M15', 'M16')

        ch1 = self['M16'].data - self['M15'].data
        ch2 = self['M15'].data - self['M14'].data
        ch3 = self['M15'].data
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB",
                                 crange=((-4, 2),
                                         (-4, 5),
                                         (243, 303)))

        return img

    ash.prerequisites = set(['M14', 'M15', 'M16'])


    def fog(self):
        """Make a Fog RGB image composite.
        """
        self.check_channels('M14', 'M15', 'M16')

        ch1 = self['M16'].data - self['M15'].data
        ch2 = self['M15'].data - self['M14'].data
        ch3 = self['M15'].data
        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB",
                                 crange=((-4, 2),
                                         (0, 6),
                                         (243, 283)))

        img.enhance(gamma=(1.0, 2.0, 1.0))
        
        return img

    fog.prerequisites = set(['M14', 'M15', 'M16'])


    def cloudtop(self):
        """Make a Cloudtop RGB image composite.
        """
        self.check_channels('M12', 'M15', 'M16')

        ch1 = -self['M12'].data
        ch2 = -self['M15'].data
        ch3 = -self['M16'].data

        img = geo_image.GeoImage((ch1, ch2, ch3),
                                 self.area,
                                 self.time_slot,
                                 fill_value=(0, 0, 0),
                                 mode="RGB")

        img.enhance(stretch=(0.005, 0.005))

        return img

    cloudtop.prerequisites = set(['M12', 'M15', 'M16'])


    def dnb(self, stretch="histogram"):
        """Make a black and white image of the Day-Night band."""
        self.check_channels('DNB')
    
        img =  geo_image.GeoImage(self['DNB'].data,
                                  self.area,
                                  self.time_slot,
                                  fill_value=0,
                                  mode="L")
        if stretch:
            img.enhance(stretch=stretch)
        return img
    
    dnb.prerequisites = set(['DNB'])

    def dnb_rgb(self, stretch="linear"):
        """Make a RGB Day-Night band using M15 as blue."""
        self.check_channels('DNB', 'M15')
        ch1 = self['DNB'].data
        ch2 = self['DNB'].data
        ch3 = -self['M15'].data
   
        img =  geo_image.GeoImage((ch1, ch2, ch3),
                                  self.area,
                                  self.time_slot,
                                  fill_value=(0, 0, 0),
                                  mode="RGB")
        if stretch:
            img.enhance(stretch=stretch)
        return img
    
    dnb_rgb.prerequisites = set(['DNB', 'M15'])

    def ir108(self):
        """Make a black and white image of the IR 10.8um channel.
        """
        self.check_channels("M15")

        img = geo_image.GeoImage(self["M15"].data,
                                 self.area,
                                 self.time_slot,
                                 fill_value=0,
                                 mode="L",
                                 crange=(-70 + 273.15, 57.5 + 273.15))
        img.enhance(inverse=True)
        return img

    ir108.prerequisites = set(["M15"])

    def hr_ir108(self):
        """Make a black and white image of the IR 10.8um channel (320m).
        """
        self.check_channels("I05")

        img = geo_image.GeoImage(self["I05"].data,
                                 self.area,
                                 self.time_slot,
                                 fill_value=0,
                                 mode="L",
                                 crange=(-70 + 273.15, 57.5 + 273.15))
        img.enhance(inverse=True)
        return img

    hr_ir108.prerequisites = set(["I05"])
