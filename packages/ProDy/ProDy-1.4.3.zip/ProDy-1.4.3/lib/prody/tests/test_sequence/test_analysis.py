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

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

from unittest import TestCase

from numpy import array, log, zeros, char, ones
from numpy.testing import assert_array_equal, assert_array_almost_equal

from prody.tests.test_datafiles import *

from prody import LOGGER, calcShannonEntropy, buildMutinfoMatrix, parseMSA
from prody import calcMSAOccupancy, buildSeqidMatrix, uniqueSequences

LOGGER.verbosity = None

FASTA = parseMSA(pathDatafile('msa_Cys_knot.fasta'))
FASTA_ALPHA = char.isalpha(FASTA._msa)
FASTA_UPPER = char.upper(FASTA._msa)

FASTA_NUMBER, FASTA_LENGTH = FASTA_ALPHA.shape
FASTA_EYE = zeros((FASTA_NUMBER, FASTA_NUMBER))  
for i in range(FASTA_NUMBER):
    FASTA_EYE[i, i] = 1
    for j in range(i + 1, FASTA_NUMBER):
        score = 0.0
        ncols = 0
        for k in range(FASTA_LENGTH):
            if FASTA_ALPHA[i, k] or FASTA_ALPHA[j, k]:
                if FASTA_UPPER[i, k] == FASTA_UPPER[j, k]:
                    score += 1
                ncols += 1
        FASTA_EYE[i, j] = FASTA_EYE[j, i] = score / ncols


class TestCalcShannonEntropy(TestCase):


    def testSixSequences(self):
        
        msa = array([list('AAAAaaaaAAAAaaaa'), 
                     list('AAACaaacAAACaaac'),
                     list('AACDaacdAACDaacd'),
                     list('ACCEacceacceACCE'),
                     list('ACDFacdfacdfACDF'),
                     list('ACDGacdgacdgACDG')], dtype='|S1')

        expect = -log(1. / array([1, 2, 3, 6] * 4)) 
        result = calcShannonEntropy(msa)
        assert_array_almost_equal(expect, result)

    def testTwenty(self):
        
        msa = array([[char] for char in 'ACDEFGHIKLMNPQRSTVWY'], dtype='|S1')

        expect = -log(1. / 20)
        result = calcShannonEntropy(msa)
        assert_array_almost_equal(expect, result)

    
    def testSmallProbability(self):
        
        msa = zeros((1000000,1), '|S1')
        msa[0] = 'A'
        msa[1:] = 'C'
        expect = array([1., 999999.]) / 1000000
        expect = - (expect * log(expect)).sum() 
        result = calcShannonEntropy(msa)
        assert_array_almost_equal(expect, result)


    def testAmbiguous(self):
        
        msa = array([list('bjzxBJZX'),
                     list('bjzxBJZX'),], dtype='|S1')

        expect = -log(1. / array([2, 2, 2, 20] * 2)) 
        result = calcShannonEntropy(msa)
        assert_array_almost_equal(expect, result)

    def testGapDividend(self):
        
        msa = array([list('AAAA'), 
                     list('AAAC'),
                     list('AACD'),
                     list('ACCE'),
                     list('ACDF'),
                     list('ACDG'),
                     list('----')], dtype='|S1')

        expect = -log(1. / array([1, 2, 3, 6])) 
        result = calcShannonEntropy(msa, omitgaps=True)
        assert_array_almost_equal(expect, result)
        
"""
    def testSixSequences3(self):
        
        msa = array([list('AAAA'), 
                     list('AAAB'),
                     list('AABC'),
                     list('ABBD'),
                     list('ABCE'),
                     list('ABCF')])

        expect = -log(1. / array([1, 2, 3, 6])) 
        result = calcInfoEntropy(msa)
        assert_array_almost_equal(expect, result)
"""


