import os 
import sys
import platform
from os import sep as dirsep
from os.path import isfile, join

from distutils.core import setup
from distutils.extension import Extension
from distutils.command.install import install

if sys.version_info[:2] < (2, 6):
    sys.stderr.write('Python 2.5 and older is not supported\n')
    sys.exit()
    
if os.name == 'java': 
    sys.stderr.write('JavaOS is not supported\n')
    sys.exit()

try:    
    import numpy
except ImportError:
    sys.stderr.write('numpy is not installed, you can find it at: '
                     'http://numpy.scipy.org\n')
    sys.exit()

if [int(dgt) for dgt in numpy.__version__.split('.')[:2]] < [1, 4]: 
    sys.stderr.write('numpy v1.4 or later is required, you can find it at: '
                     'http://numpy.scipy.org\n')
    sys.exit()


__version__ = ''
inp = open('lib/prody/__init__.py')
for line in inp:
    if (line.startswith('__version__')):
        exec(line.strip())
        break
inp.close()

with open('README.rst') as inp:
    long_description = inp.read()


PACKAGES = ['prody', 
            'prody.atomic', 
            'prody.database', 
            'prody.dynamics', 
            'prody.ensemble', 
            'prody.kdtree', 
            'prody.measure', 
            'prody.proteins', 
            'prody.sequence', 
            'prody.trajectory', 
            'prody.utilities', 
            'prody.apps', 
            'prody.apps.prody_apps',
            'prody.apps.evol_apps',
            'prody.tests',
            'prody.tests.test_apps',
            'prody.tests.test_atomic',
            'prody.tests.test_datafiles',
            'prody.tests.test_dynamics',
            'prody.tests.test_ensemble', 
            'prody.tests.test_kdtree', 
            'prody.tests.test_measure',
            'prody.tests.test_proteins',
            'prody.tests.test_sequence',
            'prody.tests.test_trajectory',
            'prody.tests.test_utilities',]
PACKAGE_DATA = {
    'prody.tests': ['test_datafiles/pdb*.pdb', 
                    'test_datafiles/*.dat', 
                    'test_datafiles/*.coo', 
                    'test_datafiles/dcd*.dcd',
                    'test_datafiles/xml*.xml',
                    'test_datafiles/msa*',]
}

PACKAGE_DIR = {}
for pkg in PACKAGES:
    PACKAGE_DIR[pkg] = join('lib', *pkg.split('.'))

EXTENSIONS = [
    Extension('prody.proteins.cpairwise2', 
              [join('lib', 'prody', 'proteins', 'cpairwise2.c')]),
    Extension('prody.kdtree._CKDTree',
              [join('lib', 'prody', 'kdtree', 'KDTree.c'),
               join('lib', 'prody', 'kdtree', 'KDTreemodule.c')],
              include_dirs=[numpy.get_include()]),
    Extension('prody.sequence.msatools',
              [join('lib', 'prody', 'sequence', 'msatools.c'),],
              include_dirs=[numpy.get_include()]),
    Extension('prody.sequence.msaio',
              [join('lib', 'prody', 'sequence', 'msaio.c'),],
              include_dirs=[numpy.get_include()]),
    Extension('prody.sequence.seqtools',
              [join('lib', 'prody', 'sequence', 'seqtools.c'),],
              include_dirs=[numpy.get_include()]),
]

SCRIPTS = ['scripts/prody', 'scripts/evol']
if (platform.system() == 'Windows' or 
    len(sys.argv) > 1 and sys.argv[1] not in ('build', 'install')):
    for script in list(SCRIPTS):
        SCRIPTS.append(script + '.bat')

setup(
    name='ProDy',
    version=__version__,
    author='Ahmet Bakan',
    author_email='ahb12@pitt.edu',
    description='A Python Package for Protein Dynamics Analysis',
    long_description=long_description,
    url='http://www.csb.pitt.edu/ProDy',
    packages=PACKAGES,
    package_dir=PACKAGE_DIR,
    package_data=PACKAGE_DATA,
    ext_modules=EXTENSIONS,
    license='GPLv3',
    keywords=('protein, dynamics, elastic network model, '
              'Gaussian network model, anisotropic network model, '
              'essential dynamics analysis, principal component analysis, '
              'Protein Data Bank, PDB, GNM, ANM, PCA'),
    classifiers=[
                 'Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Operating System :: MacOS',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Topic :: Scientific/Engineering :: Bio-Informatics',
                 'Topic :: Scientific/Engineering :: Chemistry',
                ],
    scripts=SCRIPTS,
    requires=['NumPy (>=1.5)', ],
    provides=['ProDy ({0:s})'.format(__version__)]
)
