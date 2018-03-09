#!/usr/bin/env python

from distutils.core import setup
import os

SRC_PATH = os.path.relpath(os.path.dirname(__file__))

setup(name='gp_exts',
      description='Group Policy Client Side Extensions',
      package_dir={'': SRC_PATH},
      packages=['gp_exts', 'gp_exts.machine']
     )
