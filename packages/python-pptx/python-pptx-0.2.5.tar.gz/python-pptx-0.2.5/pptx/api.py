# -*- coding: utf-8 -*-
#
# api.py
#
# Copyright (C) 2012, 2013 Steve Canny scanny@cisco.com
#
# This module is part of python-pptx and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""
Directly exposed API classes, Presentation for now. Provides some syntactic
sugar for interacting with the pptx.presentation._Package graph and also
provides some insulation so not so many classes in the other modules need to
be named as internal (leading underscore).
"""

from pptx.presentation import _Package


class Presentation(object):
    """
    Return a |Presentation| instance loaded from *file*, where *file* can be
    either a path to a ``.pptx`` file (a string) or a file-like object. If
    *file* is missing or ``None``, load the built-in default presentation
    template.
    """
    def __init__(self, file=None):
        super(Presentation, self).__init__()
        self.__package = _Package(file)
        self.__presentation = self.__package.presentation

    @property
    def slidelayouts(self):
        """
        Tuple containing the |_SlideLayout| instances belonging to the
        first |_SlideMaster| of this presentation.
        """
        return tuple(self.__presentation.slidemasters[0].slidelayouts)

    @property
    def slidemaster(self):
        """
        First |_SlideMaster| object belonging to this presentation.
        """
        return self.__presentation.slidemasters[0]

    @property
    def slidemasters(self):
        """
        List of |_SlideMaster| objects belonging to this presentation.
        """
        return self.__presentation.slidemasters

    @property
    def slides(self):
        """
        |_SlideCollection| object containing the slides in this
        presentation.
        """
        return self.__presentation.slides

    def save(self, file):
        """
        Save this presentation to *file*, where *file* can be either a path to
        a file (a string) or a file-like object.
        """
        return self.__package.save(file)
