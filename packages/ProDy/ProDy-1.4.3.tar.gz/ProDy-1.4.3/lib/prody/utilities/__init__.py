# -*- coding: utf-8 -*-
# ProDy: A Python Package for Protein Dynamics Analysis
#
# Copyright (C) 2010-2012 Ahmet Bakan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""This module provides utility functions and classes for handling files,
logging, type checking, etc.  Contents of this module are not included in
ProDy namespace, as it is not safe to import them all due to name conflicts.
Required or classes should be imported explicitly, e.g.
``from prody.utilities import PackageLogger, openFile``.


Package utilities
===============================================================================

  * :class:`.PackageLogger`
  * :class:`.PackageSettings`
  * :func:`.getPackagePath`
  * :func:`.setPackagePath`

Type/Value checkers
===============================================================================

  * :func:`.checkCoords`
  * :func:`.checkWeights`
  * :func:`.checkTypes`

Path/file handling
===============================================================================

  * :func:`.gunzip`
  * :func:`.openFile`
  * :func:`.openDB`
  * :func:`.openSQLite`
  * :func:`.openURL`
  * :func:`.copyFile`
  * :func:`.isExecutable`
  * :func:`.isReadable`
  * :func:`.isWritable`
  * :func:`.makePath`
  * :func:`.relpath`
  * :func:`.which`
  * :func:`.pickle`
  * :func:`.unpickle`
  * :func:`.glob`


Documentation tools
===============================================================================

  * :func:`.joinRepr`
  * :func:`.joinRepr`
  * :func:`.joinTerms`
  * :func:`.tabulate`
  * :func:`.wrapText`


Miscellaneous tools
===============================================================================

  * :func:`.rangeString`
  * :func:`.alnum`
  * :func:`.importLA`
  * :func:`.dictElement`

"""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'


__all__ = []

from .checkers import *
from .logger import *
from .settings import *
from .pathtools import *
from .misctools import *
from .doctools import *
