#! /usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup
import multiprocessing

setup(name='TheLandlab',
      version='0.1.1',
      author='Eric Hutton',
      author_email='eric.hutton@colorado.edu',
      url='https://csdms.colorado.edu/trac/landlab',
      description='Python tools for Earth surface modeling.',
      long_description=open('README.rst').read(),
      #install_requires=['CmtBasicModelingInterface'],
      #setup_requires=['nose>=1.3'],
      setup_requires=['nose>=1.0'],
      packages=['landlab',
                'landlab.components',
                'landlab.grid',
                'landlab.field',
                'landlab.io',
                'landlab.tests',
                'landlab.utils',
                'landlab.examples',
                'landlab.framework',
               ],
      entry_points={
          'console_scripts': [
              'craters = landlab.components.craters:main',
              'landlab = landlab.cmd:main',
              'landlab_ex_1 = landlab.examples.diffusion2Dtest:main',
              'landlab_ex_2 = landlab.examples.diffusion2Dtest2:main',
              'landlab_ex_3 = landlab.examples.diffusion2Dtest3:main',
          ]
      },
      package_data={'': ['data/*asc']},
      test_suite='nose.collector',
      #test_suite='landlab.tests',
     )
