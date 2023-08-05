# -*- coding: utf-8 -*-
#
# util.py
#
# Copyright (C) 2012, 2013 Steve Canny scanny@cisco.com
#
# This module is part of python-pptx and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Utility functions and classes that come in handy when working with PowerPoint
and Open XML.
"""

import os
import platform
import re


class _BaseLength(int):
    """Base class for length classes Inches, Cm, Mm, Px, and Emu."""
    _EMUS_PER_INCH = 914400
    _EMUS_PER_CM = 360000
    _EMUS_PER_MM = 36000
    _EMUS_PER_PX = 9525 if platform.system() == 'Windows' else 12700

    def __new__(cls, emu):
        return int.__new__(cls, emu)

    @property
    def inches(self):
        return self / float(self._EMUS_PER_INCH)

    @property
    def cm(self):
        return self / float(self._EMUS_PER_CM)

    @property
    def mm(self):
        return self / float(self._EMUS_PER_MM)

    @property
    def px(self):
        # round can somtimes return values like x.999999 which are truncated
        # to x by int(); adding the 0.1 prevents this
        return int(round(self / float(self._EMUS_PER_PX)) + 0.1)

    @property
    def emu(self):
        return self


class Inches(_BaseLength):
    """Convenience constructor for length in inches."""
    def __new__(cls, inches):
        emu = int(inches * _BaseLength._EMUS_PER_INCH)
        return _BaseLength.__new__(cls, emu)


class Cm(_BaseLength):
    """Convenience constructor for length in centimeters."""
    def __new__(cls, cm):
        emu = int(cm * _BaseLength._EMUS_PER_CM)
        return _BaseLength.__new__(cls, emu)


class Emu(_BaseLength):
    """Convenience constructor for length in english metric units."""
    def __new__(cls, emu):
        return _BaseLength.__new__(cls, int(emu))


class Mm(_BaseLength):
    """Convenience constructor for length in millimeters."""
    def __new__(cls, mm):
        emu = int(mm * _BaseLength._EMUS_PER_MM)
        return _BaseLength.__new__(cls, emu)


class Pt(int):
    """Convenience class for setting font sizes in points"""
    _UNITS_PER_POINT = 100

    def __new__(cls, pts):
        units = int(pts * Pt._UNITS_PER_POINT)
        return int.__new__(cls, units)


class Px(_BaseLength):
    """Convenience constructor for length in pixels."""
    def __new__(cls, px):
        emu = int(px * _BaseLength._EMUS_PER_PX)
        return _BaseLength.__new__(cls, emu)


class Collection(object):
    """
    Base class for collection classes. May also be used for part collections
    that don't yet have any custom methods.

    Has the following characteristics.:

    * Container (implements __contains__)
    * Iterable (delegates __iter__ to |list|)
    * Sized (implements __len__)
    * Sequence (delegates __getitem__ to |list|)
    """
    def __init__(self):
        super(Collection, self).__init__()
        self.__values = []

    @property
    def _values(self):
        """Return read-only reference to collection values (list)."""
        return self.__values

    def __contains__(self, item):  # __iter__ would do this job by itself
        """Supports 'in' operator (e.g. 'x in collection')."""
        return (item in self.__values)

    def __getitem__(self, key):
        """Provides indexed access, (e.g. 'collection[0]')."""
        return self.__values.__getitem__(key)

    def __iter__(self):
        """Supports iteration (e.g. 'for x in collection: pass')."""
        return self.__values.__iter__()

    def __len__(self):
        """Supports len() function (e.g. 'len(collection) == 1')."""
        return len(self.__values)

    def index(self, item):
        """Supports index method (e.g. '[1, 2, 3].index(2) == 1')."""
        return self.__values.index(item)


class Partname(object):
    """
    Provides access to partname components such as the baseURI and the part
    index.
    """
    __filename_re = re.compile('([a-zA-Z]+)([1-9][0-9]*)?')

    def __init__(self, partname):
        super(Partname, self).__init__()
        self.__partname = partname

    @property
    def baseURI(self):
        """
        The base URI of partname, e.g. ``'/ppt/slides'`` for
        ``'/ppt/slides/slide1.xml'``.
        """
        return os.path.split(self.__partname)[0]

    @property
    def filename(self):
        """
        The "filename" portion of partname, e.g. ``'slide1.xml'`` for
        ``'/ppt/slides/slide1.xml'``.
        """
        return os.path.split(self.__partname)[1]

    @property
    def ext(self):
        """
        The extension portion of partname, e.g. ``'.xml'`` for
        ``'/ppt/slides/slide1.xml'``. Note that period is included, consistent
        with behavior of :meth:`os.path.ext`.
        """
        return os.path.splitext(self.__partname)[1]

    @property
    def partname(self):
        """
        The complete partname, e.g. ``'/ppt/slides/slide1.xml'`` for
        ``'/ppt/slides/slide1.xml'``.
        """
        return self.__partname

    @property
    def basename(self):
        """
        The base "filename" of the partname, e.g. ``'slide'`` for
        ``'/ppt/slides/slide1.xml'``.
        """
        name = os.path.splitext(self.filename)[0]  # filename with ext removed
        match = self.__filename_re.match(name)
        return match.group(1)

    @property
    def idx(self):
        """
        Return partname index as integer for tuple partname or None for
        singleton partname, e.g. ``21`` for ``'/ppt/slides/slide21.xml'`` and
        |None| for ``'/ppt/presentation.xml'``.
        """
        name = os.path.splitext(self.filename)[0]  # filename with ext removed
        match = self.__filename_re.match(name)
        return int(match.group(2)) if match.group(2) else None
