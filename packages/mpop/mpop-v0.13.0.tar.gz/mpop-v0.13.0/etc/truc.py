#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""
import numpy as np
from mpop.satin.xmlformat import XMLFormat

def read_raw(filename):
    """Read *filename* without scaling it afterwards.
    """

    form = XMLFormat("eps_gomel1b_7.3.xml")

    grh_dtype = np.dtype([("record_class", "|i1"),
                          ("INSTRUMENT_GROUP", "|i1"),
                          ("RECORD_SUBCLASS", "|i1"),
                          ("RECORD_SUBCLASS_VERSION", "|i1"),
                          ("RECORD_SIZE", ">u4"),
                          ("RECORD_START_TIME", "S6"),
                          ("RECORD_STOP_TIME", "S6")])

    record_class = ["Reserved", "mphr", "sphr",
                    "ipr", "geadr", "giadr",
                    "veadr", "viadr", "mdr"]


    records = []

    with open(filename, "rb") as fdes:
        while True:
            grh = np.fromfile(fdes, grh_dtype, 1)
            if not grh:
                break
            try:
                rec_class = record_class[grh["record_class"]]
                sub_class = grh["RECORD_SUBCLASS"][0]
                record = np.fromfile(fdes,
                                     form.dtype((rec_class,
                                                 sub_class)),
                                     1)
                records.append((rec_class, record, sub_class))
                print "yeah", rec_class, sub_class
            except KeyError, e:
                print grh["record_class"], e
                fdes.seek(grh["RECORD_SIZE"] - 20, 1)

    return records, form

if __name__ == '__main__':
    recs, form2 = read_raw("GOME_HRP_00_M02_20120910124607Z_20120910124615Z_N_O_20120910124607Z")
