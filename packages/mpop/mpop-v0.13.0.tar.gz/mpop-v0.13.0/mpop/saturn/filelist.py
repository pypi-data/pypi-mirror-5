#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010.

# SMHI,
# Folkborgsvägen 1,
# Norrköping, 
# Sweden

# Author(s):
 
#   Martin Raspaud <martin.raspaud@smhi.se>

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

"""Filelist class.
"""
import os
import shutil
import tempfile

from mpop.utils import ensure_dir
from mpop.saturn import LOG

class FileList(list):
    """List of files.
    """
    def __init__(self, *args):
        list.__init__(self, *args)

    def put_date(self, date):
        """Return an new filelist with the given *date*.
        """
        return FileList([date.strftime(i) for i in self])

    def put_metadata(self, metadata):
        """Fill in the filelist with the given *metadata*.
        """
        return FileList([i % metadata for i in self])

    def _get_by_ext(self):
        """Convert the filelist into a dict with extensions as keys.
        """
        types = {}
        for filename in self:
            file_tuple = os.path.splitext(filename)
            ext = file_tuple[1][:4]
            types[ext] = types.get(ext, FileList()) + FileList([filename])
        return types

    def save_object(self, obj):
        """save *obj* to the filelist.
        """
        files_by_ext = self._get_by_ext()
        for extkey in files_by_ext:
            path, trash = os.path.split(files_by_ext[extkey][0])
            del trash
            try:
                ensure_dir(files_by_ext[extkey][0])
                handle, tmpfilename = tempfile.mkstemp(extkey,
                                                       "mpop_tmp",
                                                       path)
                os.fsync(handle)
                obj.save(tmpfilename)
                os.fsync(handle)
                os.chmod(tmpfilename, 0644)
                os.fsync(handle)
            except Exception:
                LOG.exception("Something went wrong in saving file... "
                              "Dumping trace.")
                LOG.warning("Job skipped, going on with the next.")
                continue
            for filename in files_by_ext[extkey][1:]:
                path2, trash = os.path.split(filename)
                del trash

                ensure_dir(filename)
                handle2, tmpfilename2 = tempfile.mkstemp(extkey,
                                                         "mpop_tmp",
                                                         path2)
                os.fsync(handle2)
                try:
                    shutil.copy(tmpfilename, tmpfilename2)
                    os.fsync(handle2)
                    os.close(handle2)
                except (IOError, OSError):
                    LOG.exception("Copying file %s to %s failed"
                                  %(tmpfilename,tmpfilename2))
                    LOG.info("Retrying...")
                    try:
                        shutil.copy(tmpfilename, tmpfilename2)
                        os.fsync(handle2)
                        os.close(handle2)
                        LOG.info("Went OK this time...")
                    except (IOError, OSError):
                        LOG.exception("No way...")
                try:
                    os.rename(tmpfilename2, filename)
                except (IOError, OSError):
                    LOG.exception("Renaming file %s to %s failed"
                                %(tmpfilename2,filename))
                    LOG.info("Retrying...")
                    try:
                        os.rename(tmpfilename2, filename)
                    except (IOError, OSError):
                        LOG.exception("No way...")
                LOG.debug("Done saving "+filename)
                
            os.rename(tmpfilename, files_by_ext[extkey][0])
            os.fsync(handle)
            os.close(handle)
            LOG.debug("Done saving "+files_by_ext[extkey][0])
