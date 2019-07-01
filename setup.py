#!/usr/bin/env python                                                                                                                                        
import sys

from setuptools import setup, find_packages

requirements = ['six']

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 3):
    requirements.append('ipaddress')

setup(version='0.14',
      name="RouterOS-api",
      description='Python API to RouterBoard devices produced by MikroTik.',
      author='Tomasz Wysocki',
      author_email='tomasz@pozytywnie.pl',
      packages=find_packages(),
      test_suite="tests",
      license="MIT",
      install_requires=requirements)
