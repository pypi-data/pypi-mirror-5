#!/usr/bin/python
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

"""This module contains unit tests for :mod:`~prody.KDTree` module."""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

from numpy import tile, array, arange, ones
from numpy.testing import assert_allclose

from prody.tests import unittest
from prody.kdtree import KDTree
ATOL = 1e-5
RTOL = 0

class TestKDTree(unittest.TestCase):


    def setUp(self):

        self.coords = tile(arange(10), (3,1)).T.astype(float)
        self.kdtree = KDTree(self.coords)


    def testSearch(self):

        kdtree = self.kdtree
        coords = self.coords
        kdtree.search(10000, array([0,0,0]))
        indices = kdtree.getIndices()
        dist = (coords**2).sum(1)**0.5
        radii = kdtree.getDistances()
        assert_allclose(radii, dist[indices], rtol=RTOL, atol=ATOL,
                        err_msg='KDTree search failed')

    def testAllSearch(self):
        kdtree = self.kdtree
        coords = self.coords
        kdtree.search(1.75)
        radii = kdtree.getDistances()
        indices = kdtree.getIndices()
        self.assertEqual(len(indices), 9, 'KDTree all search failed')
        for pair, radius in zip(indices, radii):
            x, y = coords[pair]
            assert_allclose(((x - y)**2).sum()**0.5, radius,
                            rtol=RTOL, atol=ATOL,
                            err_msg='KDTree all search failed')


COORDS = array([[-1., -1., 0.],
                [-1.,  5., 0.],
                [ 2.,  2., 0.],
                [ 5., -1., 0.],
                [ 5.,  5., 0.],])
UNITCELL = array([4., 4., 0.])

KDTREE = KDTree(COORDS)
KDTREE_PBC = KDTree(COORDS, unitcell=UNITCELL)

class TestKDTreePBC(unittest.TestCase):

    def testPointNoPBC(self):

        KDTREE.search(2, ones(3) * 2)
        self.assertEqual(1, KDTREE.getCount())

    def testPairNoPBC(self):

        KDTREE.search(2)
        self.assertEqual(0, KDTREE.getCount())

    def testPointPBC(self):

        KDTREE_PBC.search(2, array([2., 2., 0.]))
        self.assertEqual(5, KDTREE_PBC.getCount())

    def testPairPBC(self):

        KDTREE_PBC.search(2)
        self.assertEqual(8, KDTREE_PBC.getCount())
