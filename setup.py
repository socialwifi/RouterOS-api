#!/usr/bin/env python                                                                                                                                        
from setuptools import setup, find_packages

setup(version='0.11',
      name="RouterOS-api",
      description='Python API to RouterBoard devices produced by MikroTik.',
      author='Tomasz Wysocki',
      author_email='tomasz@pozytywnie.pl',
      packages=find_packages(),
      test_suite="tests",
      license="MIT",
)
