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

"""Perform EDA calculations and output the results in plain text, NMD, and 
graphical formats.

Download example :download:`MDM2 trajectory files </doctest/mdm2.tar.gz>`."""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

import os.path

from ..apptools import *
from .nmaoptions import *
                       
def addCommand(commands):

    subparser = commands.add_parser('eda', 
        parents=[commands.choices.get('pca')], 
        help='perform essential dynamics analysis calculations', 
        add_help=False)