class TestCalcMutualInfo(TestCase):
  

    def testSixSequences(self):
        
        msa = array([list('ACCA'), 
                     list('ACDA'),
                     list('ACEC'),
                     list('ACGC')], dtype='|S1')

        expect = array([[0., 0., 0., 0.],
                        [0., 0., 0., 0.],
                        [0., 0., 0., log(2.)],
                        [0., 0., log(2.), 0.],]) 
        result = buildMutinfoMatrix(msa)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')


    def testTwenty(self):
        
        seq = 'ACDEFGHIKLMNPQRSTVWY'
        msa = array([[s, s] for s in seq], dtype='|S1')

        expect = log(20.)
        expect = array([[0., expect],
                        [expect, 0.]])
        result = buildMutinfoMatrix(msa, debug=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')
    

    def testTwentyReversed(self):
        
        seq = 'ACDEFGHIKLMNPQRSTVWY'
        msa = array([[s, seq[-i-1]] for i, s in enumerate(seq)], dtype='|S1')

        expect = log(20.)
        expect = array([[0., expect],
                        [expect, 0.]])
        result = buildMutinfoMatrix(msa)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')


    def testAmbiguity(self):
        
        msa = array([list('OX'),
                     list('XO')], dtype='|S1')

        expect = array([[0., log(2.)],
                        [log(2.), 0.]]) 
        result = buildMutinfoMatrix(msa, debug=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')


    def testNoAmbiguity(self):
        
        msa = array([list('OX'),
                     list('XO')], dtype='|S1')

        expect = array([[0., log(2.)],
                        [log(2.), 0.]]) 
        result = buildMutinfoMatrix(msa, ambiquity=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, ambiquity=False, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')


    def testAmbiguity2(self):
        
        msa = array([list('AB'),
                     list('BZ')], dtype='|S1')
        expect = (2 * .25 * log(.25 / .5 / .25) + 
                  4 * .125 * log(.125 / .25 / .25))
        expect = array([[0., expect],
                        [expect, 0.]]) 
        result = buildMutinfoMatrix(msa, debug=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')
        

    def testAmbiguity3(self):
        
        msa = array([list('XX')], dtype='|S1')

        expect = zeros((2, 2)) 
        result = buildMutinfoMatrix(msa, debug=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')


    def testAmbiguity4(self):
        
        msa = array([list('Bb'),
                     list('jJ'),
                     list('Zz'),], dtype='|S1')

        expect = log((1./12) / (1./6) / (1./6))
        expect = array([[0., expect],
                        [expect, 0.]]) 
        result = buildMutinfoMatrix(msa, debug=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')


    def testAmbiguity5(self):

        expect = array([[0., 0.],
                        [0., 0.]]) 

        for seq in ['bx', 'Xb', 'jX', 'Xj', 'xz', 'ZX',
                    'bj', 'jb', 'bz', 'zb', 'jz', 'zj']:
            msa = array([list(seq)], dtype='|S1')
            result = buildMutinfoMatrix(msa, debug=False)
            assert_array_almost_equal(expect, result, err_msg=seq + ' failed')


    def testAmbiguity6(self):

        expect = zeros((2, 2)) 

        for seq in ['bb', 'jj', 'zz']:
            msa = array([list(seq)], dtype='|S1')
            result = buildMutinfoMatrix(msa, debug=False)
            assert_array_almost_equal(expect, result, err_msg=seq + ' failed')

    def testAmbiguity7(self):
        
        msa = array([list('bx'),
                     list('xb')], dtype='|S1')
        expect = (72 * 0.0125 * log(0.0125/0.0250/0.275) + 
                  4 * 0.0250 * log(0.0250/0.275/0.275))
        expect = array([[0., expect],
                        [expect, 0.]]) 
        result = buildMutinfoMatrix(msa, debug=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')

    def testInf(self):
        
        msa = zeros((500, 10), '|S1')
        msa.fill('.')
        msa[95,8] = 's'
        msa[95,9] = 'i'
        expect = zeros((10,10))
        expect[8,9] = expect[9,8] = 0.002 * log(500.) + 0.998 * log(1. / 0.998)
        result = buildMutinfoMatrix(msa, debug=False)
        assert_array_almost_equal(expect, result, err_msg='turbo failed')
        result = buildMutinfoMatrix(msa, turbo=False)
        assert_array_almost_equal(expect, result, err_msg='w/out turbo failed')

    def testNorm(self):
        
        seq = 'ACDEFGHIKLMNPQRSTVWY'
        msa = array([[s, seq[-i-1]] for i, s in enumerate(seq)], dtype='|S1')

        expect = 1. 
        expect = array([[0., expect],
                        [expect, 0.]])
        result = buildMutinfoMatrix(msa, norm=True)
        assert_array_almost_equal(expect, result, err_msg='norm failed')

    def testNorm2(self):
        
        seq = 'ACDEFGHIKLMNPQRSTVWY'
        msa = array([[s, 'O' if i % 2 else 'U'] for i, s in enumerate(seq)], 
                    dtype='|S1')
        
        expect = log(1./20. / (1./20. * 1./2.)) / (-log(1./20.)) 
        expect = array([[0., expect],
                        [expect, 0.]])
        result = buildMutinfoMatrix(msa, norm=True)
        assert_array_almost_equal(expect, result, err_msg='norm failed')


class TestCalcMSAOccupancy(TestCase):
    
    def testResidueCount(self):
        
        assert_array_equal(calcMSAOccupancy(FASTA, 'residue', count=1),
                           FASTA_ALPHA.sum(0))
    
    def testSequenceCount(self):
        
        assert_array_equal(calcMSAOccupancy(FASTA, 'sequence', count=1),
                           FASTA_ALPHA.sum(1))
        
    def testResidueOccupancy(self):
        
        assert_array_equal(calcMSAOccupancy(FASTA, 'residue'),
                           FASTA_ALPHA.sum(0) / (FASTA.numSequences() * 1.0))
    
    def testSequenceOccupancy(self):
        
        assert_array_equal(calcMSAOccupancy(FASTA, 'sequence'),
                           FASTA_ALPHA.sum(1) / (FASTA.numResidues() * 1.0))
        

class TestIdentity(TestCase):
    
    def testIdentityMatrix(self):

        assert_array_almost_equal(FASTA_EYE, buildSeqidMatrix(FASTA))

    def testIdentityMatrixNonTurbo(self):

        assert_array_almost_equal(FASTA_EYE, 
                                  buildSeqidMatrix(FASTA, turbo=False))


class TestUnique(TestCase):
    
    def testUnique(self):

        seqid = 0.98
        unique = ones(FASTA_NUMBER, bool)
        for i in range(FASTA_NUMBER):
            if not unique[i]:
                continue
            for j in range(i+1, FASTA_NUMBER):
                if FASTA_EYE[i, j] >= seqid:
                    unique[j] = False
                
        assert_array_equal(unique, uniqueSequences(FASTA, seqid))

    def testUnique2(self):

        seqid = 0.5
        unique = ones(FASTA_NUMBER, bool)
        for i in range(FASTA_NUMBER):
            if not unique[i]:
                continue
            for j in range(i+1, FASTA_NUMBER):
                if FASTA_EYE[i, j] >= seqid:
                    unique[j] = False
                
        assert_array_equal(unique, uniqueSequences(FASTA, seqid))
